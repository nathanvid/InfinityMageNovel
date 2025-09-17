#!/usr/bin/env python3
"""
Enhanced Glossary Manager for Infinity Mage Translation
Manages master glossary with smart sub-glossary generation for context-aware translation
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from collections import defaultdict, Counter

class InfinityGlossaryManager:
    def __init__(self, glossary_path: str = None):
        # Default to data/glossaries structure
        if glossary_path is None:
            # Get the project root (parent of scripts directory)
            project_root = Path(__file__).parent.parent
            glossary_path = project_root / "data" / "glossaries" / "translation_glossary.json"

        self.glossary_path = Path(glossary_path)
        # Ensure the directory exists
        self.glossary_path.parent.mkdir(parents=True, exist_ok=True)

        self.glossary = self.load_glossary()
        self.chapter_history = []  # Track last 10 chapters
        
    def load_glossary(self) -> Dict:
        """Load the master glossary with enhanced metadata"""
        try:
            if self.glossary_path.exists():
                with open(self.glossary_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # Ensure proper structure with metadata
                if 'metadata' not in data:
                    data['metadata'] = {
                        'version': '2.0',
                        'last_updated': datetime.now().isoformat(),
                        'total_chapters_processed': 0,
                        'statistics': {}
                    }
                
                # Ensure all term categories exist
                for category in ['characters', 'places', 'magic_terms', 'organizations', 'items', 'concepts']:
                    if category not in data:
                        data[category] = {}
                
                return data
        except Exception as e:
            print(f"Warning: Could not load glossary: {e}")
        
        # Create new glossary structure
        return {
            'metadata': {
                'version': '2.0',
                'created': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat(),
                'total_chapters_processed': 0,
                'statistics': {}
            },
            'characters': {},
            'places': {},
            'magic_terms': {},
            'organizations': {},
            'items': {},
            'concepts': {}
        }
    
    def save_glossary(self):
        """Save the master glossary with updated metadata"""
        self.glossary['metadata']['last_updated'] = datetime.now().isoformat()
        
        try:
            with open(self.glossary_path, 'w', encoding='utf-8') as f:
                json.dump(self.glossary, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving glossary: {e}")
    
    def add_term(self, korean: str, english: str, category: str, chapter_num: int, 
                 context: str = "", gender: str = "", relationships: List[str] = None):
        """Add a new term to the glossary with enhanced metadata"""
        if category not in self.glossary:
            self.glossary[category] = {}
        
        term_data = {
            'english': english,
            'category': category,
            'first_appearance': chapter_num,
            'usage_count': 1,
            'chapters_used': [chapter_num],
            'last_used': chapter_num,
            'context': context,
            'added_date': datetime.now().isoformat()
        }
        
        # Add character-specific fields
        if category == 'characters':
            # Extract name and surname from English translation
            english_parts = english.split()
            name = english_parts[0] if english_parts else english
            surname = ' '.join(english_parts[1:]) if len(english_parts) > 1 else ''
            
            term_data.update({
                'name': name,
                'surname': surname,
                'korean_name': '',  # Korean characters for given name
                'korean_family_name': '',  # Korean characters for family name  
                'korean_full_name': korean,  # Full Korean name as provided
                'english_full_name': english,  # Full English name
                'gender': gender.lower() if gender else 'unknown',
                'relationships': relationships or [],
                'aliases': [],
                'titles': []
            })
        
        # Add place-specific fields
        if category == 'places':
            term_data.update({
                'type': 'unknown',  # city, kingdom, dungeon, etc.
                'parent_location': '',
                'description': context
            })
        
        # Add magic-specific fields
        if category == 'magic_terms':
            term_data.update({
                'type': 'unknown',  # spell, technique, concept, etc.
                'element': '',
                'tier': 'unknown',
                'description': context
            })
        
        self.glossary[category][korean] = term_data
        self.update_statistics()
        
    def update_term_usage(self, korean: str, category: str, chapter_num: int):
        """Update usage statistics for an existing term"""
        if category in self.glossary and korean in self.glossary[category]:
            term = self.glossary[category][korean]
            term['usage_count'] += 1
            term['last_used'] = chapter_num
            
            if chapter_num not in term['chapters_used']:
                term['chapters_used'].append(chapter_num)
                term['chapters_used'].sort()
    
    def analyze_chapter_content(self, korean_text: str) -> Dict[str, Set[str]]:
        """Analyze chapter content to find existing terms"""
        found_terms = {
            'characters': set(),
            'places': set(),
            'magic_terms': set(),
            'organizations': set(),
            'items': set(),
            'concepts': set()
        }
        
        # Search for existing terms in the chapter text
        for category in found_terms.keys():
            if category in self.glossary:
                for korean_term, term_data in self.glossary[category].items():
                    # Check for exact match first
                    if korean_term in korean_text:
                        found_terms[category].add(korean_term)
                    # For characters, also check individual name parts
                    elif category == 'characters':
                        korean_given = term_data.get('korean_name', '')
                        korean_family = term_data.get('korean_family_name', '')
                        
                        # Check if given name appears in text
                        if korean_given and korean_given in korean_text:
                            found_terms[category].add(korean_term)
                        # Check if family name appears in text  
                        elif korean_family and korean_family in korean_text:
                            found_terms[category].add(korean_term)
        
        return found_terms
    
    def get_context_terms(self, current_chapter: int, chapters_back: int = 10) -> Dict[str, Dict]:
        """Get terms that appeared in the last N chapters for context"""
        context_terms = {
            'characters': {},
            'places': {},
            'magic_terms': {},
            'organizations': {},
            'items': {},
            'concepts': {}
        }
        
        min_chapter = max(1, current_chapter - chapters_back)
        
        for category in context_terms.keys():
            if category in self.glossary:
                for korean_term, data in self.glossary[category].items():
                    # Include if term was used in the context window
                    if any(min_chapter <= chapter <= current_chapter 
                           for chapter in data.get('chapters_used', [])):
                        context_terms[category][korean_term] = data
        
        return context_terms
    
    def generate_sub_glossary(self, korean_text: str, current_chapter: int, 
                            max_terms_per_category: int = 15) -> Dict[str, Dict]:
        """Generate smart sub-glossary for current chapter + context"""
        
        # Find terms in current chapter
        chapter_terms = self.analyze_chapter_content(korean_text)
        
        # Get context terms from last 10 chapters
        context_terms = self.get_context_terms(current_chapter, 10)
        
        # Create prioritized sub-glossary
        sub_glossary = {
            'characters': {},
            'places': {},
            'magic_terms': {},
            'organizations': {},
            'items': {},
            'concepts': {}
        }
        
        for category in sub_glossary.keys():
            # Priority 1: Terms found in current chapter
            priority_terms = []
            for term in chapter_terms[category]:
                if term in context_terms[category]:
                    priority_terms.append((term, context_terms[category][term], 3))
            
            # Priority 2: High usage terms from context
            for term, data in context_terms[category].items():
                if term not in chapter_terms[category]:
                    usage_score = min(data.get('usage_count', 1) / 10.0, 2.0)
                    recency_score = 1.0 if data.get('last_used', 0) >= current_chapter - 3 else 0.5
                    priority_terms.append((term, data, usage_score + recency_score))
            
            # Sort by priority and limit
            priority_terms.sort(key=lambda x: x[2], reverse=True)
            
            for term, data, _ in priority_terms[:max_terms_per_category]:
                sub_glossary[category][term] = {
                    'english': data['english'],
                    'context': data.get('context', ''),
                    'usage_count': data.get('usage_count', 1)
                }
                
                # Add category-specific info
                if category == 'characters':
                    sub_glossary[category][term]['gender'] = data.get('gender', 'unknown')
                    sub_glossary[category][term]['relationships'] = data.get('relationships', [])
        
        return sub_glossary
    
    def validate_consistency(self, translation_text: str, sub_glossary: Dict) -> List[str]:
        """Validate translation consistency against glossary"""
        issues = []
        
        # Check character names and gender consistency
        for korean_name, data in sub_glossary.get('characters', {}).items():
            english_name = data['english']
            gender = data.get('gender', 'unknown')
            
            if english_name.lower() in translation_text.lower():
                # Check for gender consistency
                if gender == 'male':
                    if re.search(rf'\b{re.escape(english_name)}\b.*?\b(she|her|hers)\b', 
                               translation_text, re.IGNORECASE):
                        issues.append(f"Gender inconsistency: {english_name} (male) referred to as 'she/her'")
                elif gender == 'female':
                    if re.search(rf'\b{re.escape(english_name)}\b.*?\b(he|him|his)\b', 
                               translation_text, re.IGNORECASE):
                        issues.append(f"Gender inconsistency: {english_name} (female) referred to as 'he/him'")
        
        return issues
    
    def update_from_translation(self, korean_text: str, translation_text: str, 
                              discovered_terms: Dict, current_chapter: int):
        """Update glossary based on translation results"""
        
        # Update usage for existing terms
        chapter_terms = self.analyze_chapter_content(korean_text)
        for category, terms in chapter_terms.items():
            for term in terms:
                self.update_term_usage(term, category, current_chapter)
        
        # Add new discovered terms and update existing ones with additional metadata
        for category, terms in discovered_terms.items():
            for korean_term, term_data in terms.items():
                # Handle both string and dict formats for backward compatibility
                if isinstance(term_data, str):
                    english_translation = term_data
                    context = f"Discovered in Chapter {current_chapter}"
                    gender = ""
                else:
                    english_translation = term_data.get('english', '')
                    context = term_data.get('context', f"Discovered in Chapter {current_chapter}")
                    gender = term_data.get('gender', '')
                
                # Check if term already exists
                if category not in self.glossary or korean_term not in self.glossary[category]:
                    # Add new term
                    self.add_term(korean_term, english_translation, category, 
                                current_chapter, context, gender)
                else:
                    # Update existing term with new metadata if available
                    existing_term = self.glossary[category][korean_term]
                    
                    # Update gender if it was unknown and we now have information
                    if gender and existing_term.get('gender', '') in ['', 'unknown']:
                        existing_term['gender'] = gender
                        print(f"Updated gender for {korean_term} ({existing_term['english']}) to {gender}")
                    
                    # Update other metadata as needed
                    if context and 'Discovered in Chapter' in context:
                        # Don't overwrite existing context with generic "Discovered" message
                        pass
                    elif context and existing_term.get('context', '') == f"Discovered in Chapter {existing_term.get('first_appearance', 'unknown')}":
                        # Replace generic context with more specific one
                        existing_term['context'] = context
        
        # Update metadata
        self.glossary['metadata']['total_chapters_processed'] = max(
            self.glossary['metadata']['total_chapters_processed'], current_chapter)
        
        self.update_statistics()
        self.save_glossary()
    
    def update_statistics(self):
        """Update glossary statistics"""
        stats = {
            'total_terms': 0,
            'terms_by_category': {},
            'most_used_terms': {},
            'recent_additions': []
        }
        
        for category in ['characters', 'places', 'magic_terms', 'organizations', 'items', 'concepts']:
            if category in self.glossary:
                count = len(self.glossary[category])
                stats['terms_by_category'][category] = count
                stats['total_terms'] += count
                
                # Get most used terms in this category
                if self.glossary[category]:
                    most_used = max(self.glossary[category].items(), 
                                  key=lambda x: x[1].get('usage_count', 0))
                    stats['most_used_terms'][category] = {
                        'term': most_used[0],
                        'english': most_used[1]['english'],
                        'usage_count': most_used[1].get('usage_count', 0)
                    }
        
        self.glossary['metadata']['statistics'] = stats
    
    def get_statistics(self) -> Dict:
        """Get current glossary statistics"""
        return self.glossary['metadata'].get('statistics', {})
    
    def export_readable_glossary(self, output_path: str = None):
        """Export a human-readable markdown glossary"""
        if output_path is None:
            # Default to data/glossaries structure
            project_root = Path(__file__).parent.parent
            output_path = project_root / "data" / "glossaries" / "readable_glossary.md"
        output_path = Path(output_path)
        # Ensure the directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        lines = [
            "# Infinity Mage Translation Glossary",
            f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n",
            f"**Total Terms**: {self.get_statistics().get('total_terms', 0)}",
            f"**Chapters Processed**: {self.glossary['metadata']['total_chapters_processed']}\n"
        ]
        
        for category in ['characters', 'places', 'magic_terms', 'organizations', 'items', 'concepts']:
            if category in self.glossary and self.glossary[category]:
                lines.append(f"## {category.replace('_', ' ').title()}")
                lines.append("")
                
                # Sort by usage count
                sorted_terms = sorted(
                    self.glossary[category].items(),
                    key=lambda x: x[1].get('usage_count', 0),
                    reverse=True
                )
                
                for korean, data in sorted_terms:
                    english = data['english']
                    usage = data.get('usage_count', 1)
                    first_chap = data.get('first_appearance', 'Unknown')
                    
                    line = f"- **{korean}** → {english} *(Used {usage}x, First: Ch.{first_chap})*"
                    
                    if category == 'characters' and data.get('gender'):
                        line += f" *[{data['gender']}]*"
                    
                    lines.append(line)
                
                lines.append("")
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            print(f"✅ Readable glossary exported to: {output_path}")
        except Exception as e:
            print(f"❌ Error exporting readable glossary: {e}")

    def update_character_name(self, korean_full_name: str, name: str = None, surname: str = None, 
                             korean_name: str = None, korean_family_name: str = None):
        """Update name components for a character
        
        Args:
            korean_full_name: The Korean key to look up (e.g., '아리안 시로네' or '시로네')
            name: English given name (e.g., 'Shirone')
            surname: English family name (e.g., 'Arian') 
            korean_name: Korean given name characters (e.g., '시로네')
            korean_family_name: Korean family name characters (e.g., '아리안')
        """
        if korean_full_name not in self.glossary.get('characters', {}):
            print(f"Character '{korean_full_name}' not found in glossary")
            return False
        
        character = self.glossary['characters'][korean_full_name]
        
        # Update English parts
        if name is not None:
            character['name'] = name
        if surname is not None:
            character['surname'] = surname
            
        # Update Korean parts
        if korean_name is not None:
            character['korean_name'] = korean_name
        if korean_family_name is not None:
            character['korean_family_name'] = korean_family_name
            
        # Update the English full name to match name + surname
        if character.get('name') and character.get('surname'):
            character['english'] = f"{character['surname']} {character['name']}"  # Western order
            character['english_full_name'] = f"{character['surname']} {character['name']}"
        elif character.get('name'):
            character['english'] = character['name']
            character['english_full_name'] = character['name']
            
        self.save_glossary()
        
        korean_parts = []
        if character.get('korean_family_name'):
            korean_parts.append(f"Family: {character['korean_family_name']}")
        if character.get('korean_name'):
            korean_parts.append(f"Given: {character['korean_name']}")
        
        english_parts = []
        if character.get('surname'):
            english_parts.append(f"Family: {character['surname']}")
        if character.get('name'):
            english_parts.append(f"Given: {character['name']}")
            
        print(f"Updated character '{korean_full_name}':")
        print(f"  Korean: {' | '.join(korean_parts) if korean_parts else 'N/A'}")  
        print(f"  English: {' | '.join(english_parts) if english_parts else 'N/A'}")
        return True

    def add_character_with_parts(self, korean_full_name: str, english_family_name: str, english_given_name: str,
                                korean_family_name: str, korean_given_name: str, chapter_num: int, 
                                context: str = "", gender: str = "", relationships: List[str] = None):
        """Add a character with separate Korean and English name parts"""
        
        english_full = f"{english_family_name} {english_given_name}" if english_family_name else english_given_name
        
        term_data = {
            'english': english_full,
            'name': english_given_name,
            'surname': english_family_name,
            'korean_name': korean_given_name,
            'korean_family_name': korean_family_name,
            'korean_full_name': korean_full_name,
            'english_full_name': english_full,
            'category': 'characters',
            'first_appearance': chapter_num,
            'usage_count': 1,
            'chapters_used': [chapter_num],
            'last_used': chapter_num,
            'context': context,
            'added_date': datetime.now().isoformat(),
            'gender': gender.lower() if gender else 'unknown',
            'relationships': relationships or [],
            'aliases': [],
            'titles': []
        }
        
        if 'characters' not in self.glossary:
            self.glossary['characters'] = {}
            
        self.glossary['characters'][korean_full_name] = term_data
        self.save_glossary()
        
        print(f"Added character:")
        print(f"  Korean: {korean_family_name} {korean_given_name} (Full: {korean_full_name})")
        print(f"  English: {english_family_name} {english_given_name}")
        return True

def main():
    """Test the glossary manager"""
    manager = InfinityGlossaryManager()
    
    # Test data
    korean_text = "시로네는 마법을 배우며 알페아스 마법학교에서 공부했다."
    
    # Add test terms
    manager.add_term("시로네", "Shirone", "characters", 1, "Main protagonist", "male")
    manager.add_term("알페아스 마법학교", "Alpheas Magic School", "places", 1, "Magic academy")
    
    # Generate sub-glossary
    sub_glossary = manager.generate_sub_glossary(korean_text, 1)
    
    print("Generated Sub-Glossary:")
    print(json.dumps(sub_glossary, ensure_ascii=False, indent=2))
    
    # Export readable version
    manager.export_readable_glossary()

if __name__ == "__main__":
    main()