#!/usr/bin/env python3
"""
Response Parser for Infinity Mage Translation
Parses Claude CLI structured responses, extracts markdown, and processes new terms
"""

import re
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from infinity_glossary_manager import InfinityGlossaryManager

class InfinityResponseParser:
    def __init__(self, glossary_manager: InfinityGlossaryManager, 
                 output_dir: str = "translated_chapters"):
        self.glossary_manager = glossary_manager
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Response parsing patterns
        self.translation_pattern = r'TRANSLATION_START\s*\n(.*?)\nTRANSLATION_END'
        self.new_terms_pattern = r'NEW_TERMS_DISCOVERED:\s*\n(.*?)(?:\n\n|\nCONSISTENCY_CHECK:|\Z)'
        self.consistency_pattern = r'CONSISTENCY_CHECK:\s*\n(.*?)(?:\n\n|\Z)'
        
    def parse_claude_response(self, response_text: str, chapter_number: int, 
                            korean_original: str = "") -> Dict:
        """Parse complete Claude response and extract all components"""
        
        result = {
            'success': False,
            'chapter_data': None,
            'new_terms': {},
            'consistency_notes': [],
            'errors': [],
            'warnings': []
        }
        
        try:
            # Extract translation content
            translation_data = self._extract_translation(response_text)
            if translation_data['success']:
                result['chapter_data'] = translation_data
                result['success'] = True
            else:
                result['errors'].extend(translation_data['errors'])
            
            # Extract new terms
            new_terms = self._extract_new_terms(response_text)
            result['new_terms'] = new_terms['terms']
            if new_terms['warnings']:
                result['warnings'].extend(new_terms['warnings'])
            
            # Extract consistency notes
            consistency_notes = self._extract_consistency_notes(response_text)
            result['consistency_notes'] = consistency_notes
            
            # Validate translation quality
            if result['success'] and korean_original:
                validation_issues = self._validate_translation_quality(
                    translation_data['content'], korean_original, chapter_number)
                if validation_issues:
                    # Separate critical issues from warnings
                    critical_issues = [issue for issue in validation_issues if issue.startswith('CRITICAL:')]
                    warning_issues = [issue for issue in validation_issues if not issue.startswith('CRITICAL:')]
                    
                    if critical_issues:
                        # Critical issues cause parsing failure
                        result['success'] = False
                        result['errors'].extend(critical_issues)
                        result['warnings'].extend(warning_issues)
                    else:
                        result['warnings'].extend(validation_issues)
            
        except Exception as e:
            result['errors'].append(f"Response parsing error: {str(e)}")
            result['success'] = False
        
        return result
    
    def _extract_translation(self, response_text: str) -> Dict:
        """Extract and parse the translation markdown content"""
        
        result = {
            'success': False,
            'title': '',
            'date': '',
            'content': '',
            'raw_markdown': '',
            'errors': []
        }
        
        # Find translation section
        translation_match = re.search(self.translation_pattern, response_text, re.DOTALL)
        if len(response_text) < 1000:
            result['errors'].append("Response too short to contain valid translation")
            return result
        if not translation_match:
            result['errors'].append("No TRANSLATION_START/TRANSLATION_END section found")
            return result
        
        raw_markdown = translation_match.group(1).strip()
        result['raw_markdown'] = raw_markdown
        
        # Parse markdown frontmatter
        frontmatter_pattern = r'^---\s*\n(.*?)\n---\s*\n(.*?)(?:\n---\s*$|$)'
        frontmatter_match = re.search(frontmatter_pattern, raw_markdown, re.DOTALL)
        
        if frontmatter_match:
            # Parse frontmatter
            frontmatter = frontmatter_match.group(1)
            content = frontmatter_match.group(2).strip()
            
            # Extract title and date from frontmatter
            title_match = re.search(r'title:\s*(.+)', frontmatter)
            date_match = re.search(r'date:\s*(.+)', frontmatter)
            
            result['title'] = title_match.group(1).strip() if title_match else 'Untitled'
            result['date'] = date_match.group(1).strip() if date_match else datetime.now().strftime('%Y-%m-%d')
            result['content'] = content
            result['success'] = True
            
        else:
            # Try to extract without proper frontmatter
            result['errors'].append("Markdown frontmatter not properly formatted")
            
            # Look for title in first few lines
            lines = raw_markdown.split('\n')
            potential_title = ""
            content_start = 0
            
            for i, line in enumerate(lines[:10]):  # Check first 10 lines
                line = line.strip()
                if line and not line.startswith('#') and len(line) < 100:
                    potential_title = line
                    content_start = i + 1
                    break
            
            result['title'] = potential_title or 'Untitled'
            result['date'] = datetime.now().strftime('%Y-%m-%d')
            result['content'] = '\n'.join(lines[content_start:]) if content_start > 0 else raw_markdown
            result['success'] = True  # Accept with warnings
        
        return result
    
    def _extract_new_terms(self, response_text: str) -> Dict:
        """Extract and parse new terms discovered by Claude"""
        
        result = {
            'terms': {
                'characters': {},
                'places': {},
                'magic_terms': {},
                'organizations': {},
                'items': {},
                'concepts': {}
            },
            'warnings': []
        }
        
        # Find new terms section
        terms_match = re.search(self.new_terms_pattern, response_text, re.DOTALL)
        if not terms_match:
            result['warnings'].append("No NEW_TERMS_DISCOVERED section found")
            return result
        
        terms_text = terms_match.group(1).strip()
        
        # Parse term entries
        # Expected format: korean_term → english_translation (category: type) {context}
        term_patterns = [
            r'[-*]\s*([^→]+)→\s*([^(]+)\s*\(category:\s*([^)]+)\)\s*(?:\{([^}]+)\})?',
            r'[-*]\s*([^→]+)→\s*([^(]+)\s*\(([^)]+)\)\s*(?:\{([^}]+)\})?',
            r'([^→]+)→\s*([^(]+)\s*\(category:\s*([^)]+)\)\s*(?:\{([^}]+)\})?'
        ]
        
        for line in terms_text.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            term_parsed = False
            for pattern in term_patterns:
                match = re.search(pattern, line)
                if match:
                    korean = match.group(1).strip()
                    english = match.group(2).strip()
                    category_raw = match.group(3).strip().lower()
                    context = match.group(4).strip() if len(match.groups()) >= 4 and match.group(4) else ""
                    
                    # Extract category and additional info (e.g., "character: female" -> "character", "female")
                    category_parts = category_raw.split(':')
                    category = category_parts[0].strip()
                    additional_info = category_parts[1].strip() if len(category_parts) > 1 else ""
                    
                    # Normalize category names
                    category_mapping = {
                        'character': 'characters',
                        'person': 'characters',
                        'people': 'characters',
                        'place': 'places',
                        'location': 'places',
                        'area': 'places',
                        'magic': 'magic_terms',
                        'magic_term': 'magic_terms',
                        'spell': 'magic_terms',
                        'technique': 'magic_terms',
                        'organization': 'organizations',
                        'org': 'organizations',
                        'family': 'organizations',
                        'gang': 'organizations',
                        'item': 'items',
                        'weapon': 'items',
                        'tool': 'items',
                        'concept': 'concepts'
                    }
                    
                    normalized_category = category_mapping.get(category, category)
                    if normalized_category not in result['terms']:
                        # Smart categorization based on context clues (order matters!)
                        if self._detect_organization_context(english, context):
                            normalized_category = 'organizations'
                        elif self._detect_magic_context(english, context):
                            normalized_category = 'magic_terms'
                        elif self._detect_place_context(english, context):
                            normalized_category = 'places'
                        elif self._detect_item_context(english, context):
                            normalized_category = 'items'
                        elif self._detect_character_context(english, context):
                            normalized_category = 'characters'
                        else:
                            normalized_category = 'concepts'  # Final fallback
                    
                    # Prepare term data
                    term_data = {
                        'english': english,
                        'context': context
                    }
                    
                    # Add gender information for characters
                    if normalized_category == 'characters' and additional_info:
                        # Check if additional_info is a gender (male/female/boy/girl/man/woman)
                        gender_mapping = {
                            'male': 'male', 'female': 'female',
                            'boy': 'male', 'girl': 'female', 
                            'man': 'male', 'woman': 'female'
                        }
                        if additional_info.lower() in gender_mapping:
                            term_data['gender'] = gender_mapping[additional_info.lower()]
                    
                    result['terms'][normalized_category][korean] = term_data
                    
                    term_parsed = True
                    break
            
            if not term_parsed and line:
                result['warnings'].append(f"Could not parse term entry: {line}")
        
        return result
    
    def _detect_character_context(self, english: str, context: str) -> bool:
        """Detect if a term should be categorized as a character"""
        # Strong character indicators (definitive)
        strong_character_indicators = [
            'male', 'female', 'boy', 'girl', 'man', 'woman', 'person', 'character',
            'father', 'mother', 'son', 'daughter', 'brother', 'sister',
            'king', 'queen', 'prince', 'princess', 'lord', 'lady', 
            'teacher', 'student', 'mage', 'wizard', 'principal', 'director',
            'he', 'she', 'his', 'her', 'him', 'protagonist', 'villain',
            'retired from politics', 'daughter of', 'son of'
        ]
        
        # Check context for strong character indicators
        context_lower = context.lower()
        
        for indicator in strong_character_indicators:
            if indicator in context_lower:
                return True
        
        # Check if it has gender markers (very strong indicator)
        gender_patterns = [r'\b(male|female)\b', r'\b(he|she)\b', r'\b(boy|girl)\b']
        for pattern in gender_patterns:
            if re.search(pattern, context_lower):
                return True
        
        # Check if it's a person's name pattern (but be conservative)
        if english and english[0].isupper():
            name_words = english.split()
            if len(name_words) <= 2:  # Most names are 1-2 words
                # Look for context clues that suggest it's a person
                person_context_clues = ['from', 'of', 'the', "'s", 'who', 'is', 'was']
                if any(clue in context_lower for clue in person_context_clues):
                    # But not if it's clearly an organization
                    org_blockers = ['family', 'house', 'clan', 'guild', 'school', 'academy']
                    if not any(blocker in context_lower for blocker in org_blockers):
                        return True
        
        return False
    
    def _detect_place_context(self, english: str, context: str) -> bool:
        """Detect if a term should be categorized as a place"""
        place_indicators = [
            'city', 'town', 'village', 'district', 'area', 'region', 'place', 'location',
            'school', 'academy', 'library', 'building', 'house', 'palace', 'castle',
            'kingdom', 'empire', 'nation', 'country', 'forest', 'mountain', 'valley',
            'street', 'alley', 'road', 'path', 'gate', 'door', 'room', 'hall'
        ]
        
        context_lower = context.lower()
        english_lower = english.lower()
        
        for indicator in place_indicators:
            if indicator in context_lower or indicator in english_lower:
                return True
        
        return False
    
    def _detect_magic_context(self, english: str, context: str) -> bool:
        """Detect if a term should be categorized as magic"""
        magic_indicators = [
            'magic', 'spell', 'technique', 'skill', 'ability', 'power',
            'cast', 'conjure', 'summon', 'enchant', 'ritual', 'incantation',
            'mana', 'energy', 'force', 'element', 'elemental',
            'fire', 'water', 'earth', 'air', 'wind', 'lightning', 'ice', 'light', 'dark'
        ]
        
        context_lower = context.lower()
        english_lower = english.lower()
        
        for indicator in magic_indicators:
            if indicator in context_lower or indicator in english_lower:
                return True
        
        return False
    
    def _detect_organization_context(self, english: str, context: str) -> bool:
        """Detect if a term should be categorized as organization"""
        org_indicators = [
            'family', 'house', 'clan', 'tribe', 'gang', 'group', 'organization',
            'guild', 'order', 'society', 'association', 'company', 'faction',
            'nobility', 'royal', 'government', 'kingdom', 'empire', 'military',
            'school', 'academy', 'institution'
        ]
        
        context_lower = context.lower()
        english_lower = english.lower()
        
        for indicator in org_indicators:
            if indicator in context_lower or indicator in english_lower:
                return True
        
        return False
    
    def _detect_item_context(self, english: str, context: str) -> bool:
        """Detect if a term should be categorized as item"""
        item_indicators = [
            'weapon', 'sword', 'knife', 'blade', 'axe', 'bow', 'staff', 'wand',
            'armor', 'shield', 'helmet', 'boots', 'gloves', 'cloak', 'robe',
            'potion', 'scroll', 'book', 'tome', 'artifact', 'relic', 'treasure',
            'tool', 'instrument', 'device', 'object', 'item', 'equipment'
        ]
        
        context_lower = context.lower()
        english_lower = english.lower()
        
        for indicator in item_indicators:
            if indicator in context_lower or indicator in english_lower:
                return True
        
        return False
    
    def _extract_consistency_notes(self, response_text: str) -> List[str]:
        """Extract consistency check notes from Claude's response"""
        
        consistency_match = re.search(self.consistency_pattern, response_text, re.DOTALL)
        if not consistency_match:
            return ["No consistency check notes provided"]
        
        notes_text = consistency_match.group(1).strip()
        notes = []
        
        for line in notes_text.split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                # Remove bullet points and format
                line = re.sub(r'^[-*]\s*', '', line)
                notes.append(line)
        
        return notes
    
    def _validate_translation_quality(self, translation: str, korean_original: str, 
                                    chapter_number: int) -> List[str]:
        """Validate translation quality and consistency"""
        
        issues = []
        
        # Check for untranslated Korean text
        korean_chars = re.findall(r'[가-힣]+', translation)
        if korean_chars:
            issues.append(f"Found untranslated Korean text: {', '.join(korean_chars[:5])}")
        
        # Check for placeholder text (critical failure indicators)
        critical_placeholders = [
            r'\[English chapter title here\]',
            r'\[Your excellent English translation here.*?\]',
            r'\[.*?chapter title.*?\]',
            r'\[.*?translation.*?here.*?\]'
        ]
        
        placeholder_matches = re.findall(r'\[.*?\]|\{.*?\}|TODO|PLACEHOLDER|XXX', translation, re.IGNORECASE)
        critical_matches = []
        
        for pattern in critical_placeholders:
            match = re.search(pattern, translation, re.IGNORECASE)
            if match:
                placeholder_text = match.group(0)
                if placeholder_text not in critical_matches:  # Avoid duplicates
                    critical_matches.append(placeholder_text)
        
        if critical_matches:
            issues.append(f"CRITICAL: Translation contains unprocessed placeholders: {', '.join(critical_matches[:3])}")
        elif placeholder_matches:
            issues.append(f"Found placeholder text: {', '.join(placeholder_matches[:3])}")
        
        # Check for minimal/empty content
        content_words = len([word for word in translation.split() if word.strip() and not word.startswith('[')])
        if content_words < 5:
            issues.append("CRITICAL: Translation appears to be empty or contains minimal content")
        
        # Check length reasonableness (translation should be similar length to original)
        korean_length = len(korean_original.strip())
        translation_length = len(translation.strip())
        
        if translation_length < korean_length * 0.5:
            issues.append("Translation appears too short compared to original")
        elif translation_length > korean_length * 3:
            issues.append("Translation appears too long compared to original")
        
        # Use glossary manager for consistency validation
        glossary_issues = self.glossary_manager.validate_consistency(
            translation, self.glossary_manager.generate_sub_glossary("", chapter_number))
        issues.extend(glossary_issues)
        
        return issues
    
    def save_chapter(self, chapter_data: Dict, chapter_number: int, 
                    volume_number: Optional[int] = None) -> str:
        """Save chapter as markdown file with proper formatting"""
        
        # Generate filename
        if volume_number:
            filename = f"chapter_{chapter_number:04d}.md"
        else:
            filename = f"chapter_{chapter_number:04d}.md"
        
        filepath = self.output_dir / filename
        
        # Create final markdown content
        markdown_content = f"""---
title: {chapter_data['title']}
date: {chapter_data['date']}
---

{chapter_data['content']}

---
"""
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            return str(filepath)
            
        except Exception as e:
            raise Exception(f"Error saving chapter to {filepath}: {str(e)}")
    
    def update_glossary_from_response(self, korean_original: str, new_terms: Dict, 
                                    chapter_number: int, translation_content: str):
        """Update glossary with new terms from translation response"""
        
        # Process new terms
        discovered_terms = {}
        for category, terms in new_terms.items():
            if terms:  # Only process categories with terms
                discovered_terms[category] = {}
                for korean, data in terms.items():
                    discovered_terms[category][korean] = data['english']
        
        # Update glossary through manager
        self.glossary_manager.update_from_translation(
            korean_original, translation_content, discovered_terms, chapter_number)
    
    def process_complete_response(self, response_text: str, korean_original: str, 
                                chapter_number: int, volume_number: Optional[int] = None) -> Dict:
        """Complete processing of Claude response: parse, save, update glossary"""
        
        print(f"🔄 Processing Chapter {chapter_number} response...")
        
        # Parse response
        parsed_result = self.parse_claude_response(response_text, chapter_number, korean_original)
        
        if not parsed_result['success']:
            return {
                'success': False,
                'errors': parsed_result['errors'],
                'warnings': parsed_result['warnings']
            }
        
        try:
            # Save chapter
            filepath = self.save_chapter(parsed_result['chapter_data'], chapter_number, volume_number)
            print(f"✅ Chapter saved to: {filepath}")
            
            # Update glossary
            self.update_glossary_from_response(
                korean_original, 
                parsed_result['new_terms'], 
                chapter_number, 
                parsed_result['chapter_data']['content']
            )
            print(f"📖 Glossary updated with new terms from Chapter {chapter_number}")
            
            # Generate processing report
            report = {
                'success': True,
                'chapter_file': filepath,
                'title': parsed_result['chapter_data']['title'],
                'new_terms_count': sum(len(terms) for terms in parsed_result['new_terms'].values()),
                'consistency_notes': parsed_result['consistency_notes'],
                'warnings': parsed_result['warnings'],
                'errors': []
            }
            
            print(f"🎉 Chapter {chapter_number} processing complete!")
            if report['new_terms_count'] > 0:
                print(f"📝 Added {report['new_terms_count']} new terms to glossary")
            if report['warnings']:
                print(f"⚠️ {len(report['warnings'])} warnings generated")
            
            return report
            
        except Exception as e:
            return {
                'success': False,
                'errors': [f"Processing error: {str(e)}"],
                'warnings': parsed_result['warnings']
            }
    
    def create_processing_report(self, results: List[Dict]) -> str:
        """Create a comprehensive processing report"""
        
        report_lines = [
            "# Infinity Mage Translation Processing Report",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            ""
        ]
        
        successful_chapters = [r for r in results if r['success']]
        failed_chapters = [r for r in results if not r['success']]
        
        report_lines.extend([
            f"## Summary",
            f"- **Total Chapters**: {len(results)}",
            f"- **Successful**: {len(successful_chapters)}",
            f"- **Failed**: {len(failed_chapters)}",
            f"- **Total New Terms**: {sum(r.get('new_terms_count', 0) for r in successful_chapters)}",
            ""
        ])
        
        if successful_chapters:
            report_lines.append("## Successful Chapters")
            for result in successful_chapters:
                report_lines.append(f"- **{result.get('title', 'Unknown')}** - {result.get('new_terms_count', 0)} new terms")
            report_lines.append("")
        
        if failed_chapters:
            report_lines.append("## Failed Chapters")
            for result in failed_chapters:
                report_lines.append(f"- Chapter processing failed:")
                for error in result['errors']:
                    report_lines.append(f"  - {error}")
            report_lines.append("")
        
        # Warnings summary
        all_warnings = []
        for result in results:
            all_warnings.extend(result.get('warnings', []))
        
        if all_warnings:
            report_lines.append("## Warnings")
            for warning in set(all_warnings):  # Remove duplicates
                report_lines.append(f"- {warning}")
        
        return '\n'.join(report_lines)

