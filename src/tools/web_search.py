# -*- coding: utf-8 -*-
"""
Web Search Tool for Math Mentor AI
Implements web search with citations using DuckDuckGo and Google Search API
"""

import logging
from typing import Dict, Any, List, Optional
import re
from datetime import datetime

# Try DuckDuckGo Search
try:
    from duckduckgo_search import DDGS
    DDGS_AVAILABLE = True
except ImportError:
    DDGS_AVAILABLE = False
    logging.warning("DuckDuckGo search not available")

# Try Google Search API
try:
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GOOGLE_API_AVAILABLE = True
except ImportError:
    GOOGLE_API_AVAILABLE = False
    logging.warning("Google API client not available")

from ..config import config

logger = logging.getLogger(__name__)

class WebSearchTool:
    """Web search tool with citation management"""
    
    def __init__(self):
        """Initialize web search tool"""
        self.ddgs_available = DDGS_AVAILABLE
        self.google_available = GOOGLE_API_AVAILABLE and config.GOOGLE_SEARCH_API_KEY
        
        # Search configuration
        self.max_results = 5
        self.search_timeout = 10
        
        # Citation tracking
        self.citations = []
        
        logger.info(f"Web Search initialized - DuckDuckGo: {self.ddgs_available}, Google: {self.google_available}")
    
    def search(self, query: str, 
              search_type: str = "text",
              max_results: int = None,
              region: str = "us-en") -> Dict[str, Any]:
        """
        Perform web search with multiple fallback options
        
        Args:
            query: Search query
            search_type: Type of search ('text', 'math', 'definition')
            max_results: Maximum number of results
            region: Search region
            
        Returns:
            Search results with citations
        """
        max_results = max_results or self.max_results
        
        logger.info(f"Performing web search for: {query}")
        
        # Enhance query for mathematical content
        if search_type == "math":
            query = self._enhance_math_query(query)
        
        # Try DuckDuckGo first (free, no API key required)
        if self.ddgs_available:
            try:
                results = self._search_duckduckgo(query, max_results, region)
                if results["success"]:
                    return results
            except Exception as e:
                logger.warning(f"DuckDuckGo search failed: {e}")
        
        # Fallback to Google Custom Search API
        if self.google_available:
            try:
                results = self._search_google(query, max_results)
                if results["success"]:
                    return results
            except Exception as e:
                logger.warning(f"Google search failed: {e}")
        
        # No search available
        return {
            "success": False,
            "error": "No search engines available",
            "query": query,
            "results": []
        }
    
    def _search_duckduckgo(self, query: str, max_results: int, region: str) -> Dict[str, Any]:
        """Search using DuckDuckGo"""
        try:
            with DDGS() as ddgs:
                # Text search
                raw_results = list(ddgs.text(
                    query,
                    region=region,
                    safesearch='moderate',
                    max_results=max_results
                ))
                
                # Process results
                processed_results = []
                for i, result in enumerate(raw_results, 1):
                    processed_result = {
                        "rank": i,
                        "title": result.get("title", ""),
                        "url": result.get("href", ""),
                        "snippet": result.get("body", ""),
                        "source": "DuckDuckGo",
                        "citation_id": self._generate_citation_id()
                    }
                    processed_results.append(processed_result)
                    
                    # Add to citations
                    self._add_citation(processed_result)
                
                return {
                    "success": True,
                    "query": query,
                    "results": processed_results,
                    "count": len(processed_results),
                    "search_engine": "DuckDuckGo",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"DuckDuckGo search error: {e}")
            return {
                "success": False,
                "error": str(e),
                "query": query,
                "results": []
            }
    
    def _search_google(self, query: str, max_results: int) -> Dict[str, Any]:
        """Search using Google Custom Search API"""
        try:
            service = build("customsearch", "v1", developerKey=config.GOOGLE_SEARCH_API_KEY)
            
            # Perform search
            result = service.cse().list(
                q=query,
                cx=config.GOOGLE_SEARCH_CX,
                num=max_results
            ).execute()
            
            # Process results
            processed_results = []
            for i, item in enumerate(result.get("items", []), 1):
                processed_result = {
                    "rank": i,
                    "title": item.get("title", ""),
                    "url": item.get("link", ""),
                    "snippet": item.get("snippet", ""),
                    "source": "Google",
                    "citation_id": self._generate_citation_id()
                }
                processed_results.append(processed_result)
                
                # Add to citations
                self._add_citation(processed_result)
            
            return {
                "success": True,
                "query": query,
                "results": processed_results,
                "count": len(processed_results),
                "search_engine": "Google",
                "timestamp": datetime.now().isoformat()
            }
            
        except HttpError as e:
            logger.error(f"Google search HTTP error: {e}")
            return {
                "success": False,
                "error": f"Google API error: {str(e)}",
                "query": query,
                "results": []
            }
        except Exception as e:
            logger.error(f"Google search error: {e}")
            return {
                "success": False,
                "error": str(e),
                "query": query,
                "results": []
            }
    
    def _enhance_math_query(self, query: str) -> str:
        """Enhance query for better mathematical content results"""
        # Add mathematical context keywords
        math_keywords = ["mathematics", "formula", "theorem", "proof", "equation"]
        
        # Check if query already has math keywords
        has_math_keyword = any(keyword in query.lower() for keyword in math_keywords)
        
        if not has_math_keyword:
            # Add "mathematics" to improve results
            query = f"{query} mathematics"
        
        # Prioritize educational sources
        query = f"{query} site:math.stackexchange.com OR site:khanacademy.org OR site:mathworld.wolfram.com"
        
        return query
    
    def _generate_citation_id(self) -> str:
        """Generate unique citation ID"""
        citation_count = len(self.citations) + 1
        return f"cite_{citation_count}"
    
    def _add_citation(self, result: Dict[str, Any]):
        """Add result to citations list"""
        citation = {
            "id": result["citation_id"],
            "title": result["title"],
            "url": result["url"],
            "accessed_date": datetime.now().strftime("%Y-%m-%d"),
            "source": result["source"]
        }
        self.citations.append(citation)
    
    def get_citations(self, format: str = "text") -> str:
        """
        Get formatted citations
        
        Args:
            format: Citation format ('text', 'bibtex', 'apa', 'mla')
            
        Returns:
            Formatted citations string
        """
        if not self.citations:
            return "No citations available."
        
        if format == "text":
            return self._format_text_citations()
        elif format == "apa":
            return self._format_apa_citations()
        elif format == "mla":
            return self._format_mla_citations()
        elif format == "bibtex":
            return self._format_bibtex_citations()
        else:
            return self._format_text_citations()
    
    def _format_text_citations(self) -> str:
        """Format citations as plain text"""
        citation_lines = ["REFERENCES:", "=" * 60, ""]
        
        for citation in self.citations:
            citation_lines.append(f"[{citation['id']}] {citation['title']}")
            citation_lines.append(f"    URL: {citation['url']}")
            citation_lines.append(f"    Source: {citation['source']}")
            citation_lines.append(f"    Accessed: {citation['accessed_date']}")
            citation_lines.append("")
        
        return "\n".join(citation_lines)
    
    def _format_apa_citations(self) -> str:
        """Format citations in APA style"""
        citation_lines = ["REFERENCES (APA Style):", "=" * 60, ""]
        
        for citation in self.citations:
            # APA format: Title. (Date). Retrieved from URL
            apa_citation = (
                f"{citation['title']}. ({citation['accessed_date']}). "
                f"Retrieved from {citation['url']}"
            )
            citation_lines.append(apa_citation)
            citation_lines.append("")
        
        return "\n".join(citation_lines)
    
    def _format_mla_citations(self) -> str:
        """Format citations in MLA style"""
        citation_lines = ["Works Cited (MLA Style):", "=" * 60, ""]
        
        for citation in self.citations:
            # MLA format: "Title." Web. Date.
            mla_citation = f'"{citation["title"]}." Web. {citation["accessed_date"]}. <{citation["url"]}>.'
            citation_lines.append(mla_citation)
            citation_lines.append("")
        
        return "\n".join(citation_lines)
    
    def _format_bibtex_citations(self) -> str:
        """Format citations in BibTeX style"""
        citation_lines = []
        
        for citation in self.citations:
            # Generate BibTeX key from citation ID
            bibtex_key = citation['id'].replace('_', '')
            
            bibtex_entry = f"""@misc{{{bibtex_key},
    title = {{{citation['title']}}},
    url = {{{citation['url']}}},
    note = {{Accessed: {citation['accessed_date']}}},
    howpublished = {{\\url{{{citation['url']}}}}}
}}"""
            citation_lines.append(bibtex_entry)
            citation_lines.append("")
        
        return "\n".join(citation_lines)
    
    def verify_url(self, url: str) -> Dict[str, Any]:
        """
        Verify that a URL is valid and accessible
        
        Args:
            url: URL to verify
            
        Returns:
            Verification result
        """
        try:
            import requests
            
            # Check URL format
            url_pattern = re.compile(
                r'^https?://'  # http:// or https://
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
                r'localhost|'  # localhost
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
                r'(?::\d+)?'  # optional port
                r'(?:/?|[/?]\S+)$', re.IGNORECASE)
            
            if not url_pattern.match(url):
                return {
                    "valid": False,
                    "error": "Invalid URL format",
                    "url": url
                }
            
            # Try to access URL
            response = requests.head(url, timeout=5, allow_redirects=True)
            
            return {
                "valid": response.status_code == 200,
                "status_code": response.status_code,
                "url": url,
                "accessible": response.status_code < 400
            }
            
        except Exception as e:
            return {
                "valid": False,
                "error": str(e),
                "url": url
            }
    
    def clear_citations(self):
        """Clear all citations"""
        self.citations = []
        logger.debug("Citations cleared")


