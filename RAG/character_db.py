"""
Character database structures for the Infinity Mage RAG system.

This module defines data structures for storing and managing character profiles,
relationships, and development timelines extracted from the novel chapters.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import json
from datetime import datetime


class CharacterStatusEnum(Enum):
    """Enum for character social/professional status."""
    STUDENT = "student"
    TEACHER = "teacher" 
    NOBLE = "noble"
    COMMONER = "commoner"
    MAGE = "mage"
    HUNTER = "hunter"
    MERCHANT = "merchant"
    ROYALTY = "royalty"
    UNKNOWN = "unknown"


class RelationshipType(Enum):
    """Enum for relationship types between characters."""
    FRIEND = "friend"
    ENEMY = "enemy"
    FAMILY = "family"
    MENTOR = "mentor"
    STUDENT = "student"
    RIVAL = "rival"
    ALLY = "ally"
    ROMANTIC = "romantic"
    ACQUAINTANCE = "acquaintance"
    UNKNOWN = "unknown"


class AbilityType(Enum):
    """Enum for character ability types."""
    MAGIC = "magic"
    COMBAT = "combat"
    INTELLECTUAL = "intellectual"
    SOCIAL = "social"
    PHYSICAL = "physical"
    LEADERSHIP = "leadership"
    UNKNOWN = "unknown"


@dataclass
class PhysicalAppearance:
    """Character physical appearance information."""
    height: Optional[str] = None
    build: Optional[str] = None
    hair_color: Optional[str] = None
    eye_color: Optional[str] = None
    distinguishing_features: List[str] = field(default_factory=list)
    clothing_style: Optional[str] = None
    age_appearance: Optional[str] = None
    description: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'height': self.height,
            'build': self.build,
            'hair_color': self.hair_color,
            'eye_color': self.eye_color,
            'distinguishing_features': self.distinguishing_features,
            'clothing_style': self.clothing_style,
            'age_appearance': self.age_appearance,
            'description': self.description
        }


@dataclass
class CharacterStatus:
    """Character status information."""
    social_status: List[str] = field(default_factory=list)
    professional_status: List[str] = field(default_factory=list) 
    academic_status: List[str] = field(default_factory=list)
    titles: List[str] = field(default_factory=list)
    affiliations: List[str] = field(default_factory=list)
    rank: Optional[str] = None
    reputation: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'social_status': self.social_status,
            'professional_status': self.professional_status,
            'academic_status': self.academic_status,
            'titles': self.titles,
            'affiliations': self.affiliations,
            'rank': self.rank,
            'reputation': self.reputation
        }


@dataclass
class Relationship:
    """Represents a relationship between two characters."""
    target_character: str
    relationship_type: RelationshipType
    description: str
    strength: float = 0.5  # 0.0 to 1.0, strength of relationship
    context: str = ""
    first_mentioned_chapter: Optional[str] = None
    development_notes: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'target_character': self.target_character,
            'relationship_type': self.relationship_type.value,
            'description': self.description,
            'strength': self.strength,
            'context': self.context,
            'first_mentioned_chapter': self.first_mentioned_chapter,
            'development_notes': self.development_notes
        }


@dataclass
class Ability:
    """Represents a character ability or skill."""
    name: str
    ability_type: AbilityType
    description: str
    proficiency_level: str = "unknown"  # beginner, intermediate, advanced, master
    magical_school: Optional[str] = None  # for magical abilities
    limitations: List[str] = field(default_factory=list)
    development_notes: List[str] = field(default_factory=list)
    first_shown_chapter: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'name': self.name,
            'ability_type': self.ability_type.value,
            'description': self.description,
            'proficiency_level': self.proficiency_level,
            'magical_school': self.magical_school,
            'limitations': self.limitations,
            'development_notes': self.development_notes,
            'first_shown_chapter': self.first_shown_chapter
        }


@dataclass
class CharacterDevelopmentEvent:
    """Represents a significant character development event."""
    chapter_title: str
    chapter_number: Optional[int] = None
    event_type: str = ""  # growth, setback, revelation, relationship_change, etc.
    description: str = ""
    impact: str = ""  # how this affected the character
    related_characters: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'chapter_title': self.chapter_title,
            'chapter_number': self.chapter_number,
            'event_type': self.event_type,
            'description': self.description,
            'impact': self.impact,
            'related_characters': self.related_characters
        }


@dataclass
class CharacterProfile:
    """Comprehensive character profile."""
    name: str
    aliases: List[str] = field(default_factory=list)
    appearance: PhysicalAppearance = field(default_factory=PhysicalAppearance)
    status: CharacterStatus = field(default_factory=CharacterStatus)
    relationships: Dict[str, Relationship] = field(default_factory=dict)
    abilities: Dict[str, Ability] = field(default_factory=dict)
    personality_traits: List[str] = field(default_factory=list)
    background: str = ""
    goals: List[str] = field(default_factory=list)
    fears: List[str] = field(default_factory=list)
    development_timeline: List[CharacterDevelopmentEvent] = field(default_factory=list)
    
    # Metadata
    first_appearance_chapter: Optional[str] = None
    total_mentions: int = 0
    chapters_appeared: List[str] = field(default_factory=list)
    last_updated: Optional[datetime] = None
    
    def add_relationship(self, relationship: Relationship):
        """Add or update a relationship."""
        self.relationships[relationship.target_character] = relationship
    
    def add_ability(self, ability: Ability):
        """Add or update an ability."""
        self.abilities[ability.name] = ability
    
    def add_development_event(self, event: CharacterDevelopmentEvent):
        """Add a development event to the timeline."""
        self.development_timeline.append(event)
        # Sort by chapter number if available
        self.development_timeline.sort(
            key=lambda x: x.chapter_number if x.chapter_number else 0
        )
    
    def get_relationship_summary(self) -> str:
        """Get a summary of all relationships."""
        if not self.relationships:
            return "No known relationships."
        
        summary_parts = []
        for rel in self.relationships.values():
            summary_parts.append(
                f"{rel.relationship_type.value.title()} with {rel.target_character}: {rel.description}"
            )
        
        return " | ".join(summary_parts)
    
    def get_ability_summary(self) -> str:
        """Get a summary of all abilities."""
        if not self.abilities:
            return "No known abilities."
        
        summary_parts = []
        for ability in self.abilities.values():
            summary_parts.append(
                f"{ability.name} ({ability.ability_type.value}): {ability.description}"
            )
        
        return " | ".join(summary_parts)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'name': self.name,
            'aliases': self.aliases,
            'appearance': self.appearance.to_dict(),
            'status': self.status.to_dict(),
            'relationships': {k: v.to_dict() for k, v in self.relationships.items()},
            'abilities': {k: v.to_dict() for k, v in self.abilities.items()},
            'personality_traits': self.personality_traits,
            'background': self.background,
            'goals': self.goals,
            'fears': self.fears,
            'development_timeline': [event.to_dict() for event in self.development_timeline],
            'first_appearance_chapter': self.first_appearance_chapter,
            'total_mentions': self.total_mentions,
            'chapters_appeared': self.chapters_appeared,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CharacterProfile':
        """Create CharacterProfile from dictionary."""
        profile = cls(name=data['name'])
        profile.aliases = data.get('aliases', [])
        
        # Reconstruct appearance
        appearance_data = data.get('appearance', {})
        profile.appearance = PhysicalAppearance(**appearance_data)
        
        # Reconstruct status
        status_data = data.get('status', {})
        profile.status = CharacterStatus(**status_data)
        
        # Reconstruct relationships
        relationships_data = data.get('relationships', {})
        for char_name, rel_data in relationships_data.items():
            rel_data['relationship_type'] = RelationshipType(rel_data['relationship_type'])
            profile.relationships[char_name] = Relationship(**rel_data)
        
        # Reconstruct abilities
        abilities_data = data.get('abilities', {})
        for ability_name, ability_data in abilities_data.items():
            ability_data['ability_type'] = AbilityType(ability_data['ability_type'])
            profile.abilities[ability_name] = Ability(**ability_data)
        
        # Reconstruct development timeline
        timeline_data = data.get('development_timeline', [])
        for event_data in timeline_data:
            profile.development_timeline.append(CharacterDevelopmentEvent(**event_data))
        
        # Set other attributes
        profile.personality_traits = data.get('personality_traits', [])
        profile.background = data.get('background', '')
        profile.goals = data.get('goals', [])
        profile.fears = data.get('fears', [])
        profile.first_appearance_chapter = data.get('first_appearance_chapter')
        profile.total_mentions = data.get('total_mentions', 0)
        profile.chapters_appeared = data.get('chapters_appeared', [])
        
        if data.get('last_updated'):
            profile.last_updated = datetime.fromisoformat(data['last_updated'])
        
        return profile


class CharacterDatabase:
    """
    Database for managing character profiles and relationships.
    """
    
    def __init__(self):
        """Initialize empty character database."""
        self.characters: Dict[str, CharacterProfile] = {}
        self.character_aliases: Dict[str, str] = {}  # alias -> canonical name mapping
    
    def add_character(self, profile: CharacterProfile):
        """Add a character profile to the database."""
        self.characters[profile.name] = profile
        
        # Update alias mappings
        for alias in profile.aliases:
            self.character_aliases[alias.lower()] = profile.name
    
    def get_character(self, name: str) -> Optional[CharacterProfile]:
        """Get character by name or alias."""
        # Try direct name match first
        if name in self.characters:
            return self.characters[name]
        
        # Try alias match
        canonical_name = self.character_aliases.get(name.lower())
        if canonical_name:
            return self.characters.get(canonical_name)
        
        return None
    
    def get_or_create_character(self, name: str) -> CharacterProfile:
        """Get existing character or create new one."""
        character = self.get_character(name)
        if character is None:
            character = CharacterProfile(name=name)
            self.add_character(character)
        return character
    
    def get_all_characters(self) -> List[CharacterProfile]:
        """Get all character profiles."""
        return list(self.characters.values())
    
    def search_characters(self, query: str) -> List[CharacterProfile]:
        """Search characters by name, alias, or description."""
        query_lower = query.lower()
        results = []
        
        for character in self.characters.values():
            # Check name
            if query_lower in character.name.lower():
                results.append(character)
                continue
            
            # Check aliases
            if any(query_lower in alias.lower() for alias in character.aliases):
                results.append(character)
                continue
            
            # Check background
            if query_lower in character.background.lower():
                results.append(character)
                continue
        
        return results
    
    def get_character_relationships(self, character_name: str) -> Dict[str, List[Relationship]]:
        """Get all relationships for a character (both outgoing and incoming)."""
        character = self.get_character(character_name)
        if not character:
            return {}
        
        relationships = {
            'outgoing': list(character.relationships.values()),
            'incoming': []
        }
        
        # Find incoming relationships
        for other_char in self.characters.values():
            if other_char.name == character_name:
                continue
            
            for relationship in other_char.relationships.values():
                if relationship.target_character == character_name:
                    relationships['incoming'].append(relationship)
        
        return relationships
    
    def save_to_file(self, filepath: str):
        """Save database to JSON file."""
        data = {
            'characters': {name: profile.to_dict() for name, profile in self.characters.items()},
            'aliases': self.character_aliases
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load_from_file(self, filepath: str):
        """Load database from JSON file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.characters = {}
        self.character_aliases = data.get('aliases', {})
        
        for name, profile_data in data.get('characters', {}).items():
            profile = CharacterProfile.from_dict(profile_data)
            self.characters[name] = profile
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics."""
        total_characters = len(self.characters)
        total_relationships = sum(len(char.relationships) for char in self.characters.values())
        total_abilities = sum(len(char.abilities) for char in self.characters.values())
        
        # Character status distribution
        status_counts = {}
        for character in self.characters.values():
            for status in character.status.social_status:
                status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            'total_characters': total_characters,
            'total_relationships': total_relationships,
            'total_abilities': total_abilities,
            'status_distribution': status_counts,
            'characters_with_abilities': sum(1 for char in self.characters.values() if char.abilities),
            'characters_with_relationships': sum(1 for char in self.characters.values() if char.relationships)
        }