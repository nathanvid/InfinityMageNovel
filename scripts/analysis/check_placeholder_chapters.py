#!/usr/bin/env python3
"""
Check Placeholder Chapters
Identifies chapters with placeholder content that should be marked as failed
"""

import os
import sys
from pathlib import Path

# Add parent directory to path to import from other script modules
sys.path.append(str(Path(__file__).parent.parent))

from translation.infinity_response_parser import InfinityResponseParser
from infinity_glossary_manager import InfinityGlossaryManager

def check_placeholder_chapters():
    """Check all translated chapters for placeholder content"""
    
    translated_dir = Path("translated_chapters")
    if not translated_dir.exists():
        print("❌ No translated_chapters directory found")
        return
    
    # Initialize parser
    manager = InfinityGlossaryManager()
    parser = InfinityResponseParser(manager)
    
    # Find all markdown files
    chapter_files = list(translated_dir.glob("*.md"))
    
    print(f"📁 Found {len(chapter_files)} translated chapter files")
    print("🔍 Checking for placeholder content...\n")
    
    problematic_chapters = []
    valid_chapters = []
    
    for chapter_file in sorted(chapter_files):
        try:
            with open(chapter_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract content between frontmatter
            lines = content.split('\n')
            content_lines = []
            in_frontmatter = False
            frontmatter_count = 0
            
            for line in lines:
                if line.strip() == '---':
                    frontmatter_count += 1
                    if frontmatter_count == 2:
                        in_frontmatter = False
                        continue
                    if frontmatter_count == 1:
                        in_frontmatter = True
                        continue
                
                if not in_frontmatter and frontmatter_count >= 2:
                    content_lines.append(line)
            
            translation_content = '\n'.join(content_lines).strip()
            
            # Check for issues using the parser's validation
            if translation_content:
                # Use a dummy Korean text for length comparison
                dummy_korean = "시로네는 마법을 연습했다. " * 20  # Make it reasonably long
                validation_issues = parser._validate_translation_quality(
                    translation_content, dummy_korean, int(chapter_file.stem.split('_')[-1])
                )
                
                critical_issues = [issue for issue in validation_issues if issue.startswith('CRITICAL:')]
                
                if critical_issues:
                    problematic_chapters.append({
                        'file': chapter_file.name,
                        'issues': critical_issues,
                        'content_preview': translation_content[:100] + "..." if len(translation_content) > 100 else translation_content
                    })
                else:
                    valid_chapters.append(chapter_file.name)
            else:
                problematic_chapters.append({
                    'file': chapter_file.name,
                    'issues': ['CRITICAL: File appears to be completely empty'],
                    'content_preview': '<EMPTY>'
                })
                
        except Exception as e:
            print(f"❌ Error reading {chapter_file.name}: {e}")
    
    print(f"📊 RESULTS:")
    print(f"✅ Valid chapters: {len(valid_chapters)}")
    print(f"❌ Problematic chapters: {len(problematic_chapters)}")
    
    if problematic_chapters:
        print(f"\n🚨 PROBLEMATIC CHAPTERS:")
        for chapter in problematic_chapters:
            print(f"\n📄 {chapter['file']}:")
            for issue in chapter['issues']:
                print(f"  ⚠️  {issue}")
            print(f"  📝 Preview: {chapter['content_preview']}")
    
    if valid_chapters:
        print(f"\n✅ VALID CHAPTERS: {', '.join(valid_chapters[:10])}")
        if len(valid_chapters) > 10:
            print(f"   ... and {len(valid_chapters) - 10} more")
    
    return {
        'problematic': len(problematic_chapters),
        'valid': len(valid_chapters),
        'problematic_files': [c['file'] for c in problematic_chapters]
    }

if __name__ == "__main__":
    results = check_placeholder_chapters()
    
    print(f"\n📈 SUMMARY:")
    print(f"Total chapters analyzed: {results['problematic'] + results['valid']}")
    print(f"Problematic chapters: {results['problematic']}")
    print(f"Valid chapters: {results['valid']}")
    
    if results['problematic'] > 0:
        print(f"\n💡 RECOMMENDATION:")
        print("These problematic chapters should be retranslated as they contain")
        print("placeholder content instead of actual Korean→English translations.")