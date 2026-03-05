# -*- coding: utf-8 -*-
"""
Knowledge Base RAG System for Math Mentor AI
Implements vector database with ChromaDB for retrieving relevant math knowledge
"""

import logging
import os
from typing import List, Dict, Any, Optional
from pathlib import Path
import hashlib

logger = logging.getLogger(__name__)

class MathKnowledgeRAG:
    """RAG system for mathematical knowledge retrieval"""
    
    def __init__(self, knowledge_base_path: str = "knowledge_base", 
                 persist_directory: str = "data/chroma_db"):
        """
        Initialize the RAG system
        
        Args:
            knowledge_base_path: Path to knowledge base documents
            persist_directory: Directory for ChromaDB persistence
        """
        self.knowledge_base_path = Path(knowledge_base_path)
        self.persist_directory = Path(persist_directory)
        self.logger = logging.getLogger(__name__)
        
        # Try to import ChromaDB
        try:
            import chromadb
            from chromadb.config import Settings
            self.chromadb_available = True
            self.chromadb = chromadb
            self.Settings = Settings
            self.logger.info("ChromaDB available")
        except ImportError:
            self.chromadb_available = False
            self.chromadb = None
            self.Settings = None
            self.logger.warning("ChromaDB not available - RAG will be limited")
        
        # Try to import embedding models
        try:
            from sentence_transformers import SentenceTransformer
            self.embeddings_available = True
            self.SentenceTransformer = SentenceTransformer
            self.logger.info("Sentence Transformers available")
        except ImportError:
            self.embeddings_available = False
            self.SentenceTransformer = None
            self.logger.warning("Sentence Transformers not available")
        
        # Initialize collection and embeddings
        self.collection = None
        self.embedding_model = None
        self._setup_vector_database()
    
    def _setup_vector_database(self):
        """Setup ChromaDB vector database"""
        if not self.chromadb_available:
            self.logger.warning("ChromaDB not available - using in-memory fallback")
            self._init_fallback_storage()
            return
        
        try:
            # Create persist directory if needed
            self.persist_directory.mkdir(parents=True, exist_ok=True)
            
            # Initialize ChromaDB client
            self.client = self.chromadb.PersistentClient(
                path=str(self.persist_directory)
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name="math_knowledge",
                metadata={"description": "Mathematical knowledge base for JEE-level problems"}
            )
            
            # Load embedding model if available
            if self.embeddings_available:
                self.embedding_model = self.SentenceTransformer('all-MiniLM-L6-v2')
                self.logger.info("Loaded embedding model: all-MiniLM-L6-v2")
            
            # Load documents from knowledge base
            self._load_knowledge_base()
            
            self.logger.info(f"Vector database initialized with {self.collection.count()} documents")
            
        except Exception as e:
            self.logger.error(f"Failed to setup vector database: {e}")
            self._init_fallback_storage()
    
    def _init_fallback_storage(self):
        """Initialize fallback in-memory storage when ChromaDB not available"""
        self.fallback_documents = []
        self.logger.info("Using fallback in-memory storage")
        # Still load knowledge base documents into fallback storage
        self._load_knowledge_base()
    
    def _load_knowledge_base(self):
        """Load documents from knowledge base directory"""
        if not self.knowledge_base_path.exists():
            self.logger.warning(f"Knowledge base path does not exist: {self.knowledge_base_path}")
            return
        
        # Find all markdown and text files
        documents_loaded = 0
        
        for file_path in self.knowledge_base_path.rglob("*.md"):
            try:
                self.add_document_from_file(file_path)
                documents_loaded += 1
            except Exception as e:
                self.logger.error(f"Failed to load {file_path}: {e}")
        
        for file_path in self.knowledge_base_path.rglob("*.txt"):
            try:
                self.add_document_from_file(file_path)
                documents_loaded += 1
            except Exception as e:
                self.logger.error(f"Failed to load {file_path}: {e}")
        
        self.logger.info(f"Loaded {documents_loaded} documents from knowledge base")
    
    def add_document_from_file(self, file_path: Path):
        """
        Add a document from a file
        
        Args:
            file_path: Path to the document file
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract metadata from file
        metadata = {
            "source": str(file_path),
            "filename": file_path.name,
            "type": "knowledge_base_document"
        }
        
        # Try to extract title from markdown
        if file_path.suffix == '.md':
            lines = content.split('\n')
            for line in lines:
                if line.startswith('# '):
                    metadata["title"] = line[2:].strip()
                    break
        
        self.add_document(content, metadata)
    
    def add_document(self, content: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Add a document to the knowledge base
        
        Args:
            content: Document content
            metadata: Document metadata
        """
        if not content or not content.strip():
            return
        
        metadata = metadata or {}
        
        # Generate document ID
        doc_id = self._generate_doc_id(content)
        
        if self.collection:
            try:
                # Generate embedding if model available
                if self.embedding_model:
                    embedding = self.embedding_model.encode(content).tolist()
                    
                    self.collection.add(
                        ids=[doc_id],
                        documents=[content],
                        metadatas=[metadata],
                        embeddings=[embedding]
                    )
                else:
                    # Let ChromaDB generate embeddings
                    self.collection.add(
                        ids=[doc_id],
                        documents=[content],
                        metadatas=[metadata]
                    )
                
                self.logger.debug(f"Added document {doc_id}")
                
            except Exception as e:
                self.logger.error(f"Failed to add document: {e}")
        else:
            # Fallback storage
            self.fallback_documents.append({
                "id": doc_id,
                "content": content,
                "metadata": metadata
            })
    
    def retrieve_relevant_knowledge(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve relevant knowledge for a query
        
        Args:
            query: Query text
            top_k: Number of results to return
            
        Returns:
            List of relevant documents with metadata
        """
        if not query or not query.strip():
            return []
        
        if self.collection:
            try:
                # Generate query embedding if model available
                if self.embedding_model:
                    query_embedding = self.embedding_model.encode(query).tolist()
                    
                    results = self.collection.query(
                        query_embeddings=[query_embedding],
                        n_results=min(top_k, self.collection.count())
                    )
                else:
                    # Let ChromaDB handle embedding
                    results = self.collection.query(
                        query_texts=[query],
                        n_results=min(top_k, self.collection.count())
                    )
                
                # Format results
                documents = []
                if results and results['documents']:
                    for i, doc in enumerate(results['documents'][0]):
                        # Calculate relevance score safely (avoid negative scores)
                        distance = results['distances'][0][i] if results.get('distances') else 0.5
                        # Use 1/(1+distance) formula for stable 0-1 range scores
                        relevance_score = 1.0 / (1.0 + distance)
                        
                        documents.append({
                            "content": doc,
                            "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                            "distance": distance,
                            "relevance_score": relevance_score
                        })
                
                return documents
                
            except Exception as e:
                self.logger.error(f"Failed to retrieve knowledge: {e}")
                return self._fallback_retrieval(query, top_k)
        else:
            return self._fallback_retrieval(query, top_k)
    
    def _fallback_retrieval(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Simple keyword-based retrieval when vector DB not available"""
        if not hasattr(self, 'fallback_documents'):
            return []
        
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        # Score documents by keyword overlap
        scored_docs = []
        for doc in self.fallback_documents:
            content_lower = doc['content'].lower()
            content_words = set(content_lower.split())
            
            # Calculate overlap score
            overlap = len(query_words.intersection(content_words))
            score = overlap / max(len(query_words), 1)
            
            if overlap > 0:
                scored_docs.append({
                    "content": doc['content'],
                    "metadata": doc['metadata'],
                    "relevance_score": score
                })
        
        # Sort by score and return top k
        scored_docs.sort(key=lambda x: x['relevance_score'], reverse=True)
        return scored_docs[:top_k]
    
    def get_knowledge_for_problem_type(self, problem_type: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Get knowledge relevant to a specific problem type
        
        Args:
            problem_type: Type of problem (algebra, calculus, etc.)
            top_k: Number of results
            
        Returns:
            Relevant knowledge documents
        """
        # Map problem types to search queries
        query_map = {
            "algebra": "algebraic equations linear quadratic polynomial factoring",
            "calculus": "derivatives integrals limits differentiation integration",
            "probability": "probability statistics combinations permutations",
            "geometry": "geometric geometry shapes angles triangles circles",
            "trigonometry": "trigonometric functions sine cosine tangent",
            "number_theory": "number theory primes divisibility modular",
            "coordinate_geometry": "coordinate geometry lines curves parabola"
        }
        
        query = query_map.get(problem_type, problem_type)
        return self.retrieve_relevant_knowledge(query, top_k)
    
    def get_knowledge_statistics(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base"""
        stats = {
            "total_documents": 0,
            "storage_type": "chromadb" if self.collection else "fallback",
            "embeddings_available": self.embeddings_available
        }
        
        if self.collection:
            try:
                stats["total_documents"] = self.collection.count()
            except:
                pass
        elif hasattr(self, 'fallback_documents'):
            stats["total_documents"] = len(self.fallback_documents)
        
        return stats
    
    def search_by_topic(self, topic: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search knowledge base by topic
        
        Args:
            topic: Topic to search for
            top_k: Number of results
            
        Returns:
            Relevant documents
        """
        return self.retrieve_relevant_knowledge(topic, top_k)
    
    def get_formulas_for_topic(self, topic: str) -> List[str]:
        """
        Extract formulas related to a topic
        
        Args:
            topic: Topic to search
            
        Returns:
            List of formulas
        """
        results = self.retrieve_relevant_knowledge(topic, top_k=3)
        
        formulas = []
        for result in results:
            content = result.get("content", "")
            
            # Extract lines that look like formulas
            lines = content.split('\n')
            for line in lines:
                # Check if line contains mathematical symbols
                if any(symbol in line for symbol in ['=', '+', '-', '*', '/', '^', '∫', '∑', '√']):
                    # Skip markdown headers and explanatory text
                    if not line.strip().startswith('#') and len(line.strip()) < 100:
                        formulas.append(line.strip())
        
        return formulas[:10]  # Limit to 10 formulas
    
    def add_problem_solution_to_kb(self, problem: str, solution: str, 
                                   metadata: Optional[Dict[str, Any]] = None):
        """
        Add a solved problem to the knowledge base for future reference
        
        Args:
            problem: Problem statement
            solution: Solution steps
            metadata: Additional metadata
        """
        metadata = metadata or {}
        metadata["type"] = "solved_problem"
        
        content = f"Problem: {problem}\n\nSolution: {solution}"
        self.add_document(content, metadata)
    
    def clear_database(self):
        """Clear all documents from the database (use with caution)"""
        if self.collection:
            try:
                self.client.delete_collection("math_knowledge")
                self.collection = self.client.create_collection(
                    name="math_knowledge",
                    metadata={"description": "Mathematical knowledge base for JEE-level problems"}
                )
                self.logger.info("Database cleared")
            except Exception as e:
                self.logger.error(f"Failed to clear database: {e}")
        elif hasattr(self, 'fallback_documents'):
            self.fallback_documents = []
    
    def _generate_doc_id(self, content: str) -> str:
        """Generate unique document ID from content"""
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def batch_add_documents(self, documents: List[Dict[str, Any]]):
        """
        Add multiple documents in batch
        
        Args:
            documents: List of dicts with 'content' and optional 'metadata'
        """
        for doc in documents:
            content = doc.get("content")
            metadata = doc.get("metadata", {})
            if content:
                self.add_document(content, metadata)
        
        self.logger.info(f"Batch added {len(documents)} documents")


# Convenience function for initializing RAG system
def initialize_rag_system(knowledge_base_path: str = "knowledge_base",
                         persist_directory: str = "data/chroma_db") -> MathKnowledgeRAG:
    """
    Initialize and return RAG system
    
    Args:
        knowledge_base_path: Path to knowledge base documents
        persist_directory: ChromaDB persistence directory
        
    Returns:
        Initialized MathKnowledgeRAG instance
    """
    return MathKnowledgeRAG(knowledge_base_path, persist_directory)
