#!/usr/bin/env python3
"""
Batch Chapter Rescue Tool
Finds failed chapters and attempts to rescue them using manual parsing
"""

import os
import re
import sys
from pathlib import Path

# Add parent directory to path to import from other script modules
sys.path.append(str(Path(__file__).parent.parent))

from analysis.manual_chapter_parser import ManualChapterParser
from analysis.check_placeholder_chapters import check_placeholder_chapters

def find_response_files():
    """Find all response files that might contain failed chapters"""
    
    response_files = []
    
    # Check responses directory
    responses_dir = Path("responses")
    if responses_dir.exists():
        for file in responses_dir.glob("*.txt"):
            response_files.append(file)
    
    # Check other common locations
    for pattern in ["reponses/*.txt", "prompts/*.txt", "claude_response*.txt"]:
        for file in Path(".").glob(pattern):
            if file not in response_files:
                response_files.append(file)
    
    return sorted(response_files)

def extract_chapter_number_from_filename(filename: str) -> int:
    """Try to extract chapter number from filename"""
    
    # Common patterns
    patterns = [
        r'chapter_(\d+)',
        r'chapter(\d+)', 
        r'ch_(\d+)',
        r'ch(\d+)',
        r'(\d+)',
    ]
    
    filename_lower = filename.lower()
    
    for pattern in patterns:
        match = re.search(pattern, filename_lower)
        if match:
            return int(match.group(1))
    
    return 0  # Unknown

def rescue_failed_chapters():
    """Main rescue function"""
    
    print("🚑 CHAPTER RESCUE OPERATION")
    print("="*50)
    
    # Step 1: Find problematic chapters
    print("📋 Step 1: Analyzing existing chapters...")
    chapter_analysis = check_placeholder_chapters()
    
    if chapter_analysis['problematic'] == 0:
        print("✅ No problematic chapters found!")
        return
    
    print(f"Found {chapter_analysis['problematic']} problematic chapters")
    
    # Step 2: Find response files
    print("\n🔍 Step 2: Looking for response files...")
    response_files = find_response_files()
    print(f"Found {len(response_files)} response files")
    
    if not response_files:
        print("❌ No response files found to rescue from")
        return
    
    # Step 3: Try to rescue each problematic chapter
    print("\n🚑 Step 3: Attempting rescue operations...")
    parser = ManualChapterParser()
    
    rescued_count = 0
    failed_count = 0
    
    for problematic_file in chapter_analysis['problematic_files']:
        # Extract chapter number from problematic file
        chapter_match = re.search(r'chapter_(\d+)', problematic_file)
        if not chapter_match:
            print(f"⚠️ Cannot extract chapter number from {problematic_file}")
            continue
        
        chapter_num = int(chapter_match.group(1))
        
        print(f"\n🚑 Rescuing Chapter {chapter_num}...")
        
        # Try to find matching response file
        rescued = False
        
        for response_file in response_files:
            response_chapter_num = extract_chapter_number_from_filename(response_file.name)
            
            if response_chapter_num == chapter_num or response_chapter_num == 0:
                print(f"   Trying response file: {response_file.name}")
                
                try:
                    result = parser.parse_response_file(str(response_file), chapter_num, force_save=True)
                    
                    if result['success']:
                        print(f"   ✅ Rescued using {result.get('method', 'unknown')} method")
                        rescued_count += 1
                        rescued = True
                        break
                    else:
                        print(f"   ❌ Rescue failed: {result.get('error', 'unknown error')}")
                        
                except Exception as e:
                    print(f"   ❌ Error during rescue: {str(e)}")
        
        if not rescued:
            print(f"   ❌ Could not rescue Chapter {chapter_num}")
            failed_count += 1
    
    # Final report
    print("\n" + "="*50)
    print("📊 RESCUE OPERATION COMPLETE")
    print("="*50)
    print(f"✅ Chapters rescued: {rescued_count}")
    print(f"❌ Chapters still failed: {failed_count}")
    print(f"📁 Total response files checked: {len(response_files)}")
    
    if rescued_count > 0:
        print(f"\n💡 Recommendation: Re-run the chapter analysis to verify rescued chapters")

def interactive_rescue():
    """Interactive mode for rescuing specific chapters"""
    
    print("🎯 INTERACTIVE CHAPTER RESCUE")
    print("="*40)
    
    parser = ManualChapterParser()
    
    while True:
        print("\nOptions:")
        print("1. Rescue specific chapter from response file")
        print("2. Rescue from direct text input")
        print("3. List response files")
        print("4. Exit")
        
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == '1':
            # Rescue from file
            response_file = input("Response file path: ").strip()
            chapter_num = int(input("Chapter number: ").strip())
            
            if not Path(response_file).exists():
                print(f"❌ File not found: {response_file}")
                continue
            
            result = parser.parse_response_file(response_file, chapter_num, force_save=True)
            
            if result['success']:
                print(f"✅ Chapter {chapter_num} rescued successfully!")
                print(f"   File: {result['chapter_file']}")
                print(f"   Title: {result['title']}")
            else:
                print(f"❌ Rescue failed: {result.get('error', 'unknown error')}")
        
        elif choice == '2':
            # Rescue from text
            print("Paste the Claude response (end with empty line):")
            lines = []
            while True:
                line = input()
                if not line:
                    break
                lines.append(line)
            
            response_text = '\n'.join(lines)
            chapter_num = int(input("Chapter number: ").strip())
            
            result = parser.parse_response_text(response_text, chapter_num, force_save=True)
            
            if result['success']:
                print(f"✅ Chapter {chapter_num} rescued successfully!")
                print(f"   File: {result['chapter_file']}")
                print(f"   Title: {result['title']}")
            else:
                print(f"❌ Rescue failed: {result.get('error', 'unknown error')}")
        
        elif choice == '3':
            # List files
            response_files = find_response_files()
            print(f"\nFound {len(response_files)} response files:")
            for i, file in enumerate(response_files, 1):
                chapter_num = extract_chapter_number_from_filename(file.name)
                print(f"  {i:2d}. {file.name} (Chapter {chapter_num if chapter_num else '?'})")
        
        elif choice == '4':
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_rescue()
    else:
        rescue_failed_chapters()