#!/usr/bin/env python3
"""
Advanced Prompt Generator for Infinity Mage Translation
Creates context-aware prompts with dynamic sub-glossaries and quality instructions
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from infinity_glossary_manager import InfinityGlossaryManager

class InfinityPromptGenerator:
    def __init__(self, glossary_manager: InfinityGlossaryManager):
        self.glossary_manager = glossary_manager
        self.quality_instructions = self._load_quality_instructions()
        
    def _load_quality_instructions(self) -> Dict[str, str]:
        """Load comprehensive quality instructions for translation"""
        return {
            'consistency_rules': """
CRITICAL CONSISTENCY RULES:
1. **Names**: Use EXACT translations from the glossary. Never improvise or change established names.
2. **Gender**: Maintain perfect gender consistency for all characters throughout the translation.
3. **Locations**: Use established place names consistently. Cities, kingdoms, schools must match glossary.
4. **Magic Terms**: Preserve established magic terminology, spell names, and techniques exactly.
5. **Titles/Ranks**: Keep established titles and hierarchical terms consistent.
6. **Organizations**: Use consistent names for guilds, schools, governments, etc.
""",
            
            'translation_quality': """
TRANSLATION QUALITY REQUIREMENTS:
1. **Natural English**: Produce fluent, readable English that doesn't feel translated.
2. **Korean Honorifics**: Adapt honorifics naturally (님, 선배, etc.) into English context.
3. **Cultural Context**: Explain Korean-specific concepts when necessary with brief context.
4. **Dialogue Flow**: Make conversations feel natural in English while preserving character voice.
5. **Action Scenes**: Ensure fight scenes and magic descriptions are clear and exciting.
6. **Character Voice**: Maintain distinct speaking patterns for different characters.
""",
            
            'format_requirements': """
OUTPUT FORMAT REQUIREMENTS:
1. **Markdown Structure**: Use proper markdown formatting with metadata.
2. **Chapter Title**: Extract or create appropriate English chapter title.
3. **Content Flow**: Ensure smooth paragraph breaks and scene transitions.
4. **Dialogue Tags**: Use clear dialogue attribution in English style.
5. **Magic Descriptions**: Make spell casting and magic effects vivid and clear.
""",
            
            'discovery_instructions': """
NEW TERM DISCOVERY:
1. **Characters**: Any person mentioned - include gender, relationships, titles.
2. **Places**: Locations, buildings, geographical features, kingdoms, cities.
3. **Magic Terms**: Spells, techniques, magic concepts, magical items.
4. **Organizations**: Schools, guilds, governments, groups, factions.
5. **Items**: Weapons, artifacts, tools, equipment mentioned.
6. **Concepts**: Unique world-building concepts, systems, philosophies.

For each new term, determine:
- Korean original → English translation
- Category (character/place/magic_term/organization/item/concept)
- Context (brief explanation of what/who it is)
- For characters: gender (male/female/unknown)
"""
        }
    
    def _format_sub_glossary_for_prompt(self, sub_glossary: Dict[str, Dict]) -> str:
        """Format sub-glossary for inclusion in prompt"""
        lines = ["# GLOSSARY - USE THESE TRANSLATIONS EXACTLY"]
        lines.append("*Critical: Use these exact translations to maintain consistency*\n")
        
        for category, terms in sub_glossary.items():
            if terms:  # Only include categories with terms
                category_name = category.replace('_', ' ').title()
                lines.append(f"## {category_name}")
                
                for korean, data in terms.items():
                    english = data['english']
                    usage_count = data.get('usage_count', 1)
                    
                    line = f"- **{korean}** → {english}"
                    
                    # Add category-specific context
                    if category == 'characters':
                        # Add Korean name parts info
                        korean_family = data.get('korean_family_name', '')
                        korean_given = data.get('korean_name', '')
                        if korean_family and korean_given:
                            line += f" *(Korean parts: {korean_family}={data.get('surname', '')}, {korean_given}={data.get('name', '')})*"
                        elif korean_given and korean_given != korean:
                            line += f" *(Korean given: {korean_given})*"
                        
                        # Add English name parts if different from main
                        name = data.get('name', '')
                        surname = data.get('surname', '')
                        if name or surname:
                            name_info = f"{name} {surname}".strip()
                            if name_info != english and (name != english):
                                line += f" *(English: {name_info})*"
                        
                        gender = data.get('gender', 'unknown')
                        if gender != 'unknown':
                            line += f" *[{gender}]*"
                        relationships = data.get('relationships', [])
                        if relationships:
                            line += f" *(Relationships: {', '.join(relationships)})*"
                    
                    context = data.get('context', '')
                    if context and len(context) < 50:
                        line += f" *({context})*"
                    
                    lines.append(line)
                
                lines.append("")  # Empty line between categories
        
        return '\n'.join(lines)
    
    def _extract_chapter_title(self, korean_text: str) -> str:
        """Extract or generate chapter title from Korean text"""
        # Look for common chapter title patterns
        title_patterns = [
            r'제\s*(\d+)\s*장\s*[:-]\s*([^.\n]+)',  # 제1장 - Title
            r'Chapter\s*(\d+)\s*[:-]\s*([^.\n]+)',   # Chapter 1 - Title
            r'(\d+)\s*[.-]\s*([^.\n]+)',            # 1. Title
        ]
        
        for pattern in title_patterns:
            match = re.search(pattern, korean_text)
            if match:
                if len(match.groups()) >= 2:
                    return match.group(2).strip()
                
        # If no title found, extract first significant line
        lines = korean_text.strip().split('\n')
        for line in lines[:5]:  # Check first 5 lines
            line = line.strip()
            if line and len(line) < 100:  # Reasonable title length
                return line
        
        return "Untitled Chapter"
    
    def generate_translation_prompt(self, korean_text: str, chapter_number: int, 
                                  volume_number: Optional[int] = None) -> str:
        """Generate complete translation prompt with context and instructions"""
        
        # Generate smart sub-glossary
        sub_glossary = self.glossary_manager.generate_sub_glossary(korean_text, chapter_number)
        
        # Extract chapter title
        korean_title = self._extract_chapter_title(korean_text)
        
        # Get current date
        current_date = datetime.now().strftime('%Y-%m-%d')
        
        # Build the comprehensive prompt
        prompt_parts = [
            "# INFINITY MAGE TRANSLATION - PROFESSIONAL QUALITY REQUIRED",
            f"**Chapter**: {chapter_number}",
            f"**Volume**: {volume_number if volume_number else 'Unknown'}",
            f"**Date**: {current_date}",
            "",
            
            # Quality instructions
            self.quality_instructions['consistency_rules'],
            self.quality_instructions['translation_quality'],
            self.quality_instructions['format_requirements'],
            "",
            
            # Sub-glossary
            self._format_sub_glossary_for_prompt(sub_glossary),
            "",
            
            # Discovery instructions
            self.quality_instructions['discovery_instructions'],
            "",
            
            # Output format specification
            """# REQUIRED OUTPUT FORMAT
