#!/usr/bin/env python3
"""
Manual Chapter Parser for Failed Responses
Takes Claude's response as input and manually extracts/saves chapter content
"""

import re
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple

# Add parent directory to path to import from other script modules
sys.path.append(str(Path(__file__).parent.parent))

from translation.infinity_response_parser import InfinityResponseParser
from infinity_glossary_manager import InfinityGlossaryManager

class ManualChapterParser:
    def __init__(self):
        self.glossary_manager = InfinityGlossaryManager()
        self.auto_parser = InfinityResponseParser(self.glossary_manager)
        self.output_dir = Path("translated_chapters")
        self.output_dir.mkdir(exist_ok=True)
        
    def parse_response_file(self, response_file_path: str, chapter_number: int, 
                           force_save: bool = False) -> Dict:
        """Parse a response file and extract chapter content"""
        
        print(f"🔄 Processing response file: {response_file_path}")
        print(f"📖 Chapter number: {chapter_number}")
        
        try:
            # Read the response file
            with open(response_file_path, 'r', encoding='utf-8') as f:
                response_text = f.read()
            
            # Try automatic parsing first
            print("\n🤖 Attempting automatic parsing...")
            auto_result = self.auto_parser.parse_claude_response(response_text, chapter_number)
            
            if auto_result['success'] and not force_save:
                print("✅ Automatic parsing successful!")
                return self._save_chapter_auto(auto_result, chapter_number)
            
            # Manual parsing for failed cases
            print("⚠️ Automatic parsing failed or force_save=True, trying manual parsing...")
            return self._manual_parse_response(response_text, chapter_number)
            
        except FileNotFoundError:
            return {'success': False, 'error': f"Response file not found: {response_file_path}"}
        except Exception as e:
            return {'success': False, 'error': f"Error processing file: {str(e)}"}
    
    def parse_response_text(self, response_text: str, chapter_number: int, 
                           force_save: bool = False) -> Dict:
        """Parse response text directly"""
        
        print(f"🔄 Processing response text for chapter {chapter_number}")
        
        # Try automatic parsing first
        print("\n🤖 Attempting automatic parsing...")
        auto_result = self.auto_parser.parse_claude_response(response_text, chapter_number)
        
        if auto_result['success'] and not force_save:
            print("✅ Automatic parsing successful!")
            return self._save_chapter_auto(auto_result, chapter_number)
        
        # Manual parsing for failed cases
        print("⚠️ Automatic parsing failed or force_save=True, trying manual parsing...")
        return self._manual_parse_response(response_text, chapter_number)
    
    def _manual_parse_response(self, response_text: str, chapter_number: int) -> Dict:
        """Manual parsing when automatic parsing fails"""
        
        result = {
            'success': False,
            'method': 'manual',
            'chapter_file': None,
            'title': 'Unknown',
            'issues_found': [],
            'content_extracted': False
        }
        
        print(f"\n🔧 Manual parsing for Chapter {chapter_number}")
        
        # Step 1: Try to find translation content using various patterns
        translation_content, title, extraction_method = self._extract_content_manually(response_text)
        
        if not translation_content:
            result['issues_found'].append("No translation content found in response")
            return result
        
        print(f"✅ Content extracted using method: {extraction_method}")
        result['content_extracted'] = True
        result['extraction_method'] = extraction_method
        
        # Step 2: Clean and validate the content
        cleaned_content, cleaning_notes = self._clean_content(translation_content)
        result['cleaning_notes'] = cleaning_notes
        
        # Step 3: Extract title
        if not title:
            title = self._extract_title_manually(response_text, cleaned_content)
        result['title'] = title
        
        # Step 4: Save the chapter
        try:
            chapter_file = self._save_manual_chapter(cleaned_content, title, chapter_number)
            result['success'] = True
            result['chapter_file'] = chapter_file
            print(f"✅ Chapter saved to: {chapter_file}")
            
        except Exception as e:
            result['issues_found'].append(f"Failed to save chapter: {str(e)}")
            return result
        
        # Step 5: Try to extract new terms if possible
        self._extract_terms_manually(response_text, result)
        
        return result
    
    def _extract_content_manually(self, response_text: str) -> Tuple[Optional[str], Optional[str], str]:
        """Extract content using multiple fallback methods"""
        
        # Method 1: Standard TRANSLATION_START/END blocks
        translation_pattern = r'TRANSLATION_START\s*\n(.*?)\nTRANSLATION_END'
        match = re.search(translation_pattern, response_text, re.DOTALL)
        if match:
            raw_content = match.group(1).strip()
            content, title = self._parse_frontmatter(raw_content)
            if content and len(content.strip()) > 50:  # Reasonable content length
                return content, title, "standard_translation_block"
        
        # Method 2: Look for markdown frontmatter without explicit blocks
        frontmatter_pattern = r'---\s*\n.*?title:\s*([^\n]+).*?\n---\s*\n(.*?)(?:\n---\s*$|$)'
        match = re.search(frontmatter_pattern, response_text, re.DOTALL)
        if match:
            title = match.group(1).strip()
            content = match.group(2).strip()
            if content and len(content) > 50:
                return content, title, "frontmatter_extraction"
        
        # Method 3: Look for large text blocks that might be the translation
        lines = response_text.split('\n')
        potential_content = []
        current_block = []
        
        for line in lines:
            line = line.strip()
            
            # Skip obvious non-content lines
            if (line.startswith('NEW_TERMS_DISCOVERED:') or 
                line.startswith('CONSISTENCY_CHECK:') or
                line.startswith('TRANSLATION_START') or
                line.startswith('TRANSLATION_END') or
                line.startswith('#') or
                line.startswith('---') or
                not line):
                
                if current_block and len(' '.join(current_block)) > 100:
                    potential_content.append(' '.join(current_block))
                current_block = []
                continue
            
            current_block.append(line)
        
        # Add final block
        if current_block and len(' '.join(current_block)) > 100:
            potential_content.append(' '.join(current_block))
        
        # Find the longest reasonable text block
        if potential_content:
            longest_block = max(potential_content, key=len)
            if len(longest_block) > 200:  # Must be substantial
                return longest_block, None, "longest_text_block"
        
        # Method 4: Try to find any substantial English text
        english_blocks = []
        for line in lines:
            line = line.strip()
            # Look for lines that seem like story content
            if (len(line) > 30 and 
                not line.startswith('[') and 
                not line.startswith('NEW_TERMS') and
                not line.startswith('CONSISTENCY') and
                not line.startswith('TRANSLATION_') and
                not line.startswith('#') and
                not line.startswith('---') and
                re.search(r'[a-zA-Z]', line)):
                english_blocks.append(line)
        
        if english_blocks and len(' '.join(english_blocks)) > 100:
            return ' '.join(english_blocks), None, "english_text_extraction"
        
        return None, None, "no_extraction_method_worked"
    
    def _parse_frontmatter(self, raw_content: str) -> Tuple[str, Optional[str]]:
        """Parse frontmatter from raw content"""
        
        frontmatter_pattern = r'^---\s*\n(.*?)\n---\s*\n(.*?)(?:\n---\s*$|$)'
        match = re.search(frontmatter_pattern, raw_content, re.DOTALL)
        
        if match:
            frontmatter = match.group(1)
            content = match.group(2).strip()
            
            # Extract title from frontmatter
            title_match = re.search(r'title:\s*(.+)', frontmatter)
            title = title_match.group(1).strip() if title_match else None
            
            return content, title
        
        return raw_content, None
    
    def _clean_content(self, content: str) -> Tuple[str, list]:
        """Clean and validate extracted content"""
        
        cleaning_notes = []
        
        # Remove placeholder content
        placeholders_removed = 0
        placeholder_patterns = [
            r'\[English chapter title here\]',
            r'\[Your excellent English translation here.*?\]',
            r'\[.*?chapter title.*?\]',
            r'\[.*?translation.*?here.*?\]'
        ]
        
        for pattern in placeholder_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                content = re.sub(pattern, '', content, flags=re.IGNORECASE)
                placeholders_removed += 1
        
        if placeholders_removed > 0:
            cleaning_notes.append(f"Removed {placeholders_removed} placeholder elements")
        
        # Clean up extra whitespace
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)  # Max 2 consecutive newlines
        content = content.strip()
        
        # Check for remaining issues
        if '[' in content and ']' in content:
            bracket_content = re.findall(r'\[([^\]]+)\]', content)
            if bracket_content:
                cleaning_notes.append(f"Warning: Found bracketed content: {bracket_content[:3]}")
        
        return content, cleaning_notes
    
    def _extract_title_manually(self, response_text: str, content: str) -> str:
        """Try to extract or generate a title"""
        
        # Try to find title in response
        title_patterns = [
            r'title:\s*([^\n]+)',
            r'Chapter\s+\d+[:\-]\s*([^\n]+)',
            r'제\s*\d+\s*장[:\-]\s*([^\n]+)'
        ]
        
        for pattern in title_patterns:
            match = re.search(pattern, response_text, re.IGNORECASE)
            if match:
                title = match.group(1).strip()
                if title and not title.startswith('[') and len(title) < 100:
                    return title
        
        # Try to extract from content
        content_lines = content.split('\n')
        for line in content_lines[:5]:  # Check first 5 lines
            line = line.strip()
            if line and len(line) < 100 and not line.startswith('['):
                return line
        
        return "Untitled Chapter"
    
    def _save_manual_chapter(self, content: str, title: str, chapter_number: int) -> str:
        """Save manually parsed chapter"""
        
        filename = f"chapter_{chapter_number:04d}.md"
        filepath = self.output_dir / filename
        
        # Create markdown content
        markdown_content = f"""---
title: {title}
date: {datetime.now().strftime('%Y-%m-%d')}
parsing_method: manual
---

{content}

---
"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        return str(filepath)
    
    def _save_chapter_auto(self, auto_result: Dict, chapter_number: int) -> Dict:
        """Save chapter using automatic parsing result"""
        
        try:
            chapter_data = auto_result['chapter_data']
            filepath = self.auto_parser.save_chapter(chapter_data, chapter_number)
            
            return {
                'success': True,
                'method': 'automatic',
                'chapter_file': filepath,
                'title': chapter_data['title'],
                'content_extracted': True
            }
        except Exception as e:
            return {
                'success': False,
                'method': 'automatic',
                'error': f"Failed to save automatic result: {str(e)}"
            }
    
    def _extract_terms_manually(self, response_text: str, result: Dict):
        """Try to extract new terms manually"""
        
        # Look for terms section
        terms_pattern = r'NEW_TERMS_DISCOVERED:\s*\n(.*?)(?:\n\n|\nCONSISTENCY_CHECK:|\Z)'
        match = re.search(terms_pattern, response_text, re.DOTALL)
        
        if match:
            terms_text = match.group(1).strip()
            if terms_text and not terms_text.lower().startswith('no') and not terms_text.lower().startswith('none'):
                result['new_terms_found'] = True
                result['terms_text'] = terms_text
            else:
                result['new_terms_found'] = False
        else:
            result['new_terms_found'] = False

def main():
    """Command line interface for manual chapter parsing"""
    
    parser = ManualChapterParser()
    
    if len(sys.argv) < 3:
        print("Usage: python manual_chapter_parser.py <response_file_or_text> <chapter_number> [--force]")
        print("")
        print("Examples:")
        print("  python manual_chapter_parser.py responses/claude_response_chapter_15.txt 15")
        print("  python manual_chapter_parser.py 'TRANSLATION_START...' 15 --force")
        print("")
        sys.exit(1)
    
    input_arg = sys.argv[1]
    chapter_number = int(sys.argv[2])
    force_save = '--force' in sys.argv
    
    print("="*60)
    print("🔧 MANUAL CHAPTER PARSER")
    print("="*60)
    
    # Check if input is a file or direct text
    if Path(input_arg).exists():
        # It's a file
        result = parser.parse_response_file(input_arg, chapter_number, force_save)
    else:
        # It's direct text
        result = parser.parse_response_text(input_arg, chapter_number, force_save)
    
    # Show results
    print("\n" + "="*60)
    print("📊 RESULTS")
    print("="*60)
    
    if result['success']:
        print(f"✅ SUCCESS!")
        print(f"   Method: {result.get('method', 'unknown')}")
        print(f"   File: {result['chapter_file']}")
        print(f"   Title: {result['title']}")
        
        if 'extraction_method' in result:
            print(f"   Extraction: {result['extraction_method']}")
        
        if 'cleaning_notes' in result:
            for note in result['cleaning_notes']:
                print(f"   Note: {note}")
        
        if result.get('new_terms_found'):
            print(f"   New terms: Found")
        
    else:
        print(f"❌ FAILED")
        if 'error' in result:
            print(f"   Error: {result['error']}")
        
        if 'issues_found' in result:
            for issue in result['issues_found']:
                print(f"   Issue: {issue}")

if __name__ == "__main__":
    main()