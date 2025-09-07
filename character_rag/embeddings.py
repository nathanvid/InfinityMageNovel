"""
Character-centric embedding strategies for the Infinity Mage RAG system.

This module provides specialized embedding and chunking strategies optimized
for character analysis and retrieval from the novel chapters.
"""

from typing import List, Dict, Any, Optional, Tuple
import re
from dataclasses import dataclass
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document
from langchain_community.vectorstores import Chroma
import numpy as np


@dataclass
class CharacterChunk:
    """Enhanced chunk with character-specific metadata."""
    content: str
    characters_mentioned: List[str]
    chunk_type: str  # dialogue, action, description, relationship
    importance_score: float
    chapter_info: Dict[str, Any]
    position_in_chapter: int


class CharacterAwareTextSplitter:
    """
    Text splitter that preserves character contexts and creates meaningful chunks
    for character analysis.
    """
    
    def __init__(
        self,
        chunk_size: int = 800,
        chunk_overlap: int = 100,
        character_names: Optional[List[str]] = None
    ):
        """
        Initialize the character-aware text splitter.
        
        Args:
            chunk_size: Maximum size of each chunk
            chunk_overlap: Overlap between chunks
            character_names: Known character names for better processing
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.character_names = set(character_names or [])
        self.base_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", "! ", "? ", " ", ""]
        )
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents with character-aware chunking."""
        enhanced_chunks = []
        
        for doc in documents:
            chunks = self._create_character_chunks(doc)
            enhanced_chunks.extend(chunks)
        
        return enhanced_chunks
    
    def _create_character_chunks(self, document: Document) -> List[Document]:
        """Create character-aware chunks from a single document."""
        content = document.page_content
        base_chunks = self.base_splitter.split_text(content)
        
        enhanced_chunks = []
        
        for i, chunk in enumerate(base_chunks):
            # Analyze chunk for character information
            chunk_analysis = self._analyze_chunk(chunk, document.metadata)
            
            # Create enhanced metadata
            enhanced_metadata = {
                **document.metadata,
                'chunk_id': f"{document.metadata.get('source', 'unknown')}_{i}",
                'characters_in_chunk': chunk_analysis['characters'],
                'chunk_type': chunk_analysis['type'],
                'importance_score': chunk_analysis['importance'],
                'dialogue_ratio': chunk_analysis['dialogue_ratio'],
                'action_indicators': chunk_analysis['action_indicators'],
                'relationship_indicators': chunk_analysis['relationship_indicators'],
                'position_in_chapter': i,
                'total_chunks': len(base_chunks)
            }
            
            enhanced_chunks.append(Document(
                page_content=chunk,
                metadata=enhanced_metadata
            ))
        
        return enhanced_chunks
    
    def _analyze_chunk(self, chunk: str, chapter_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a chunk for character-specific information."""
        analysis = {
            'characters': self._find_characters_in_chunk(chunk),
            'type': self._determine_chunk_type(chunk),
            'importance': self._calculate_importance_score(chunk),
            'dialogue_ratio': self._calculate_dialogue_ratio(chunk),
            'action_indicators': self._find_action_indicators(chunk),
            'relationship_indicators': self._find_relationship_indicators(chunk)
        }
        
        return analysis
    
    def _find_characters_in_chunk(self, chunk: str) -> List[str]:
        """Find character names mentioned in the chunk."""
        characters_found = []
        
        # Use known character names if available
        for name in self.character_names:
            if re.search(rf'\b{re.escape(name)}\b', chunk, re.IGNORECASE):
                characters_found.append(name)
        
        # Also look for capitalized words that might be character names
        potential_names = re.findall(r'\b[A-Z][a-z]+\b', chunk)
        for name in potential_names:
            if (len(name) > 2 and 
                name not in ['The', 'And', 'But', 'For', 'His', 'Her', 'That', 'This'] and
                name not in characters_found):
                characters_found.append(name)
        
        return characters_found
    
    def _determine_chunk_type(self, chunk: str) -> str:
        """Determine the type of content in the chunk."""
        dialogue_markers = ['"', "'", 'said', 'asked', 'replied', 'whispered', 'shouted']
        action_markers = ['ran', 'jumped', 'attacked', 'cast', 'magic', 'spell', 'sword']
        description_markers = ['was', 'were', 'looked', 'appeared', 'seemed']
        relationship_markers = ['friend', 'enemy', 'family', 'loved', 'hated', 'met']
        
        dialogue_score = sum(1 for marker in dialogue_markers if marker.lower() in chunk.lower())
        action_score = sum(1 for marker in action_markers if marker.lower() in chunk.lower())
        description_score = sum(1 for marker in description_markers if marker.lower() in chunk.lower())
        relationship_score = sum(1 for marker in relationship_markers if marker.lower() in chunk.lower())
        
        scores = {
            'dialogue': dialogue_score,
            'action': action_score,
            'description': description_score,
            'relationship': relationship_score
        }
        
        return max(scores, key=scores.get)
    
    def _calculate_importance_score(self, chunk: str) -> float:
        """Calculate importance score for the chunk."""
        importance_indicators = [
            ('magic', 2.0),
            ('spell', 1.8),
            ('power', 1.5),
            ('ability', 1.5),
            ('friend', 1.3),
            ('enemy', 1.3),
            ('family', 1.4),
            ('school', 1.2),
            ('teacher', 1.2),
            ('student', 1.1),
            ('fight', 1.6),
            ('battle', 1.6),
            ('learn', 1.3),
            ('understand', 1.2)
        ]
        
        score = 1.0  # Base score
        chunk_lower = chunk.lower()
        
        for indicator, weight in importance_indicators:
            if indicator in chunk_lower:
                score += weight * 0.1
        
        # Boost score for chunks with multiple characters
        character_count = len(self._find_characters_in_chunk(chunk))
        if character_count > 1:
            score += character_count * 0.2
        
        return min(score, 3.0)  # Cap at 3.0
    
    def _calculate_dialogue_ratio(self, chunk: str) -> float:
        """Calculate ratio of dialogue content in chunk."""
        # Count quoted content
        quotes = re.findall(r'"[^"]*"', chunk)
        dialogue_chars = sum(len(quote) for quote in quotes)
        total_chars = len(chunk)
        
        return dialogue_chars / total_chars if total_chars > 0 else 0.0
    
    def _find_action_indicators(self, chunk: str) -> List[str]:
        """Find action indicators in the chunk."""
        action_patterns = [
            r'\b(attack|fight|battle|cast|magic|spell)\b',
            r'\b(ran|jumped|fell|hit|struck)\b',
            r'\b(defend|dodge|block|counter)\b',
            r'\b(sword|weapon|staff|wand)\b'
        ]
        
        indicators = []
        for pattern in action_patterns:
            matches = re.findall(pattern, chunk, re.IGNORECASE)
            indicators.extend(matches)
        
        return list(set(indicators))  # Remove duplicates
    
    def _find_relationship_indicators(self, chunk: str) -> List[str]:
        """Find relationship indicators in the chunk."""
        relationship_patterns = [
            r'\b(friend|friendship|ally)\b',
            r'\b(enemy|rival|opponent)\b',
            r'\b(family|father|mother|son|daughter|brother|sister)\b',
            r'\b(love|loved|loving|romantic)\b',
            r'\b(hate|hated|dislike)\b',
            r'\b(mentor|teacher|student|disciple)\b',
            r'\b(trust|trusted|betrayed)\b'
        ]
        
        indicators = []
        for pattern in relationship_patterns:
            matches = re.findall(pattern, chunk, re.IGNORECASE)
            indicators.extend(matches)
        
        return list(set(indicators))  # Remove duplicates


class MultiModalEmbeddingStrategy:
    """
    Multi-modal embedding strategy that creates specialized embeddings
    for different types of character queries.
    """
    
    def __init__(self, openai_api_key: str):
        """Initialize with OpenAI API key."""
        self.embeddings = OpenAIEmbeddings(api_key=openai_api_key)
        
    def create_character_embeddings(
        self, 
        documents: List[Document],
        persist_directory: str = "./character_embeddings_db"
    ) -> Dict[str, Chroma]:
        """
        Create multiple vector stores for different query types.
        
        Returns:
            Dictionary of vector stores for different purposes
        """
        # Filter documents by type for specialized embeddings
        dialogue_docs = self._filter_documents_by_type(documents, "dialogue")
        action_docs = self._filter_documents_by_type(documents, "action")
        description_docs = self._filter_documents_by_type(documents, "description")
        relationship_docs = self._filter_documents_by_type(documents, "relationship")
        
        # Create specialized vector stores
        vector_stores = {}
        
        # General character store (all documents)
        vector_stores['general'] = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=f"{persist_directory}/general",
            collection_name="character_general"
        )
        
        # Dialogue-focused store
        if dialogue_docs:
            vector_stores['dialogue'] = Chroma.from_documents(
                documents=dialogue_docs,
                embedding=self.embeddings,
                persist_directory=f"{persist_directory}/dialogue",
                collection_name="character_dialogue"
            )
        
        # Action-focused store
        if action_docs:
            vector_stores['action'] = Chroma.from_documents(
                documents=action_docs,
                embedding=self.embeddings,
                persist_directory=f"{persist_directory}/action",
                collection_name="character_action"
            )
        
        # Description-focused store
        if description_docs:
            vector_stores['description'] = Chroma.from_documents(
                documents=description_docs,
                embedding=self.embeddings,
                persist_directory=f"{persist_directory}/description",
                collection_name="character_description"
            )
        
        # Relationship-focused store
        if relationship_docs:
            vector_stores['relationship'] = Chroma.from_documents(
                documents=relationship_docs,
                embedding=self.embeddings,
                persist_directory=f"{persist_directory}/relationship",
                collection_name="character_relationship"
            )
        
        return vector_stores
    
    def _filter_documents_by_type(self, documents: List[Document], doc_type: str) -> List[Document]:
        """Filter documents by chunk type."""
        return [
            doc for doc in documents
            if doc.metadata.get('chunk_type') == doc_type
        ]
    
    def load_existing_embeddings(
        self,
        persist_directory: str = "./character_embeddings_db"
    ) -> Dict[str, Chroma]:
        """Load existing vector stores from disk."""
        vector_stores = {}
        
        store_types = ['general', 'dialogue', 'action', 'description', 'relationship']
        
        for store_type in store_types:
            try:
                vector_stores[store_type] = Chroma(
                    embedding_function=self.embeddings,
                    persist_directory=f"{persist_directory}/{store_type}",
                    collection_name=f"character_{store_type}"
                )
            except Exception as e:
                print(f"Could not load {store_type} vector store: {e}")
        
        return vector_stores


class CharacterQueryRouter:
    """
    Routes queries to appropriate vector stores based on query type.
    """
    
    def __init__(self, vector_stores: Dict[str, Chroma]):
        """Initialize with vector stores."""
        self.vector_stores = vector_stores
    
    def route_query(self, query: str, k: int = 5) -> List[Document]:
        """
        Route query to appropriate vector store and retrieve relevant documents.
        
        Args:
            query: The search query
            k: Number of documents to retrieve
            
        Returns:
            List of relevant documents
        """
        query_type = self._classify_query(query)
        
        # Select appropriate vector store
        if query_type in self.vector_stores:
            vectorstore = self.vector_stores[query_type]
        else:
            vectorstore = self.vector_stores.get('general')
        
        if vectorstore is None:
            return []
        
        # Retrieve documents
        results = vectorstore.similarity_search(query, k=k)
        
        # If primary store doesn't return enough results, supplement with general store
        if len(results) < k and query_type != 'general' and 'general' in self.vector_stores:
            additional_results = self.vector_stores['general'].similarity_search(
                query, 
                k=k-len(results)
            )
            results.extend(additional_results)
        
        return results
    
    def _classify_query(self, query: str) -> str:
        """Classify query to determine which vector store to use."""
        query_lower = query.lower()
        
        # Keywords for different query types
        dialogue_keywords = ['said', 'say', 'talk', 'speak', 'conversation', 'dialogue', 'quote']
        action_keywords = ['fight', 'battle', 'magic', 'spell', 'cast', 'attack', 'ability', 'power']
        description_keywords = ['look', 'appear', 'description', 'physical', 'appearance', 'height', 'hair']
        relationship_keywords = ['friend', 'relationship', 'family', 'enemy', 'love', 'mentor', 'ally']
        
        # Count keyword matches
        scores = {
            'dialogue': sum(1 for kw in dialogue_keywords if kw in query_lower),
            'action': sum(1 for kw in action_keywords if kw in query_lower),
            'description': sum(1 for kw in description_keywords if kw in query_lower),
            'relationship': sum(1 for kw in relationship_keywords if kw in query_lower)
        }
        
        # Return type with highest score, or 'general' if no clear winner
        max_score = max(scores.values())
        if max_score > 0:
            return max(scores, key=scores.get)
        
        return 'general'
    
    def multi_store_search(self, query: str, k_per_store: int = 3) -> Dict[str, List[Document]]:
        """
        Search across multiple stores and return categorized results.
        
        Args:
            query: The search query
            k_per_store: Number of documents to retrieve from each store
            
        Returns:
            Dictionary with results from each store
        """
        results = {}
        
        for store_name, vectorstore in self.vector_stores.items():
            try:
                store_results = vectorstore.similarity_search(query, k=k_per_store)
                if store_results:
                    results[store_name] = store_results
            except Exception as e:
                print(f"Error searching {store_name} store: {e}")
        
        return results