def main():
    """Test the response parser"""
    
    # Initialize components
    glossary_manager = InfinityGlossaryManager()
    parser = InfinityResponseParser(glossary_manager)
    
    # Test response
    test_response = """
TRANSLATION_START
---
title: Meeting Magic (1)
date: 2024-01-01
---

Shirone was studying magic at Alpheas Magic School. He was a boy with genius-level talent, but he had not yet realized his true power.

"Shirone, let's try creating a photon sphere in today's lesson," the teacher said.

Shirone concentrated and cast his magic. A glowing orb appeared from his hands.

---
TRANSLATION_END

NEW_TERMS_DISCOVERED:
- 광구 → photon sphere (category: magic_term) {A basic light magic spell}
- 시전 → cast (category: magic_term) {The act of using magic}

CONSISTENCY_CHECK:
- Verified all character names from glossary
- Maintained gender consistency for all characters
- Used established magic terminology
"""
    
    korean_original = """시로네는 알페아스 마법학교에서 마법을 배우고 있었다. 그는 천재적인 재능을 가진 소년이었지만, 아직 자신의 진정한 힘을 깨닫지 못했다.

"시로네, 오늘 수업에서 광구를 만들어보자." 선생님이 말했다.

시로네는 집중하며 마법을 시전했다. 그의 손에서 빛나는 구체가 나타났다."""
    
    # Test processing
    result = parser.process_complete_response(test_response, korean_original, 1, 1)
    
    print("\n" + "="*50)
    print("PROCESSING RESULT:")
    print("="*50)
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()