You MUST respond in this exact format:

```
TRANSLATION_START
---
title: [English chapter title here]
date: """ + current_date + """
---

[Your excellent English translation here, maintaining all consistency rules and quality requirements]

---
TRANSLATION_END

NEW_TERMS_DISCOVERED:
[List any new terms you encountered, format: korean_term → english_translation (category: character/place/magic_term/organization/item/concept) {context}]

CONSISTENCY_CHECK:
- Verified all character names from glossary
- Maintained gender consistency for all characters  
- Preserved established place names
- Used consistent magic terminology
- [Any other consistency notes]
```

""",
            
            # The Korean text to translate
            "# KOREAN TEXT TO TRANSLATE:",
            f"**Korean Chapter Title**: {korean_title}",
            "",
            "```korean",
            korean_text.strip(),
            "```",
            "",
            
            # Final instruction
            "**IMPORTANT**: Translate the above Korean text following ALL consistency rules and quality requirements. Use the glossary terms EXACTLY as provided. Respond in the specified format only."
        ]
        
        return '\n'.join(prompt_parts)
    
    def generate_batch_prompt(self, chapters_data: List[Dict]) -> str:
        """Generate prompt for batch translation of multiple chapters"""
        if not chapters_data:
            return "No chapters provided for batch translation."
        
        batch_prompt_parts = [
            "# INFINITY MAGE BATCH TRANSLATION",
            f"**Chapters**: {len(chapters_data)} chapters to translate",
            f"**Date**: {datetime.now().strftime('%Y-%m-%d')}",
            "",
            
            "**BATCH PROCESSING INSTRUCTIONS**:",
            "1. Translate each chapter individually following all quality rules",
            "2. Maintain consistency across all chapters in this batch", 
            "3. Use cumulative glossary knowledge (terms from earlier chapters apply to later ones)",
            "4. Respond with each chapter in the specified format, separated by '=== NEXT CHAPTER ==='",
            "",
        ]
        
        # Add consolidated glossary for all chapters
        all_terms = set()
        for chapter_data in chapters_data:
            chapter_num = chapter_data['chapter_number']
            korean_text = chapter_data['korean_text']
            
            # Get terms for this chapter
            sub_glossary = self.glossary_manager.generate_sub_glossary(korean_text, chapter_num)
            for category_terms in sub_glossary.values():
                all_terms.update(category_terms.keys())
        
        # Generate consolidated sub-glossary
        consolidated_glossary = {}
        for chapter_data in chapters_data:
            chapter_num = chapter_data['chapter_number']
            korean_text = chapter_data['korean_text']
            sub_glossary = self.glossary_manager.generate_sub_glossary(korean_text, chapter_num)
            
            for category, terms in sub_glossary.items():
                if category not in consolidated_glossary:
                    consolidated_glossary[category] = {}
                consolidated_glossary[category].update(terms)
        
        batch_prompt_parts.append(self._format_sub_glossary_for_prompt(consolidated_glossary))
        batch_prompt_parts.append("")
        
        # Add each chapter
        for i, chapter_data in enumerate(chapters_data, 1):
            batch_prompt_parts.extend([
                f"## CHAPTER {chapter_data['chapter_number']} TO TRANSLATE:",
                "",
                f"**Korean Title**: {self._extract_chapter_title(chapter_data['korean_text'])}",
                "",
                "```korean",
                chapter_data['korean_text'].strip(),
                "```",
                ""
            ])
            
            if i < len(chapters_data):
                batch_prompt_parts.append("=== NEXT CHAPTER INPUT ===")
                batch_prompt_parts.append("")
        
        batch_prompt_parts.extend([
            "",
            "**RESPOND WITH**: Each chapter translated in the specified format, separated by '=== NEXT CHAPTER ===' between translations."
        ])
        
        return '\n'.join(batch_prompt_parts)
    
    def generate_consistency_check_prompt(self, previous_translation: str, 
                                        current_korean: str, chapter_number: int) -> str:
        """Generate prompt for consistency checking against previous translations"""
        
        sub_glossary = self.glossary_manager.generate_sub_glossary(current_korean, chapter_number)
        
        return f"""# INFINITY MAGE CONSISTENCY CHECK