class MathWebSearchAssistant:
    """Assistant for mathematical web searches with smart filtering"""
    
    def __init__(self):
        """Initialize math web search assistant"""
        self.search_tool = WebSearchTool()
        
        # Trusted mathematical sources
        self.trusted_sources = [
            "math.stackexchange.com",
            "mathworld.wolfram.com",
            "khanacademy.org",
            "brilliant.org",
            "tutorial.math.lamar.edu",
            "mathsisfun.com",
            "purplemath.com",
            "cut-the-knot.org",
            "artofproblemsolving.com"
        ]
    
    def search_math_concept(self, concept: str, max_results: int = 5) -> Dict[str, Any]:
        """
        Search for a mathematical concept with filtering
        
        Args:
            concept: Mathematical concept to search
            max_results: Maximum results
            
        Returns:
            Filtered search results
        """
        # Perform search
        results = self.search_tool.search(concept, search_type="math", max_results=max_results * 2)
        
        if not results["success"]:
            return results
        
        # Filter for trusted sources
        filtered_results = []
        for result in results["results"]:
            # Check if from trusted source
            is_trusted = any(source in result["url"] for source in self.trusted_sources)
            result["is_trusted_source"] = is_trusted
            
            # Prioritize trusted sources
            if is_trusted:
                filtered_results.insert(0, result)
            else:
                filtered_results.append(result)
        
        # Limit to max_results
        filtered_results = filtered_results[:max_results]
        
        results["results"] = filtered_results
        results["count"] = len(filtered_results)
        
        return results
    
    def get_formatted_references(self, format: str = "text") -> str:
        """Get formatted references from search"""
        return self.search_tool.get_citations(format)
