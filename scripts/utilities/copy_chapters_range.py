#!/usr/bin/env python3
"""
Chapter range copy program for Infinity Mage translation.
Copies a range of chapters from start to end chapter number to a specified folder.
"""

import re
import argparse
import shutil
from pathlib import Path
from typing import List, Tuple, Optional

class ChapterRangeCopier:
    def __init__(self, source_folder: str = "translated_chapters"):
        self.source_folder = Path(source_folder)
        
    def find_all_chapters(self) -> List[Tuple[int, Path]]:
        """Find all chapter files and extract their numbers."""
        if not self.source_folder.exists():
            raise FileNotFoundError(f"Source folder not found: {self.source_folder}")
            
        chapter_files = []
        
        for file_path in self.source_folder.glob("*.md"):
            chapter_num = self._extract_chapter_number(file_path.name)
            if chapter_num is not None:
                chapter_files.append((chapter_num, file_path))
        
        # Sort by chapter number
        chapter_files.sort(key=lambda x: x[0])
        
        print(f"Found {len(chapter_files)} chapters (range: {chapter_files[0][0]}-{chapter_files[-1][0]})")
        return chapter_files
    
    def _extract_chapter_number(self, filename: str) -> Optional[int]:
        """Extract chapter number from filename."""
        # Try different patterns
        patterns = [
            r'chapter[_\s-]*(\d+)',  # "Chapter 1", "chapter_1", "chapter-1"
            r'(\d+)[_\s-]*chapter',  # "1_chapter", "1 chapter"
            r'^(\d+)[_\s-]',         # Starting with number
            r'[_\s-](\d+)[_\s-]',    # Number surrounded by separators
        ]
        
        for pattern in patterns:
            match = re.search(pattern, filename.lower())
            if match:
                return int(match.group(1))
        
        return None
    
    def get_chapters_in_range(self, start_chapter: int, end_chapter: int) -> List[Tuple[int, Path]]:
        """Get all chapters within the specified range."""
        all_chapters = self.find_all_chapters()
        
        chapters_in_range = [
            (num, path) for num, path in all_chapters 
            if start_chapter <= num <= end_chapter
        ]
        
        if not chapters_in_range:
            print(f"⚠️  No chapters found in range {start_chapter}-{end_chapter}")
            available_range = f"{all_chapters[0][0]}-{all_chapters[-1][0]}"
            print(f"Available range: {available_range}")
            return []
        
        missing_chapters = []
        for expected_num in range(start_chapter, end_chapter + 1):
            if not any(num == expected_num for num, _ in chapters_in_range):
                missing_chapters.append(expected_num)
        
        if missing_chapters:
            print(f"⚠️  Missing chapters in range: {missing_chapters}")
        
        return chapters_in_range
    
    def copy_chapters_range(self, start_chapter: int, end_chapter: int, 
                           destination_folder: str, overwrite: bool = False) -> dict:
        """Copy chapters in specified range to destination folder."""
        dest_path = Path(destination_folder)
        
        # Create destination folder if it doesn't exist
        dest_path.mkdir(parents=True, exist_ok=True)
        print("📁 Destination folder:", dest_path.absolute())
        
        # Get chapters in range
        chapters_to_copy = self.get_chapters_in_range(start_chapter, end_chapter)
        
        if not chapters_to_copy:
            return {"success": False, "copied": 0, "skipped": 0, "errors": 0}
        
        results = {"success": True, "copied": 0, "skipped": 0, "errors": 0}
        
        print(f"\n📋 Copying {len(chapters_to_copy)} chapters ({start_chapter}-{end_chapter}):")
        
        for chapter_num, source_path in chapters_to_copy:
            dest_file = dest_path / source_path.name
            
            try:
                # Check if file already exists
                if dest_file.exists() and not overwrite:
                    print(f"  ⏭️  Chapter {chapter_num}: {source_path.name} (already exists, skipped)")
                    results["skipped"] += 1
                    continue
                
                # Copy the file
                file_existed = dest_file.exists()
                shutil.copy2(source_path, dest_file)
                status = "overwritten" if file_existed else "copied"
                print(f"  ✅ Chapter {chapter_num}: {source_path.name} ({status})")
                results["copied"] += 1
                
            except Exception as e:
                print(f"  ❌ Chapter {chapter_num}: {source_path.name} - Error: {e}")
                results["errors"] += 1
        
        # Summary
        print(f"\n📊 Copy Summary:")
        print(f"  • Successfully copied: {results['copied']}")
        print(f"  • Skipped (already exist): {results['skipped']}")
        print(f"  • Errors: {results['errors']}")
        print(f"  • Destination: {dest_path.absolute()}")
        
        return results
    
    def list_chapters_in_range(self, start_chapter: int, end_chapter: int):
        """List chapters that would be copied without actually copying."""
        chapters_in_range = self.get_chapters_in_range(start_chapter, end_chapter)
        
        if not chapters_in_range:
            return
        
        print(f"\n📋 Chapters in range {start_chapter}-{end_chapter}:")
        for chapter_num, file_path in chapters_in_range:
            file_size = file_path.stat().st_size / 1024  # KB
            print(f"  • Chapter {chapter_num}: {file_path.name} ({file_size:.1f} KB)")

def main():
    parser = argparse.ArgumentParser(description="Copy a range of Infinity Mage chapters to a specified folder")
    parser.add_argument("start_chapter", type=int, help="Starting chapter number")
    parser.add_argument("end_chapter", type=int, help="Ending chapter number (inclusive)")
    parser.add_argument("destination", help="Destination folder path")
    parser.add_argument("--source", default="translated_chapters", help="Source folder path (default: translated_chapters)")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing files")
    parser.add_argument("--list-only", action="store_true", help="List files that would be copied without copying")
    
    args = parser.parse_args()
    
    # Validate range
    if args.start_chapter > args.end_chapter:
        print("❌ Error: Start chapter must be less than or equal to end chapter")
        return 1
    
    copier = ChapterRangeCopier(args.source)
    
    try:
        if args.list_only:
            print(f"Listing chapters {args.start_chapter}-{args.end_chapter} from {args.source}")
            copier.list_chapters_in_range(args.start_chapter, args.end_chapter)
        else:
            print(f"Copying chapters {args.start_chapter}-{args.end_chapter}")
            print(f"Source: {args.source}")
            print(f"Destination: {args.destination}")
            print(f"Overwrite existing: {args.overwrite}")
            
            results = copier.copy_chapters_range(
                args.start_chapter, 
                args.end_chapter, 
                args.destination,
                overwrite=args.overwrite
            )
            
            if not results["success"] or results["errors"] > 0:
                return 1
                
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())