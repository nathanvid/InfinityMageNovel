#!/usr/bin/env python3
"""
Chapter Title Standardization Script for Infinity Mage

This script fixes inconsistent chapter title formats across all translated chapters.
It standardizes titles to a clean format: "Title Name (Part Number)"
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

class ChapterTitleFixer:
    def __init__(self, translated_dir: str = "translated_chapters"):
        self.translated_dir = Path(translated_dir)
        self.fixes_made = []
        self.patterns_found = {}
        
    def analyze_title_patterns(self) -> Dict[str, List[str]]:
        """Analyze current title patterns to understand inconsistencies"""
        patterns = {}
        
        for chapter_file in self.translated_dir.glob("chapter_*.md"):
            try:
                with open(chapter_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract title line
                title_match = re.search(r'^title:\s*(.+)$', content, re.MULTILINE)
                if title_match:
                    title = title_match.group(1).strip()
                    
                    # Categorize title patterns
                    pattern = self._identify_pattern(title)
                    if pattern not in patterns:
                        patterns[pattern] = []
                    patterns[pattern].append(f"{chapter_file.name}: {title}")
                        
            except Exception as e:
                print(f"Error reading {chapter_file}: {e}")
        
        return patterns
    
    def _identify_pattern(self, title: str) -> str:
        """Identify the pattern type of a title"""
        if title.startswith('[') and ']' in title:
            return "Square brackets with number"
        elif title.startswith('Chapter ') and ' - ' in title:
            return "Chapter X - Title format"
        elif re.match(r'^\[\d+\]', title):
            return "Square brackets only number"
        elif re.match(r'^Chapter \d+', title):
            return "Chapter number prefix"
        else:
            return "Clean format"
    
    def standardize_title(self, title: str, chapter_num: int) -> str:
        """Standardize a title to Chapter X - Title format"""
        # Remove various chapter number prefixes first
        cleaned = title
        
        # Remove patterns like "[52]", "[304]", etc.
        cleaned = re.sub(r'^\[\d+\]\s*', '', cleaned)
        
        # Remove "Chapter X -" patterns 
        cleaned = re.sub(r'^Chapter \d+\s*-\s*', '', cleaned)
        
        # Remove standalone chapter numbers
        cleaned = re.sub(r'^Chapter \d+\s+', '', cleaned)
        
        # Clean up extra whitespace and quotes
        cleaned = cleaned.strip('"\'').strip()
        
        # Fix common formatting issues and specific inconsistencies
        cleaned = self._fix_common_issues(cleaned, chapter_num)
        
        # Now add the standard "Chapter X - " prefix
        return f"Chapter {chapter_num} - {cleaned}"
    
    def _fix_common_issues(self, title: str) -> str:
        """Fix common title formatting issues"""
        # Standardize part numbering - ensure space before parentheses
        title = re.sub(r'(\w)\((\d+)\)', r'\1 (\2)', title)
        
        # Fix double spaces
        title = re.sub(r'\s+', ' ', title)
        
        # Capitalize important words (basic title case)
        # But preserve existing capitalization for proper nouns
        
        return title.strip()
    
    def fix_chapter_titles(self, dry_run: bool = True) -> List[Dict]:
        """Fix all chapter titles to standardized format"""
        fixes = []
        
        for chapter_file in sorted(self.translated_dir.glob("chapter_*.md")):
            # Extract chapter number from filename
            match = re.search(r'chapter_(\d+)', chapter_file.name)
            if not match:
                continue
                
            chapter_num = int(match.group(1))
            
            try:
                with open(chapter_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Find and extract current title
                title_match = re.search(r'^title:\s*(.+)$', content, re.MULTILINE)
                if not title_match:
                    continue
                    
                current_title = title_match.group(1).strip()
                standardized_title = self.standardize_title(current_title, chapter_num)
                
                if current_title != standardized_title:
                    fix_info = {
                        'file': chapter_file.name,
                        'chapter': chapter_num,
                        'old_title': current_title,
                        'new_title': standardized_title
                    }
                    fixes.append(fix_info)
                    
                    if not dry_run:
                        # Apply the fix
                        new_content = re.sub(
                            r'^title:\s*(.+)$',
                            f'title: {standardized_title}',
                            content,
                            flags=re.MULTILINE
                        )
                        
                        with open(chapter_file, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                            
            except Exception as e:
                print(f"Error processing {chapter_file}: {e}")
        
        return fixes
    
    def generate_report(self, fixes: List[Dict]) -> str:
        """Generate a report of title fixes"""
        lines = [
            "📚 INFINITY MAGE CHAPTER TITLE STANDARDIZATION REPORT",
            "=" * 60,
            ""
        ]
        
        if not fixes:
            lines.append("✅ All chapter titles are already standardized!")
            return "\n".join(lines)
        
        lines.extend([
            f"📊 SUMMARY:",
            f"   Total chapters needing fixes: {len(fixes):,}",
            f"   Chapters analyzed: {len(list(self.translated_dir.glob('chapter_*.md'))):,}",
            ""
        ])
        
        # Group fixes by pattern type
        pattern_groups = {}
        for fix in fixes:
            pattern = self._identify_pattern(fix['old_title'])
            if pattern not in pattern_groups:
                pattern_groups[pattern] = []
            pattern_groups[pattern].append(fix)
        
        lines.append("📝 FIXES BY PATTERN TYPE:")
        for pattern, pattern_fixes in pattern_groups.items():
            lines.extend([
                f"",
                f"## {pattern} ({len(pattern_fixes)} chapters)",
                ""
            ])
            
            for fix in pattern_fixes[:10]:  # Show first 10 examples
                lines.append(f"   Chapter {fix['chapter']:03d}:")
                lines.append(f"     OLD: {fix['old_title']}")
                lines.append(f"     NEW: {fix['new_title']}")
                lines.append("")
                
            if len(pattern_fixes) > 10:
                lines.append(f"   ... and {len(pattern_fixes) - 10} more")
                lines.append("")
        
        return "\n".join(lines)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Standardize chapter title formats')
    parser.add_argument('--apply', action='store_true', 
                       help='Actually apply fixes (default is dry run)')
    parser.add_argument('--analyze', action='store_true',
                       help='Just analyze current patterns')
    parser.add_argument('--dir', default='translated_chapters',
                       help='Directory containing translated chapters')
    
    args = parser.parse_args()
    
    fixer = ChapterTitleFixer(args.dir)
    
    if args.analyze:
        print("🔍 ANALYZING CURRENT TITLE PATTERNS")
        print("=" * 40)
        patterns = fixer.analyze_title_patterns()
        
        for pattern, examples in patterns.items():
            print(f"\n📋 {pattern} ({len(examples)} chapters):")
            for example in examples[:5]:  # Show first 5 examples
                print(f"   {example}")
            if len(examples) > 5:
                print(f"   ... and {len(examples) - 5} more")
    else:
        fixes = fixer.fix_chapter_titles(dry_run=not args.apply)
        report = fixer.generate_report(fixes)
        print(report)
        
        if args.apply and fixes:
            print(f"\n✅ Applied {len(fixes)} title fixes successfully!")
        elif fixes:
            print(f"\n💡 Run with --apply to apply {len(fixes)} fixes")

if __name__ == "__main__":
    main()