"""
Main RAG engine for character analysis in the Infinity Mage system.

This module provides the core RAG functionality specifically designed for
comprehensive character analysis, relationship mapping, and story understanding.
"""

import os
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import json

from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain.schema import Document
from langchain.chains import LLMChain

from character_loader import CharacterDocumentProcessor
from character_db import CharacterDatabase, CharacterProfile, Relationship, Ability
from embeddings import (
    CharacterAwareTextSplitter,
    MultiModalEmbeddingStrategy,
    CharacterQueryRouter
)


@dataclass
class CharacterAnalysisResult:
    """Result of character analysis query."""
    character_name: str
    summary: str
    appearance: str
    status: str
    relationships: str
    abilities: str
    development: str
    supporting_evidence: List[str]
    confidence_score: float
    sources: List[str]


class CharacterRAGEngine:
    """
    Main RAG engine for character analysis and information retrieval.
    """
    
    def __init__(
        self,
        openai_api_key: str,
        data_directory: str,
        persist_directory: str = "./character_profiles_db",
        model_name: str = "gpt-3.5-turbo"
    ):
        """
        Initialize the Character RAG Engine.
        
        Args:
            openai_api_key: OpenAI API key
            data_directory: Directory containing translated chapters
            persist_directory: Directory to persist character data and embeddings
            model_name: OpenAI model to use
        """
        self.openai_api_key = openai_api_key
        self.data_directory = data_directory
        self.persist_directory = persist_directory
        self.model_name = model_name
        
        # Initialize components
        self.llm = ChatOpenAI(
            api_key=openai_api_key,
            model=model_name,
            temperature=0.1
        )
        
        self.character_db = CharacterDatabase()
        self.document_processor = CharacterDocumentProcessor(data_directory)
        self.embedding_strategy = MultiModalEmbeddingStrategy(openai_api_key)
        
        # Initialize variables
        self.vector_stores = {}
        self.query_router = None
        self.documents = []
        
        # Create persist directory if it doesn't exist
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize prompts
        self._initialize_prompts()
    
    def _initialize_prompts(self):
        """Initialize prompt templates for different query types."""
        
        # Character analysis prompt
        self.character_analysis_prompt = ChatPromptTemplate.from_template("""
You are an expert literary analyst specializing in character analysis for the novel "Infinity Mage".

Based on the provided text excerpts, create a comprehensive character analysis for {character_name}.

EXCERPTS:
{context}

INSTRUCTIONS:
1. Extract and synthesize information about the character's:
   - Physical appearance and distinguishing features
   - Social, professional, and academic status
   - Relationships with other characters
   - Abilities, powers, and skills
   - Character development and growth

2. For each category, provide specific evidence from the text with chapter references
3. If information is not available, clearly state "Not mentioned in provided excerpts"
4. Focus on factual information rather than speculation

CHARACTER ANALYSIS:

**Appearance:**
[Describe physical appearance with text evidence]

**Status:**
[Describe social/professional/academic standing with evidence]

**Relationships:**
[List and describe relationships with other characters with evidence]

**Abilities:**
[List and describe abilities, powers, or skills with evidence]

**Development:**
[Describe character growth and key moments with evidence]

**Summary:**
[Provide a concise overall summary of the character]
""")
        
        # Relationship analysis prompt
        self.relationship_prompt = ChatPromptTemplate.from_template("""
You are analyzing relationships between characters in "Infinity Mage".

Analyze the relationship between {character1} and {character2} based on these excerpts:

EXCERPTS:
{context}

ANALYSIS:
1. **Relationship Type:** [friend/enemy/family/mentor/rival/ally/romantic/acquaintance]
2. **Relationship Strength:** [weak/moderate/strong/very strong]
3. **Development:** [How has their relationship changed over time?]
4. **Key Interactions:** [Important moments between them]
5. **Current Status:** [Current state of their relationship]

Provide specific evidence from the text for each point.
""")
        
        # Ability analysis prompt
        self.ability_prompt = ChatPromptTemplate.from_template("""
You are analyzing character abilities in "Infinity Mage".

Analyze {character_name}'s abilities based on these excerpts:

EXCERPTS:
{context}

ABILITY ANALYSIS:
1. **Magical Abilities:** [List and describe magical powers/spells]
2. **Combat Skills:** [Physical fighting capabilities]
3. **Intellectual Abilities:** [Mental/academic strengths]
4. **Social Skills:** [Leadership, persuasion, etc.]
5. **Limitations:** [Known weaknesses or restrictions]
6. **Development:** [How have their abilities grown?]

For each ability, provide:
- Proficiency level (beginner/intermediate/advanced/master)
- Specific examples from the text
- Chapter references where shown
""")
        
        # Timeline prompt
        self.timeline_prompt = ChatPromptTemplate.from_template("""
Create a character development timeline for {character_name} based on these excerpts:

EXCERPTS:
{context}

Create a chronological timeline of important events in this character's development:

TIMELINE:
[List events chronologically with chapter references]

For each event, include:
- Chapter reference
- Brief description of what happened
- How it affected the character's growth
- Relationships or abilities that changed

Focus on key moments that shaped the character's development.
""")
    
    def initialize_system(self, force_rebuild: bool = False):
        """
        Initialize the RAG system by processing documents and creating embeddings.
        
        Args:
            force_rebuild: Whether to rebuild even if existing data found
        """
        print("Initializing Character RAG System...")
        
        # Check if we have existing data
        character_db_path = os.path.join(self.persist_directory, "character_database.json")
        embeddings_exist = os.path.exists(os.path.join(self.persist_directory, "character_embeddings_db"))
        
        if not force_rebuild and os.path.exists(character_db_path) and embeddings_exist:
            print("Loading existing character database and embeddings...")
            self._load_existing_data()
        else:
            print("Building character database and embeddings from scratch...")
            self._build_from_scratch()
        
        print(f"System initialized with {len(self.character_db.get_all_characters())} characters")
        print(f"Vector stores available: {list(self.vector_stores.keys())}")
    
    def _load_existing_data(self):
        """Load existing character database and embeddings."""
        # Load character database
        character_db_path = os.path.join(self.persist_directory, "character_database.json")
        self.character_db.load_from_file(character_db_path)
        
        # Load embeddings
        embeddings_dir = os.path.join(self.persist_directory, "character_embeddings_db")
        self.vector_stores = self.embedding_strategy.load_existing_embeddings(embeddings_dir)
        
        # Initialize query router
        self.query_router = CharacterQueryRouter(self.vector_stores)
    
    def _build_from_scratch(self):
        """Build character database and embeddings from scratch."""
        # Load and process documents
        print("Loading documents...")
        self.documents = self.document_processor.load_all_documents()
        print(f"Loaded {len(self.documents)} documents")
        
        # Build character database from documents
        print("Building character database...")
        self._build_character_database()
        
        # Create embeddings
        print("Creating character-aware embeddings...")
        self._create_embeddings()
        
        # Save character database
        character_db_path = os.path.join(self.persist_directory, "character_database.json")
        self.character_db.save_to_file(character_db_path)
        print(f"Character database saved to {character_db_path}")
    
    def _build_character_database(self):
        """Build character database from processed documents."""
        for doc in self.documents:
            chapter_title = doc.metadata.get('title', 'Unknown Chapter')
            character_mentions = doc.metadata.get('character_mentions', [])
            
            # Update character profiles
            for char_name in character_mentions:
                character = self.character_db.get_or_create_character(char_name)
                
                # Update basic info
                if chapter_title not in character.chapters_appeared:
                    character.chapters_appeared.append(chapter_title)
                character.total_mentions += 1
                
                if not character.first_appearance_chapter:
                    character.first_appearance_chapter = chapter_title
                
                character.last_updated = datetime.now()
    
    def _create_embeddings(self):
        """Create character-aware embeddings."""
        # Initialize text splitter with known character names
        character_names = list(self.character_db.characters.keys())
        text_splitter = CharacterAwareTextSplitter(
            chunk_size=800,
            chunk_overlap=100,
            character_names=character_names
        )
        
        # Split documents with character awareness
        print("Creating character-aware chunks...")
        enhanced_chunks = text_splitter.split_documents(self.documents)
        print(f"Created {len(enhanced_chunks)} enhanced chunks")
        
        # Create multi-modal embeddings
        embeddings_dir = os.path.join(self.persist_directory, "character_embeddings_db")
        self.vector_stores = self.embedding_strategy.create_character_embeddings(
            enhanced_chunks,
            embeddings_dir
        )
        
        # Initialize query router
        self.query_router = CharacterQueryRouter(self.vector_stores)
    
    def analyze_character(self, character_name: str, k: int = 10) -> CharacterAnalysisResult:
        """
        Perform comprehensive character analysis.
        
        Args:
            character_name: Name of character to analyze
            k: Number of relevant chunks to retrieve
            
        Returns:
            Comprehensive character analysis result
        """
        if not self.query_router:
            raise ValueError("System not initialized. Call initialize_system() first.")
        
        # Retrieve relevant documents
        query = f"Tell me about {character_name}. Who is {character_name}? What does {character_name} look like? What are {character_name}'s abilities and relationships?"
        relevant_docs = self.query_router.route_query(query, k=k)
        
        if not relevant_docs:
            return CharacterAnalysisResult(
                character_name=character_name,
                summary="No information found for this character.",
                appearance="Not mentioned in available excerpts",
                status="Not mentioned in available excerpts",
                relationships="Not mentioned in available excerpts",
                abilities="Not mentioned in available excerpts",
                development="Not mentioned in available excerpts",
                supporting_evidence=[],
                confidence_score=0.0,
                sources=[]
            )
        
        # Create context from relevant documents
        context = self._create_context_from_docs(relevant_docs)
        
        # Generate analysis
        chain = LLMChain(
            llm=self.llm,
            prompt=self.character_analysis_prompt
        )
        
        analysis = chain.run(
            character_name=character_name,
            context=context
        )
        
        # Extract sources
        sources = [doc.metadata.get('title', 'Unknown') for doc in relevant_docs]
        
        # Parse analysis into structured result
        return self._parse_character_analysis(character_name, analysis, relevant_docs, sources)
    
    def analyze_relationship(self, character1: str, character2: str, k: int = 8) -> str:
        """
        Analyze relationship between two characters.
        
        Args:
            character1: First character name
            character2: Second character name
            k: Number of relevant chunks to retrieve
            
        Returns:
            Relationship analysis
        """
        if not self.query_router:
            raise ValueError("System not initialized. Call initialize_system() first.")
        
        # Query for relationship information
        query = f"relationship between {character1} and {character2}. How do {character1} and {character2} interact? Are {character1} and {character2} friends or enemies?"
        relevant_docs = self.query_router.route_query(query, k=k)
        
        if not relevant_docs:
            return f"No information found about the relationship between {character1} and {character2}."
        
        context = self._create_context_from_docs(relevant_docs)
        
        chain = LLMChain(
            llm=self.llm,
            prompt=self.relationship_prompt
        )
        
        return chain.run(
            character1=character1,
            character2=character2,
            context=context
        )
    
    def analyze_abilities(self, character_name: str, k: int = 8) -> str:
        """
        Analyze character's abilities and powers.
        
        Args:
            character_name: Character to analyze
            k: Number of relevant chunks to retrieve
            
        Returns:
            Abilities analysis
        """
        if not self.query_router:
            raise ValueError("System not initialized. Call initialize_system() first.")
        
        query = f"{character_name} abilities powers skills magic combat. What can {character_name} do? What magic does {character_name} use?"
        relevant_docs = self.query_router.route_query(query, k=k)
        
        if not relevant_docs:
            return f"No information found about {character_name}'s abilities."
        
        context = self._create_context_from_docs(relevant_docs)
        
        chain = LLMChain(
            llm=self.llm,
            prompt=self.ability_prompt
        )
        
        return chain.run(
            character_name=character_name,
            context=context
        )
    
    def create_character_timeline(self, character_name: str, k: int = 15) -> str:
        """
        Create character development timeline.
        
        Args:
            character_name: Character to analyze
            k: Number of relevant chunks to retrieve
            
        Returns:
            Character timeline
        """
        if not self.query_router:
            raise ValueError("System not initialized. Call initialize_system() first.")
        
        query = f"{character_name} development growth changes events timeline. How has {character_name} changed throughout the story?"
        relevant_docs = self.query_router.route_query(query, k=k)
        
        if not relevant_docs:
            return f"No developmental information found for {character_name}."
        
        context = self._create_context_from_docs(relevant_docs)
        
        chain = LLMChain(
            llm=self.llm,
            prompt=self.timeline_prompt
        )
        
        return chain.run(
            character_name=character_name,
            context=context
        )
    
    def search_characters(self, query: str, k: int = 10) -> List[Document]:
        """
        Search for characters based on description.
        
        Args:
            query: Search query
            k: Number of results to return
            
        Returns:
            List of relevant documents
        """
        if not self.query_router:
            raise ValueError("System not initialized. Call initialize_system() first.")
        
        return self.query_router.route_query(query, k=k)
    
    def get_character_list(self) -> List[str]:
        """Get list of all known characters."""
        return list(self.character_db.characters.keys())
    
    def get_character_statistics(self) -> Dict[str, Any]:
        """Get statistics about the character database."""
        return self.character_db.get_statistics()
    
    def _create_context_from_docs(self, docs: List[Document]) -> str:
        """Create context string from list of documents."""
        context_parts = []
        
        for i, doc in enumerate(docs):
            chapter = doc.metadata.get('title', 'Unknown Chapter')
            content = doc.page_content
            
            context_parts.append(f"[Chapter: {chapter}]\n{content}\n")
        
        return "\n".join(context_parts)
    
    def _parse_character_analysis(
        self,
        character_name: str,
        analysis: str,
        docs: List[Document],
        sources: List[str]
    ) -> CharacterAnalysisResult:
        """Parse character analysis into structured result."""
        # Extract sections from analysis
        sections = {
            'appearance': self._extract_section(analysis, 'Appearance'),
            'status': self._extract_section(analysis, 'Status'),
            'relationships': self._extract_section(analysis, 'Relationships'),
            'abilities': self._extract_section(analysis, 'Abilities'),
            'development': self._extract_section(analysis, 'Development'),
            'summary': self._extract_section(analysis, 'Summary')
        }
        
        # Calculate confidence score based on amount of information found
        confidence_score = self._calculate_confidence_score(docs, sections)
        
        # Extract supporting evidence
        supporting_evidence = [doc.page_content[:200] + "..." for doc in docs[:3]]
        
        return CharacterAnalysisResult(
            character_name=character_name,
            summary=sections['summary'] or "Limited information available",
            appearance=sections['appearance'] or "Not mentioned in provided excerpts",
            status=sections['status'] or "Not mentioned in provided excerpts",
            relationships=sections['relationships'] or "Not mentioned in provided excerpts",
            abilities=sections['abilities'] or "Not mentioned in provided excerpts",
            development=sections['development'] or "Not mentioned in provided excerpts",
            supporting_evidence=supporting_evidence,
            confidence_score=confidence_score,
            sources=list(set(sources))
        )
    
    def _extract_section(self, text: str, section_name: str) -> str:
        """Extract a specific section from the analysis text."""
        import re
        pattern = rf'\*\*{section_name}:\*\*(.*?)(?=\*\*|\Z)'
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return ""
    
    def _calculate_confidence_score(self, docs: List[Document], sections: Dict[str, str]) -> float:
        """Calculate confidence score based on available information."""
        base_score = min(len(docs) / 10.0, 1.0)  # More docs = higher confidence
        
        # Boost score based on information completeness
        section_scores = []
        for section_content in sections.values():
            if section_content and "not mentioned" not in section_content.lower():
                section_scores.append(0.2)
        
        completeness_score = sum(section_scores)
        
        return min(base_score + completeness_score, 1.0)
    
    def export_character_profiles(self, output_file: str):
        """Export all character profiles to JSON file."""
        data = {
            'characters': {name: profile.to_dict() for name, profile in self.character_db.characters.items()},
            'statistics': self.get_character_statistics(),
            'export_timestamp': datetime.now().isoformat()
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"Character profiles exported to {output_file}")
    
    def debug_query(self, query: str, k: int = 5) -> Dict[str, Any]:
        """Debug query routing and retrieval."""
        if not self.query_router:
            raise ValueError("System not initialized. Call initialize_system() first.")
        
        # Get multi-store results
        multi_results = self.query_router.multi_store_search(query, k_per_store=k)
        
        # Get routed results
        routed_results = self.query_router.route_query(query, k=k)
        
        return {
            'query': query,
            'multi_store_results': {
                store: len(results) for store, results in multi_results.items()
            },
            'routed_results_count': len(routed_results),
            'query_classification': self.query_router._classify_query(query)
        }