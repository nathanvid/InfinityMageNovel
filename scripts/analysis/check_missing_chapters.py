#!/usr/bin/env python3
"""
Missing Chapters Checker for Infinity Mage

This script identifies which chapters are missing from the translated_chapters folder
by comparing against the expected chapter range or available Korean source files.
"""

import os
import glob
import re
from pathlib import Path
from typing import List, Set, Tuple

class MissingChaptersChecker:
    def __init__(self, translated_dir: str = "translated_chapters"):
        self.translated_dir = Path(translated_dir)
        self.translated_chapters = self._get_translated_chapters()
        
    def _get_translated_chapters(self) -> Set[int]:
        """Get set of chapter numbers that have been translated"""
        chapters = set()
        
        if not self.translated_dir.exists():
            print(f"❌ Translated chapters directory not found: {self.translated_dir}")
            return chapters
            
        # Look for chapter files with patterns like: chapter_0001.md, chapter_1.md, etc.
        patterns = [
            "chapter_*.md",
            "Chapter_*.md", 
            "chapter_*.txt",
            "Chapter_*.txt"
        ]
        
        for pattern in patterns:
            for file_path in self.translated_dir.glob(pattern):
                # Extract chapter number from filename
                match = re.search(r'chapter_?(\d+)', file_path.name.lower())
                if match:
                    chapters.add(int(match.group(1)))
        
        return chapters
    
    def _get_source_chapters(self) -> Set[int]:
        """Get chapter numbers from Korean source files if available"""
        chapters = set()
        
        # Look for Korean source files in common locations
        source_dirs = [
            "korean_chapters",
            "source_chapters", 
            "original_chapters",
            "Infinity Mage Chapters 1-1277 Translated",
            "Infinity Mage Chapters 1-1277"
        ]
        
        for source_dir in source_dirs:
            source_path = Path(source_dir)
            if source_path.exists():
                print(f"📚 Found source directory: {source_path}")
                
                # Look for chapter files
                patterns = ["*chapter*.txt", "*Chapter*.txt", "chapter*.md", "Chapter*.md"]
                
                for pattern in patterns:
                    for file_path in source_path.glob(pattern):
                        # Extract chapter numbers from various filename patterns
                        chapter_matches = re.findall(r'(\d+)', file_path.name)
                        if chapter_matches:
                            # Take the first number as chapter number
                            chapters.add(int(chapter_matches[0]))
        
        return chapters
    
    def check_missing_in_range(self, start_chapter: int = 1, end_chapter: int = 1277) -> List[int]:
        """Check for missing chapters in a specific range"""
        expected_chapters = set(range(start_chapter, end_chapter + 1))
        missing = sorted(expected_chapters - self.translated_chapters)
        return missing
    
    def check_against_source(self) -> Tuple[List[int], Set[int]]:
        """Check missing chapters against available source files"""
        source_chapters = self._get_source_chapters()
        
        if not source_chapters:
            print("📝 No source chapters found - falling back to range check")
            return self.check_missing_in_range(), set()
            
        missing = sorted(source_chapters - self.translated_chapters)
        return missing, source_chapters
    
    def get_statistics(self) -> dict:
        """Get statistics about translation progress"""
        source_chapters = self._get_source_chapters()
        
        if source_chapters:
            total_available = len(source_chapters)
            total_translated = len(self.translated_chapters & source_chapters)
        else:
            # Default range 1-1277
            total_available = 1277
            total_translated = len([c for c in self.translated_chapters if 1 <= c <= 1277])
        
        percentage = (total_translated / total_available * 100) if total_available > 0 else 0
        
        return {
            'total_available': total_available,
            'total_translated': total_translated,
            'total_missing': total_available - total_translated,
            'completion_percentage': percentage,
            'translated_chapters': sorted(list(self.translated_chapters))
        }
    
    def generate_report(self, max_missing_display: int = 50) -> str:
        """Generate a comprehensive report of missing chapters"""
        
        lines = [
            "📖 INFINITY MAGE TRANSLATION PROGRESS REPORT",
            "=" * 50
        ]
        
        # Statistics
        stats = self.get_statistics()
        lines.extend([
            "",
            "📊 STATISTICS:",
            f"   Total available chapters: {stats['total_available']:,}",
            f"   Total translated: {stats['total_translated']:,}",
            f"   Missing chapters: {stats['total_missing']:,}",
            f"   Completion: {stats['completion_percentage']:.1f}%",
            ""
        ])
        
        # Progress bar
        progress = int(stats['completion_percentage'] / 2)  # Scale to 50 chars
        bar = "█" * progress + "░" * (50 - progress)
        lines.append(f"   Progress: [{bar}] {stats['completion_percentage']:.1f}%")
        lines.append("")
        
        # Check for missing chapters
        missing, source_chapters = self.check_against_source()
        
        if missing:
            lines.extend([
                f"❌ MISSING CHAPTERS ({len(missing):,} total):",
                ""
            ])
            
            if len(missing) <= max_missing_display:
                # Show all missing chapters
                lines.append("Missing chapters:")
                # Group consecutive chapters for cleaner display
                ranges = self._group_consecutive_numbers(missing)
                for range_str in ranges:
                    lines.append(f"   • {range_str}")
            else:
                # Show first few, last few, and count
                lines.extend([
                    f"First {max_missing_display//2} missing:",
                    "   " + ", ".join(map(str, missing[:max_missing_display//2])),
                    "",
                    f"Last {max_missing_display//2} missing:", 
                    "   " + ", ".join(map(str, missing[-max_missing_display//2:])),
                    "",
                    f"... and {len(missing) - max_missing_display} more"
                ])
        else:
            lines.append("✅ NO MISSING CHAPTERS - Translation complete!")
        
        lines.extend([
            "",
            "📁 DIRECTORIES CHECKED:",
            f"   Translated: {self.translated_dir}",
        ])
        
        if source_chapters:
            lines.append(f"   Source files: Found {len(source_chapters):,} chapters")
        
        return "\n".join(lines)
    
    def _group_consecutive_numbers(self, numbers: List[int]) -> List[str]:
        """Group consecutive numbers into ranges for cleaner display"""
        if not numbers:
            return []
        
        ranges = []
        start = numbers[0]
        end = start
        
        for i in range(1, len(numbers)):
            if numbers[i] == end + 1:
                end = numbers[i]
            else:
                if start == end:
                    ranges.append(str(start))
                else:
                    ranges.append(f"{start}-{end}")
                start = end = numbers[i]
        
        # Add the last range
        if start == end:
            ranges.append(str(start))
        else:
            ranges.append(f"{start}-{end}")
        
        return ranges
    
    def export_missing_list(self, filename: str = "missing_chapters.txt"):
        """Export list of missing chapters to a file"""
        missing, _ = self.check_against_source()
        
        if not missing:
            print("✅ No missing chapters to export")
            return
            
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# Missing Chapters for Infinity Mage Translation\n")
            f.write(f"# Generated on: {Path().cwd()}\n")
            f.write(f"# Total missing: {len(missing):,} chapters\n\n")
            
            for chapter in missing:
                f.write(f"chapter_{chapter:04d}\n")
        
        print(f"📄 Missing chapters list exported to: {filename}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Check for missing translated chapters')
    parser.add_argument('--dir', default='translated_chapters', 
                       help='Directory containing translated chapters (default: translated_chapters)')
    parser.add_argument('--range', nargs=2, type=int, metavar=('START', 'END'),
                       help='Check specific chapter range (e.g., --range 1 100)')
    parser.add_argument('--export', metavar='FILENAME',
                       help='Export missing chapters list to file')
    parser.add_argument('--quiet', '-q', action='store_true',
                       help='Show only missing chapter numbers')
    
    args = parser.parse_args()
    
    checker = MissingChaptersChecker(args.dir)
    
    if args.quiet:
        # Just show missing chapter numbers
        if args.range:
            missing = checker.check_missing_in_range(args.range[0], args.range[1])
        else:
            missing, _ = checker.check_against_source()
        
        if missing:
            print(" ".join(map(str, missing)))
        else:
            print("# No missing chapters")
    else:
        # Show full report
        report = checker.generate_report()
        print(report)
        
        if args.range:
            print(f"\n🔍 RANGE CHECK ({args.range[0]}-{args.range[1]}):")
            missing_in_range = checker.check_missing_in_range(args.range[0], args.range[1])
            if missing_in_range:
                print(f"Missing in range: {len(missing_in_range)} chapters")
                ranges = checker._group_consecutive_numbers(missing_in_range)
                for range_str in ranges:
                    print(f"   • {range_str}")
            else:
                print("✅ No missing chapters in specified range")
    
    if args.export:
        checker.export_missing_list(args.export)

if __name__ == "__main__":
    main()