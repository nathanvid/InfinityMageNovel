#!/usr/bin/env python3
"""
Global Chapter Title Consistency Fixer for Infinity Mage

This script fixes title inconsistencies by:
1. Analyzing consecutive chapters to identify story arcs (by part numbers)
2. Standardizing titles within each arc to use consistent wording
3. Applying the "Chapter X - Title" format globally
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from collections import defaultdict

class GlobalTitleConsistencyFixer:
    def __init__(self, translated_dir: str = "translated_chapters"):
        self.translated_dir = Path(translated_dir)
        self.chapter_data = {}
        self.story_arcs = {}
        
    def analyze_chapters(self) -> Dict[int, Dict]:
        """Analyze all chapters and extract title information"""
        chapters = {}
        
        for chapter_file in sorted(self.translated_dir.glob("chapter_*.md")):
            # Extract chapter number
            match = re.search(r'chapter_(\d+)', chapter_file.name)
            if not match:
                continue
                
            chapter_num = int(match.group(1))
            
            try:
                with open(chapter_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract title
                title_match = re.search(r'^title:\s*(.+)$', content, re.MULTILINE)
                if not title_match:
                    continue
                    
                title = title_match.group(1).strip()
                
                # Clean title (remove Chapter X - prefix)
                clean_title = self._clean_title(title)
                
                # Extract base title and part number
                base_title, part_num = self._parse_title_parts(clean_title)
                
                chapters[chapter_num] = {
                    'file': chapter_file,
                    'original_title': title,
                    'clean_title': clean_title,
                    'base_title': base_title,
                    'part_number': part_num
                }
                
            except Exception as e:
                print(f"Error analyzing {chapter_file}: {e}")
        
        return chapters
    
    def _clean_title(self, title: str) -> str:
        """Remove Chapter X - prefix and clean up title"""
        cleaned = title
        
        # Remove various prefixes
        cleaned = re.sub(r'^\[\d+\]\s*', '', cleaned)  # [52]
        cleaned = re.sub(r'^Chapter \d+\s*-\s*', '', cleaned)  # Chapter 52 -
        cleaned = re.sub(r'^Chapter \d+\s+', '', cleaned)  # Chapter 52
        
        return cleaned.strip('"\'').strip()
    
    def _parse_title_parts(self, title: str) -> Tuple[str, Optional[int]]:
        """Parse title to extract base title and part number"""
        # Look for pattern: "Title Name (X)" where X is the part number
        match = re.search(r'^(.+?)\s*\((\d+)\)$', title)
        
        if match:
            base_title = match.group(1).strip()
            part_num = int(match.group(2))
            return base_title, part_num
        else:
            # No part number found
            return title, None
    
    def identify_story_arcs(self, chapters: Dict[int, Dict]) -> Dict[str, List[int]]:
        """Group chapters into story arcs based on base titles and similarity"""
        arcs = defaultdict(list)
        
        # First pass: group by exact base title match
        for chapter_num, data in sorted(chapters.items()):
            base_title = data['base_title']
            part_num = data['part_number']
            
            if part_num is not None:
                arcs[base_title].append(chapter_num)
        
        # Second pass: group similar titles that might be part of same arc
        # Look for titles that are very similar (likely inconsistent translations)
        arc_groups = {}
        processed_titles = set()
        
        for base_title, chapter_nums in arcs.items():
            if base_title in processed_titles:
                continue
                
            # Find similar titles
            similar_group = [base_title]
            processed_titles.add(base_title)
            
            for other_title, other_chapters in arcs.items():
                if other_title != base_title and other_title not in processed_titles:
                    if self._are_titles_similar(base_title, other_title):
                        similar_group.append(other_title)
                        processed_titles.add(other_title)
            
            # Merge chapters from similar titles
            if len(similar_group) > 1:
                all_chapters = []
                canonical_title = self._find_best_title_from_group(similar_group, arcs)
                for title in similar_group:
                    all_chapters.extend(arcs[title])
                arc_groups[canonical_title] = sorted(all_chapters)
            elif len(chapter_nums) > 1:
                arc_groups[base_title] = chapter_nums
        
        return arc_groups
    
    def _are_titles_similar(self, title1: str, title2: str) -> bool:
        """Check if two titles are similar enough to be the same arc"""
        # Normalize titles for comparison
        norm1 = self._normalize_for_comparison(title1)
        norm2 = self._normalize_for_comparison(title2)
        
        # Check for high similarity
        from difflib import SequenceMatcher
        similarity = SequenceMatcher(None, norm1, norm2).ratio()
        
        # Consider titles similar if they have >70% similarity
        # or share significant common phrases
        if similarity > 0.7:
            return True
            
        # Check for specific patterns that indicate same arc
        # Example: "An Opportunity More Precious Than Life" vs "An Opportunity Worth More Than Life"
        common_words = set(norm1.split()) & set(norm2.split())
        total_words = set(norm1.split()) | set(norm2.split())
        
        # If they share >60% of words, consider them similar
        if len(common_words) / len(total_words) > 0.6:
            return True
            
        return False
    
    def _normalize_for_comparison(self, title: str) -> str:
        """Normalize title for similarity comparison"""
        # Convert to lowercase, remove extra spaces
        normalized = re.sub(r'\s+', ' ', title.lower().strip())
        # Remove common articles and prepositions for better comparison
        return normalized
    
    def _find_best_title_from_group(self, similar_titles: List[str], arcs: Dict) -> str:
        """Find the best representative title from a group of similar titles"""
        # Use the title that appears in the most chapters
        # If tied, use the lexicographically first one for consistency
        
        best_title = None
        best_count = 0
        
        for title in similar_titles:
            chapter_count = len(arcs[title])
            if chapter_count > best_count or (chapter_count == best_count and (best_title is None or title < best_title)):
                best_count = chapter_count
                best_title = title
                
        return best_title
    
    def find_title_inconsistencies(self, story_arcs: Dict[str, List[int]], chapters: Dict[int, Dict]) -> Dict[str, Dict]:
        """Find inconsistencies within each story arc"""
        inconsistencies = {}
        
        for base_title, chapter_nums in story_arcs.items():
            variations = defaultdict(list)
            
            # Group chapters by their actual base title variations
            for chapter_num in chapter_nums:
                actual_base = chapters[chapter_num]['base_title']
                variations[actual_base].append(chapter_num)
            
            if len(variations) > 1:
                # Found inconsistency!
                inconsistencies[base_title] = {
                    'variations': dict(variations),
                    'chapters': chapter_nums
                }
        
        return inconsistencies
    
    def determine_canonical_title(self, variations: Dict[str, List[int]]) -> str:
        """Determine which title variation should be canonical"""
        # Use the variation that appears most frequently
        # If tied, use the one from the earliest chapter
        
        best_variation = None
        best_score = (0, float('inf'))  # (frequency, earliest_chapter)
        
        for variation, chapter_nums in variations.items():
            frequency = len(chapter_nums)
            earliest_chapter = min(chapter_nums)
            score = (frequency, -earliest_chapter)  # Higher frequency, lower (earlier) chapter number
            
            if score > best_score:
                best_score = score
                best_variation = variation
        
        return best_variation
    
    def fix_inconsistencies(self, chapters: Dict[int, Dict], inconsistencies: Dict[str, Dict], dry_run: bool = True) -> List[Dict]:
        """Fix title inconsistencies"""
        fixes = []
        
        for base_title, inconsistency_data in inconsistencies.items():
            variations = inconsistency_data['variations']
            canonical_title = self.determine_canonical_title(variations)
            
            print(f"\n📚 Fixing arc: '{base_title}'")
            print(f"   Canonical title: '{canonical_title}'")
            
            # Fix all chapters in this arc to use canonical title
            for variation, chapter_nums in variations.items():
                if variation != canonical_title:
                    for chapter_num in chapter_nums:
                        old_title = chapters[chapter_num]['original_title']
                        
                        # Build new title: replace base title with canonical
                        part_num = chapters[chapter_num]['part_number']
                        if part_num is not None:
                            new_clean_title = f"{canonical_title} ({part_num})"
                        else:
                            new_clean_title = canonical_title
                        
                        new_title = f"Chapter {chapter_num} - {new_clean_title}"
                        
                        fix_info = {
                            'file': chapters[chapter_num]['file'],
                            'chapter': chapter_num,
                            'old_title': old_title,
                            'new_title': new_title,
                            'arc': canonical_title
                        }
                        fixes.append(fix_info)
                        
                        print(f"   Chapter {chapter_num:03d}: {variation} → {canonical_title}")
                        
                        if not dry_run:
                            self._apply_title_fix(chapters[chapter_num]['file'], new_title)
        
        return fixes
    
    def apply_chapter_format(self, chapters: Dict[int, Dict], dry_run: bool = True) -> List[Dict]:
        """Apply Chapter X - Title format to all chapters"""
        format_fixes = []
        
        for chapter_num, data in chapters.items():
            old_title = data['original_title']
            clean_title = data['clean_title']
            new_title = f"Chapter {chapter_num} - {clean_title}"
            
            if old_title != new_title:
                fix_info = {
                    'file': data['file'],
                    'chapter': chapter_num,
                    'old_title': old_title,
                    'new_title': new_title,
                    'type': 'format'
                }
                format_fixes.append(fix_info)
                
                if not dry_run:
                    self._apply_title_fix(data['file'], new_title)
        
        return format_fixes
    
    def _apply_title_fix(self, chapter_file: Path, new_title: str):
        """Apply title fix to a chapter file"""
        try:
            with open(chapter_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Replace title line
            new_content = re.sub(
                r'^title:\s*(.+)$',
                f'title: {new_title}',
                content,
                flags=re.MULTILINE
            )
            
            with open(chapter_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
                
        except Exception as e:
            print(f"Error applying fix to {chapter_file}: {e}")
    
    def generate_report(self, chapters: Dict, inconsistencies: Dict, consistency_fixes: List, format_fixes: List) -> str:
        """Generate comprehensive report"""
        lines = [
            "📚 INFINITY MAGE GLOBAL TITLE CONSISTENCY REPORT",
            "=" * 60,
            ""
        ]
        
        # Summary
        lines.extend([
            "📊 SUMMARY:",
            f"   Total chapters analyzed: {len(chapters):,}",
            f"   Story arcs with inconsistencies: {len(inconsistencies):,}",
            f"   Chapters needing consistency fixes: {len(consistency_fixes):,}",
            f"   Chapters needing format fixes: {len(format_fixes):,}",
            ""
        ])
        
        # Inconsistencies found
        if inconsistencies:
            lines.extend([
                "🔍 TITLE INCONSISTENCIES FOUND:",
                ""
            ])
            
            for base_title, data in inconsistencies.items():
                lines.append(f"📖 Arc: '{base_title}'")
                for variation, chapter_nums in data['variations'].items():
                    chapters_str = ", ".join(f"Ch{num}" for num in chapter_nums)
                    lines.append(f"   • '{variation}': {chapters_str}")
                lines.append("")
        
        # Show some example fixes
        if consistency_fixes:
            lines.extend([
                "🔧 CONSISTENCY FIXES (first 10):",
                ""
            ])
            
            for fix in consistency_fixes[:10]:
                lines.extend([
                    f"   Chapter {fix['chapter']:03d} ({fix['arc']}):",
                    f"     OLD: {fix['old_title']}",
                    f"     NEW: {fix['new_title']}",
                    ""
                ])
            
            if len(consistency_fixes) > 10:
                lines.append(f"   ... and {len(consistency_fixes) - 10} more consistency fixes")
                lines.append("")
        
        return "\n".join(lines)
    
    def run_global_fix(self, dry_run: bool = True):
        """Run the complete global title consistency fix"""
        print("🔍 Analyzing all chapters...")
        chapters = self.analyze_chapters()
        
        print("🔗 Identifying story arcs...")
        story_arcs = self.identify_story_arcs(chapters)
        
        print(f"📚 Found {len(story_arcs)} multi-chapter story arcs")
        
        print("🕵️ Finding inconsistencies...")
        inconsistencies = self.find_title_inconsistencies(story_arcs, chapters)
        
        print(f"⚠️  Found {len(inconsistencies)} arcs with inconsistencies")
        
        # Fix inconsistencies first
        consistency_fixes = []
        if inconsistencies:
            print("\n🔧 Fixing title inconsistencies...")
            consistency_fixes = self.fix_inconsistencies(chapters, inconsistencies, dry_run)
        
        # Then apply format to all chapters
        print(f"\n📝 Applying 'Chapter X - Title' format...")
        format_fixes = self.apply_chapter_format(chapters, dry_run)
        
        # Generate report
        report = self.generate_report(chapters, inconsistencies, consistency_fixes, format_fixes)
        print("\n" + report)
        
        total_fixes = len(consistency_fixes) + len(format_fixes)
        if dry_run and total_fixes > 0:
            print(f"\n💡 Run with --apply to apply {total_fixes} fixes")
        elif total_fixes > 0:
            print(f"\n✅ Applied {total_fixes} fixes successfully!")
        else:
            print("\n✅ All titles are already consistent!")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Fix global chapter title consistency')
    parser.add_argument('--apply', action='store_true',
                       help='Actually apply fixes (default is dry run)')
    parser.add_argument('--dir', default='translated_chapters',
                       help='Directory containing translated chapters')
    
    args = parser.parse_args()
    
    fixer = GlobalTitleConsistencyFixer(args.dir)
    fixer.run_global_fix(dry_run=not args.apply)

if __name__ == "__main__":
    main()