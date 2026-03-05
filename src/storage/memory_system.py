# -*- coding: utf-8 -*-
"""
Memory System for Math Mentor AI
Persistent storage and learning capabilities using SQLite
"""

import sqlite3
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import uuid
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class InteractionRecord:
    """Data structure for storing user interactions"""
    id: str
    session_id: str
    input_type: str  # text, image, audio
    original_input: str
    processed_input: str
    problem_topic: str
    agent_trace: List[Dict]
    solution: str
    confidence_scores: Dict[str, float]
    user_feedback: Optional[Dict] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class FeedbackRecord:
    """Data structure for HITL feedback"""
    id: str
    interaction_id: str
    feedback_type: str  # approved, corrected, rejected
    original_text: str
    corrected_text: Optional[str]
    quality_rating: Optional[int]
    comments: Optional[str]
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class LearningPattern:
    """Data structure for learning patterns"""
    id: str
    pattern_type: str  # ocr_correction, solution_strategy, common_mistake
    pattern_data: Dict[str, Any]
    frequency: int
    success_rate: float
    last_used: datetime = None
    
    def __post_init__(self):
        if self.last_used is None:
            self.last_used = datetime.now()

class MathMentorMemorySystem:
    """Persistent memory and learning system"""
    
    def __init__(self, db_path: str = "data/mathmentor_memory.db"):
        """Initialize memory system with SQLite database"""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self.setup_database()
        logger.info(f"Memory system initialized with database: {self.db_path}")
    
    def setup_database(self):
        """Create database tables if they don't exist"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Interactions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS interactions (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    input_type TEXT NOT NULL,
                    original_input TEXT NOT NULL,
                    processed_input TEXT NOT NULL,
                    problem_topic TEXT,
                    agent_trace TEXT,  -- JSON string
                    solution TEXT,
                    confidence_scores TEXT,  -- JSON string
                    user_feedback TEXT,  -- JSON string
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Feedback table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS feedback (
                    id TEXT PRIMARY KEY,
                    interaction_id TEXT NOT NULL,
                    feedback_type TEXT NOT NULL,
                    original_text TEXT NOT NULL,
                    corrected_text TEXT,
                    quality_rating INTEGER,
                    comments TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (interaction_id) REFERENCES interactions (id)
                )
            ''')
            
            # Learning patterns table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS learning_patterns (
                    id TEXT PRIMARY KEY,
                    pattern_type TEXT NOT NULL,
                    pattern_data TEXT NOT NULL,  -- JSON string
                    frequency INTEGER DEFAULT 1,
                    success_rate REAL DEFAULT 1.0,
                    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Performance metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id TEXT PRIMARY KEY,
                    metric_type TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    metric_data TEXT,  -- JSON string for additional data
                    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            logger.info("Database schema created/verified successfully")
    
    # Interaction Management
    def store_interaction(self, interaction: InteractionRecord) -> bool:
        """Store a new interaction record"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO interactions (
                        id, session_id, input_type, original_input, processed_input,
                        problem_topic, agent_trace, solution, confidence_scores, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    interaction.id,
                    interaction.session_id,
                    interaction.input_type,
                    interaction.original_input,
                    interaction.processed_input,
                    interaction.problem_topic,
                    json.dumps(interaction.agent_trace),
                    interaction.solution,
                    json.dumps(interaction.confidence_scores),
                    interaction.created_at
                ))
                conn.commit()
                logger.info(f"Stored interaction: {interaction.id}")
                return True
        except Exception as e:
            logger.error(f"Failed to store interaction: {str(e)}")
            return False
    
    def get_interaction(self, interaction_id: str) -> Optional[InteractionRecord]:
        """Retrieve a specific interaction"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM interactions WHERE id = ?', (interaction_id,))
                row = cursor.fetchone()
                
                if row:
                    return InteractionRecord(
                        id=row[0],
                        session_id=row[1],
                        input_type=row[2],
                        original_input=row[3],
                        processed_input=row[4],
                        problem_topic=row[5],
                        agent_trace=json.loads(row[6] or "[]"),
                        solution=row[7],
                        confidence_scores=json.loads(row[8] or "{}"),
                        user_feedback=json.loads(row[9] or "null"),
                        created_at=datetime.fromisoformat(row[10])
                    )
        except Exception as e:
            logger.error(f"Failed to retrieve interaction: {str(e)}")
        return None
    
    # Feedback Management
    def store_feedback(self, feedback: FeedbackRecord) -> bool:
        """Store user feedback"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO feedback (
                        id, interaction_id, feedback_type, original_text,
                        corrected_text, quality_rating, comments, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    feedback.id,
                    feedback.interaction_id,
                    feedback.feedback_type,
                    feedback.original_text,
                    feedback.corrected_text,
                    feedback.quality_rating,
                    feedback.comments,
                    feedback.created_at
                ))
                conn.commit()
                
                # Update interaction with feedback
                self.update_interaction_feedback(feedback.interaction_id, asdict(feedback))
                logger.info(f"Stored feedback: {feedback.id}")
                return True
        except Exception as e:
            logger.error(f"Failed to store feedback: {str(e)}")
            return False
    
    def update_interaction_feedback(self, interaction_id: str, feedback_data: Dict) -> bool:
        """Update interaction record with feedback data"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE interactions 
                    SET user_feedback = ?
                    WHERE id = ?
                ''', (json.dumps(feedback_data), interaction_id))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Failed to update interaction feedback: {str(e)}")
            return False
    
    # Learning Pattern Management
    def store_learning_pattern(self, pattern: LearningPattern) -> bool:
        """Store or update a learning pattern"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if pattern exists
                cursor.execute('''
                    SELECT frequency, success_rate FROM learning_patterns 
                    WHERE pattern_type = ? AND pattern_data = ?
                ''', (pattern.pattern_type, json.dumps(pattern.pattern_data)))
                
                existing = cursor.fetchone()
                
                if existing:
                    # Update existing pattern
                    new_frequency = existing[0] + 1
                    # Update success rate (simple average for now)
                    new_success_rate = (existing[1] * existing[0] + pattern.success_rate) / new_frequency
                    
                    cursor.execute('''
                        UPDATE learning_patterns 
                        SET frequency = ?, success_rate = ?, last_used = ?
                        WHERE pattern_type = ? AND pattern_data = ?
                    ''', (new_frequency, new_success_rate, pattern.last_used,
                          pattern.pattern_type, json.dumps(pattern.pattern_data)))
                else:
                    # Insert new pattern
                    cursor.execute('''
                        INSERT INTO learning_patterns (
                            id, pattern_type, pattern_data, frequency, success_rate, last_used
                        ) VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        pattern.id,
                        pattern.pattern_type,
                        json.dumps(pattern.pattern_data),
                        pattern.frequency,
                        pattern.success_rate,
                        pattern.last_used
                    ))
                
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Failed to store learning pattern: {str(e)}")
            return False
    
    # Retrieval and Search
    def find_similar_problems(self, problem_text: str, topic: str = None, limit: int = 5) -> List[InteractionRecord]:
        """Find similar previously solved problems"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if topic:
                    cursor.execute('''
                        SELECT * FROM interactions 
                        WHERE problem_topic = ?
                        ORDER BY created_at DESC
                        LIMIT ?
                    ''', (topic, limit))
                else:
                    cursor.execute('''
                        SELECT * FROM interactions 
                        ORDER BY created_at DESC
                        LIMIT ?
                    ''', (limit,))
                
                rows = cursor.fetchall()
                results = []
                
                for row in rows:
                    results.append(InteractionRecord(
                        id=row[0],
                        session_id=row[1],
                        input_type=row[2],
                        original_input=row[3],
                        processed_input=row[4],
                        problem_topic=row[5],
                        agent_trace=json.loads(row[6] or "[]"),
                        solution=row[7],
                        confidence_scores=json.loads(row[8] or "{}"),
                        user_feedback=json.loads(row[9] or "null"),
                        created_at=datetime.fromisoformat(row[10])
                    ))
                
                return results
        except Exception as e:
            logger.error(f"Failed to find similar problems: {str(e)}")
            return []
    
    def get_learning_patterns(self, pattern_type: str = None) -> List[LearningPattern]:
        """Retrieve learning patterns"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if pattern_type:
                    cursor.execute('''
                        SELECT * FROM learning_patterns 
                        WHERE pattern_type = ?
                        ORDER BY frequency DESC, success_rate DESC
                    ''', (pattern_type,))
                else:
                    cursor.execute('''
                        SELECT * FROM learning_patterns 
                        ORDER BY frequency DESC, success_rate DESC
                    ''')
                
                patterns = []
                for row in cursor.fetchall():
                    patterns.append(LearningPattern(
                        id=row[0],
                        pattern_type=row[1],
                        pattern_data=json.loads(row[2]),
                        frequency=row[3],
                        success_rate=row[4],
                        last_used=datetime.fromisoformat(row[5])
                    ))
                
                return patterns
        except Exception as e:
            logger.error(f"Failed to retrieve learning patterns: {str(e)}")
            return []
    
    # Analytics and Metrics
    def get_feedback_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get feedback analytics for the last N days"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT feedback_type, COUNT(*), AVG(quality_rating)
                    FROM feedback 
                    WHERE created_at >= datetime('now', '-{} days')
                    GROUP BY feedback_type
                '''.format(days))
                
                analytics = {
                    'feedback_distribution': {},
                    'average_ratings': {},
                    'total_feedback': 0
                }
                
                for row in cursor.fetchall():
                    feedback_type, count, avg_rating = row
                    analytics['feedback_distribution'][feedback_type] = count
                    analytics['average_ratings'][feedback_type] = avg_rating or 0
                    analytics['total_feedback'] += count
                
                return analytics
        except Exception as e:
            logger.error(f"Failed to get feedback analytics: {str(e)}")
            return {}
    
    def get_performance_metrics(self, days: int = 30) -> Dict[str, Any]:
        """Get system performance metrics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get interaction counts by type
                cursor.execute('''
                    SELECT input_type, COUNT(*)
                    FROM interactions 
                    WHERE created_at >= datetime('now', '-{} days')
                    GROUP BY input_type
                '''.format(days))
                
                metrics = {
                    'input_type_distribution': dict(cursor.fetchall()),
                    'total_interactions': 0
                }
                
                # Get total interactions
                cursor.execute('''
                    SELECT COUNT(*)
                    FROM interactions 
                    WHERE created_at >= datetime('now', '-{} days')
                '''.format(days))
                
                metrics['total_interactions'] = cursor.fetchone()[0]
                
                return metrics
        except Exception as e:
            logger.error(f"Failed to get performance metrics: {str(e)}")
            return {}
    
    # Utility methods
    def clear_old_data(self, days: int = 90):
        """Clear data older than specified days"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    DELETE FROM interactions 
                    WHERE created_at < datetime('now', '-{} days')
                '''.format(days))
                
                cursor.execute('''
                    DELETE FROM feedback 
                    WHERE created_at < datetime('now', '-{} days')
                '''.format(days))
                
                conn.commit()
                logger.info(f"Cleared data older than {days} days")
        except Exception as e:
            logger.error(f"Failed to clear old data: {str(e)}")
    
    def export_data(self, output_path: str) -> bool:
        """Export all data to JSON file"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Export all tables
                export_data = {
                    'interactions': [],
                    'feedback': [],
                    'learning_patterns': []
                }
                
                # Interactions
                cursor.execute('SELECT * FROM interactions')
                for row in cursor.fetchall():
                    export_data['interactions'].append({
                        'id': row[0],
                        'session_id': row[1],
                        'input_type': row[2],
                        'original_input': row[3],
                        'processed_input': row[4],
                        'problem_topic': row[5],
                        'agent_trace': json.loads(row[6] or "[]"),
                        'solution': row[7],
                        'confidence_scores': json.loads(row[8] or "{}"),
                        'user_feedback': json.loads(row[9] or "null"),
                        'created_at': row[10]
                    })
                
                # Feedback
                cursor.execute('SELECT * FROM feedback')
                for row in cursor.fetchall():
                    export_data['feedback'].append({
                        'id': row[0],
                        'interaction_id': row[1],
                        'feedback_type': row[2],
                        'original_text': row[3],
                        'corrected_text': row[4],
                        'quality_rating': row[5],
                        'comments': row[6],
                        'created_at': row[7]
                    })
                
                # Learning patterns
                cursor.execute('SELECT * FROM learning_patterns')
                for row in cursor.fetchall():
                    export_data['learning_patterns'].append({
                        'id': row[0],
                        'pattern_type': row[1],
                        'pattern_data': json.loads(row[2]),
                        'frequency': row[3],
                        'success_rate': row[4],
                        'last_used': row[5]
                    })
                
                # Write to file
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, default=str)
                
                logger.info(f"Data exported to {output_path}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to export data: {str(e)}")
            return False

# Singleton instance
_memory_system = None

def get_memory_system() -> MathMentorMemorySystem:
    """Get the singleton memory system instance"""
    global _memory_system
    if _memory_system is None:
        _memory_system = MathMentorMemorySystem()
    return _memory_system