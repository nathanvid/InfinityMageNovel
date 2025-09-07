"""
Character-focused document loader for the Infinity Mage RAG system.

This module provides enhanced document loading capabilities that extract
character information, relationships, and context from the translated chapters.
"""

import os
import re
from typing import List, Dict, Any, Set
from dataclasses import dataclass
from langchain.document_loaders.base import BaseLoader
from langchain.schema import Document


@dataclass
class CharacterMention:
    """Represents a character mention in the text."""
    name: str
    context: str
    chapter_title: str
    position: int
    

class CharacterAwareMarkdownLoader(BaseLoader):
    """
    Enhanced markdown loader that extracts character information and relationships.
    """
    
    def __init__(self, file_path: str, character_names: Set[str] = None):
        """
        Initialize the loader.
        
        Args:
            file_path: Path to the markdown file
            character_names: Set of known character names for better detection
        """
        self.file_path = file_path
        self.character_names = character_names or set()
        
    def load(self) -> List[Document]:
        """Load document with enhanced character metadata."""
        with open(self.file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Extract frontmatter and content
        frontmatter, content_body = self._parse_frontmatter(content)
        
        # Extract character information
        character_mentions = self._extract_character_mentions(
            content_body, frontmatter.get('title', '')
        )
        
        # Enhance metadata
        enhanced_metadata = {
            **frontmatter,
            'source': os.path.basename(self.file_path),
            'character_mentions': [mention.name for mention in character_mentions],
            'character_count': len(character_mentions),
            'has_dialogue': self._has_dialogue(content_body),
            'has_action': self._has_action_sequences(content_body),
            'chapter_themes': self._extract_themes(content_body)
        }
        
        return [Document(
            page_content=content_body.strip(),
            metadata=enhanced_metadata
        )]
    
    def _parse_frontmatter(self, content: str) -> tuple[Dict[str, Any], str]:
        """Parse YAML frontmatter from markdown content."""
        frontmatter_match = re.match(r'^---\n(.*?)\n---\n(.*)', content, re.DOTALL)
        
        if frontmatter_match:
            frontmatter_text = frontmatter_match.group(1)
            content_body = frontmatter_match.group(2)
            
            # Parse frontmatter into dictionary
            metadata = {}
            for line in frontmatter_text.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    metadata[key.strip()] = value.strip()
            
            return metadata, content_body
        else:
            return {}, content
    
    def _extract_character_mentions(self, content: str, chapter_title: str) -> List[CharacterMention]:
        """Extract character mentions from the content."""
        mentions = []
        
        # Common character name patterns in the novel
        character_patterns = [
            r'\b(Shirone|Shiro)\b',  # Main character variations
            r'\b(Rian|Ryan)\b',      # Common character variations
            r'\b(Amy|Amie)\b',
            r'\b(Vincent|Olina)\b',   # Parents
            r'\b(Alpheas|Alfonso)\b', # School related
            r'\b(Carmis|Theraze)\b',  # Family names
        ]
        
        # Add known character names if provided
        if self.character_names:
            for name in self.character_names:
                character_patterns.append(rf'\b{re.escape(name)}\b')
        
        # Find all character mentions
        for pattern in character_patterns:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                # Get context around the mention
                start = max(0, match.start() - 100)
                end = min(len(content), match.end() + 100)
                context = content[start:end].replace('\n', ' ')
                
                mentions.append(CharacterMention(
                    name=match.group(1),
                    context=context,
                    chapter_title=chapter_title,
                    position=match.start()
                ))
        
        return mentions
    
    def _has_dialogue(self, content: str) -> bool:
        """Check if content contains dialogue."""
        dialogue_patterns = [
            r'"[^"]*"',  # Quoted speech
            r"'[^']*'",  # Single quoted speech
            r'said|asked|replied|whispered|shouted|exclaimed',  # Speech verbs
        ]
        
        for pattern in dialogue_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        return False
    
    def _has_action_sequences(self, content: str) -> bool:
        """Detect action sequences in the content."""
        action_keywords = [
            'attack', 'fight', 'battle', 'magic', 'spell', 'cast',
            'sword', 'weapon', 'defend', 'dodge', 'strike', 'hit'
        ]
        
        action_count = 0
        for keyword in action_keywords:
            action_count += len(re.findall(rf'\b{keyword}\b', content, re.IGNORECASE))
        
        return action_count > 2  # Threshold for action sequence
    
    def _extract_themes(self, content: str) -> List[str]:
        """Extract thematic elements from the content."""
        themes = []
        
        theme_keywords = {
            'magic': ['magic', 'mage', 'spell', 'enchant', 'mystical'],
            'school': ['school', 'class', 'student', 'teacher', 'lesson'],
            'family': ['family', 'parent', 'father', 'mother', 'son', 'daughter'],
            'friendship': ['friend', 'companion', 'together', 'help', 'support'],
            'conflict': ['fight', 'enemy', 'oppose', 'conflict', 'battle'],
            'growth': ['learn', 'grow', 'develop', 'improve', 'progress'],
        }
        
        for theme, keywords in theme_keywords.items():
            theme_score = sum(
                len(re.findall(rf'\b{keyword}\b', content, re.IGNORECASE))
                for keyword in keywords
            )
            if theme_score > 1:  # Threshold for theme presence
                themes.append(theme)
        
        return themes


class CharacterDocumentProcessor:
    """
    Processes multiple documents and extracts comprehensive character information.
    """
    
    def __init__(self, data_directory: str):
        """
        Initialize processor with data directory.
        
        Args:
            data_directory: Path to directory containing translated chapters
        """
        self.data_directory = data_directory
        self.character_names = set()
        self.documents = []
        
    def load_all_documents(self) -> List[Document]:
        """Load all documents with character-aware processing."""
        # First pass: collect character names
        self._collect_character_names()
        
        # Second pass: load documents with character awareness
        documents = []
        
        for filename in sorted(os.listdir(self.data_directory)):
            if filename.endswith('.md'):
                file_path = os.path.join(self.data_directory, filename)
                loader = CharacterAwareMarkdownLoader(file_path, self.character_names)
                documents.extend(loader.load())
        
        self.documents = documents
        return documents
    
    def _collect_character_names(self):
        """First pass to collect character names from all chapters."""
        common_names = set()
        
        for filename in os.listdir(self.data_directory):
            if filename.endswith('.md'):
                file_path = os.path.join(self.data_directory, filename)
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    
                # Extract potential character names (capitalized words)
                potential_names = re.findall(r'\b[A-Z][a-z]+\b', content)
                
                # Filter common words and keep names that appear frequently
                for name in potential_names:
                    if len(name) > 2 and name not in ['The', 'And', 'But', 'For', 'Chapter']:
                        common_names.add(name)
        
        # Keep names that appear in multiple chapters (likely character names)
        name_counts = {}
        for filename in os.listdir(self.data_directory):
            if filename.endswith('.md'):
                file_path = os.path.join(self.data_directory, filename)
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    
                for name in common_names:
                    if re.search(rf'\b{re.escape(name)}\b', content):
                        name_counts[name] = name_counts.get(name, 0) + 1
        
        # Keep names that appear in at least 3 chapters
        self.character_names = {
            name for name, count in name_counts.items() 
            if count >= 3
        }
    
    def get_character_statistics(self) -> Dict[str, Any]:
        """Get statistics about character mentions across all documents."""
        if not self.documents:
            self.load_all_documents()
        
        character_stats = {}
        
        for doc in self.documents:
            for char_name in doc.metadata.get('character_mentions', []):
                if char_name not in character_stats:
                    character_stats[char_name] = {
                        'total_mentions': 0,
                        'chapters_appeared': [],
                        'contexts': []
                    }
                
                character_stats[char_name]['total_mentions'] += 1
                character_stats[char_name]['chapters_appeared'].append(
                    doc.metadata.get('title', 'Unknown')
                )
        
        return character_stats