"""Text processing utilities."""

from typing import List, Dict, Any
import re


class TextProcessor:
    """Process and transform text data."""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Remove extra whitespace and normalize text."""
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    @staticmethod
    def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
        """
        Split text into overlapping chunks for processing.
        
        Args:
            text: The text to chunk
            chunk_size: Maximum size of each chunk
            overlap: Number of characters to overlap between chunks
        
        Returns:
            List of text chunks
        """
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - overlap
        
        return chunks
    
    @staticmethod
    def extract_keywords(text: str) -> List[str]:
        """Extract potential keywords from text."""
        # Simple keyword extraction - can be enhanced with NLP
        words = re.findall(r'\b[A-Za-z]{4,}\b', text)
        # Remove common words
        stopwords = {'that', 'this', 'with', 'from', 'have', 'will', 'been', 'were', 'they'}
        keywords = [w.lower() for w in words if w.lower() not in stopwords]
        return list(set(keywords))