**Task**: Verify translation consistency between chapters
**Chapter**: {chapter_number}
**Date**: {datetime.now().strftime('%Y-%m-%d')}

## PREVIOUS TRANSLATION REFERENCE:
```
{previous_translation}
```

## CURRENT CHAPTER KOREAN TEXT:
```korean
{current_korean}
```

## GLOSSARY FOR CONSISTENCY:
{self._format_sub_glossary_for_prompt(sub_glossary)}

## CHECK FOR:
1. **Character Names**: Same Korean names → same English names
2. **Gender Consistency**: Male/female pronouns match established patterns
3. **Place Names**: Locations translated consistently
4. **Magic Terms**: Spell names and magic concepts consistent
5. **Relationships**: Character relationships and titles consistent

## RESPOND WITH:
- **CONSISTENCY_STATUS**: PASS/FAIL
- **ISSUES_FOUND**: [List any inconsistencies discovered]
- **RECOMMENDATIONS**: [Suggested corrections]
- **GLOSSARY_UPDATES**: [Any terms that need clarification]
"""
    
    def generate_review_prompt(self, translation: str, korean_original: str, 
                             chapter_number: int) -> str:
        """Generate prompt for translation quality review"""
        
        return f"""# INFINITY MAGE TRANSLATION REVIEW

**Chapter**: {chapter_number}
**Task**: Comprehensive quality review of translation
**Date**: {datetime.now().strftime('%Y-%m-%d')}

## ORIGINAL KOREAN:
```korean
{korean_original}
```

## TRANSLATION TO REVIEW:
```
{translation}
```

## REVIEW CRITERIA:
1. **Accuracy**: Does translation capture original meaning?
2. **Naturalness**: Does English flow naturally?
3. **Consistency**: Are terms consistent with established translations?
4. **Readability**: Is it enjoyable to read?
5. **Completeness**: Is anything missing or added?

## RESPOND WITH REVIEW:
- **OVERALL_QUALITY**: Excellent/Good/Fair/Poor
- **ACCURACY_SCORE**: 1-10
- **READABILITY_SCORE**: 1-10  
- **CONSISTENCY_SCORE**: 1-10
- **SPECIFIC_ISSUES**: [List problems found]
- **IMPROVEMENT_SUGGESTIONS**: [Specific recommendations]
- **HIGHLIGHT_EXCELLENT_PARTS**: [What was done particularly well]
"""

def main():
    """Test the prompt generator"""
    # Initialize with glossary manager
    glossary_manager = InfinityGlossaryManager()
    prompt_generator = InfinityPromptGenerator(glossary_manager)
    
    # Test Korean text
    test_korean = """제1장 - 마법을 만나다 (1)

시로네는 알페아스 마법학교에서 마법을 배우고 있었다. 그는 천재적인 재능을 가진 소년이었지만, 아직 자신의 진정한 힘을 깨닫지 못했다.

"시로네, 오늘 수업에서 광구를 만들어보자." 선생님이 말했다.

시로네는 집중하며 마법을 시전했다. 그의 손에서 빛나는 구체가 나타났다."""
    
    # Generate prompt
    prompt = prompt_generator.generate_translation_prompt(test_korean, 1, 1)
    
    # Save test prompt
    with open("test_prompt.txt", "w", encoding="utf-8") as f:
        f.write(prompt)
    
    print("✅ Test prompt generated and saved to 'test_prompt.txt'")
    print(f"Prompt length: {len(prompt)} characters")
    
    # Show a preview
    print("\n" + "="*50)
    print("PROMPT PREVIEW:")
    print("="*50)
    print(prompt[:1000] + "..." if len(prompt) > 1000 else prompt)

if __name__ == "__main__":
    main()