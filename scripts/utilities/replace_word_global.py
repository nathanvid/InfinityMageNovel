#!/usr/bin/env python3
"""
Global word replacement script for Infinity Mage translation chapters.
Replaces specified words/phrases across all chapter files with backup and preview options.
"""

import os
import re
import argparse
from pathlib import Path
from typing import List, Dict, Tuple
import shutil
from datetime import datetime

class GlobalWordReplacer:
    def __init__(self, chapters_folder: str = "translated_chapters"):
        self.chapters_folder = Path(chapters_folder)
        self.backup_folder = Path("backups")
        
    def find_chapter_files(self) -> List[Path]:
        """Find all chapter markdown files in the folder."""
        if not self.chapters_folder.exists():
            raise FileNotFoundError(f"Chapters folder not found: {self.chapters_folder}")
            
        chapter_files = list(self.chapters_folder.glob("*.md"))
        chapter_files.sort(key=lambda x: self._extract_chapter_number(x.name))
        
        print(f"Found {len(chapter_files)} chapter files")
        return chapter_files
    
    def _extract_chapter_number(self, filename: str) -> int:
        """Extract chapter number from filename for sorting."""
        match = re.search(r'chapter[_\s-]*(\d+)', filename.lower())
        return int(match.group(1)) if match else 0
    
    def preview_replacements(self, old_word: str, new_word: str, 
                           case_sensitive: bool = False, 
                           whole_word: bool = False) -> Dict[str, List[Tuple[int, str, str]]]:
        """Preview what replacements would be made without applying them."""
        chapter_files = self.find_chapter_files()
        preview_results = {}
        
        flags = 0 if case_sensitive else re.IGNORECASE
        if whole_word:
            pattern = rf'\b{re.escape(old_word)}\b'
        else:
            pattern = re.escape(old_word)
        
        total_matches = 0
        
        for file_path in chapter_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                matches = []
                for line_num, line in enumerate(content.split('\n'), 1):
                    if re.search(pattern, line, flags):
                        old_line = line
                        new_line = re.sub(pattern, new_word, line, flags=flags)
                        matches.append((line_num, old_line.strip(), new_line.strip()))
                
                if matches:
                    preview_results[str(file_path)] = matches
                    total_matches += len(matches)
                    
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
        
        print(f"\nPreview Results:")
        print(f"Files with matches: {len(preview_results)}")
        print(f"Total matches: {total_matches}")
        
        if preview_results and total_matches <= 50:  # Show details for reasonable number
            print(f"\nDetailed preview:")
            for file_path, matches in preview_results.items():
                print(f"\n📁 {Path(file_path).name}:")
                for line_num, old_line, new_line in matches:
                    print(f"  Line {line_num}:")
                    print(f"    - {old_line}")
                    print(f"    + {new_line}")
        elif total_matches > 50:
            print(f"\nToo many matches to display individually ({total_matches} matches)")
            print("Use --apply to make the replacements")
        
        return preview_results
    
    def create_backup(self) -> str:
        """Create a backup of the current chapters folder."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"chapters_backup_{timestamp}"
        backup_path = self.backup_folder / backup_name
        
        self.backup_folder.mkdir(exist_ok=True)
        shutil.copytree(self.chapters_folder, backup_path)
        
        print(f"✅ Backup created: {backup_path}")
        return str(backup_path)
    
    def apply_replacements(self, old_word: str, new_word: str,
                         case_sensitive: bool = False,
                         whole_word: bool = False,
                         create_backup: bool = True) -> Dict[str, int]:
        """Apply word replacements to all chapter files."""
        if create_backup:
            backup_path = self.create_backup()
        
        chapter_files = self.find_chapter_files()
        
        flags = 0 if case_sensitive else re.IGNORECASE
        if whole_word:
            pattern = rf'\b{re.escape(old_word)}\b'
        else:
            pattern = re.escape(old_word)
        
        results = {"files_modified": 0, "total_replacements": 0}
        modified_files = []
        
        for file_path in chapter_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    original_content = f.read()
                
                new_content, num_replacements = re.subn(pattern, new_word, original_content, flags=flags)
                
                if num_replacements > 0:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    
                    results["files_modified"] += 1
                    results["total_replacements"] += num_replacements
                    modified_files.append((file_path.name, num_replacements))
                    
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
        
        print(f"\n✅ Replacement completed!")
        print(f"Files modified: {results['files_modified']}")
        print(f"Total replacements: {results['total_replacements']}")
        
        if modified_files:
            print(f"\nModified files:")
            for filename, count in modified_files:
                print(f"  - {filename}: {count} replacements")
        
        return results

def main():
    parser = argparse.ArgumentParser(description="Replace words globally in all Infinity Mage chapters")
    parser.add_argument("old_word", help="Word or phrase to replace")
    parser.add_argument("new_word", help="Replacement word or phrase")
    parser.add_argument("--apply", action="store_true", help="Apply the replacements (default: preview only)")
    parser.add_argument("--case-sensitive", action="store_true", help="Case sensitive matching")
    parser.add_argument("--whole-word", action="store_true", help="Match whole words only")
    parser.add_argument("--no-backup", action="store_true", help="Skip creating backup when applying")
    parser.add_argument("--folder", default="translated_chapters", help="Chapters folder path")
    
    args = parser.parse_args()
    
    replacer = GlobalWordReplacer(args.folder)
    
    try:
        if args.apply:
            print(f"Applying replacement: '{args.old_word}' → '{args.new_word}'")
            print(f"Case sensitive: {args.case_sensitive}")
            print(f"Whole word: {args.whole_word}")
            print(f"Create backup: {not args.no_backup}")
            
            replacer.apply_replacements(
                args.old_word, 
                args.new_word,
                case_sensitive=args.case_sensitive,
                whole_word=args.whole_word,
                create_backup=not args.no_backup
            )
        else:
            print(f"Previewing replacement: '{args.old_word}' → '{args.new_word}'")
            print(f"Case sensitive: {args.case_sensitive}")
            print(f"Whole word: {args.whole_word}")
            print("Add --apply to execute the replacement")
            
            replacer.preview_replacements(
                args.old_word,
                args.new_word, 
                case_sensitive=args.case_sensitive,
                whole_word=args.whole_word
            )
            
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())