#!/usr/bin/env python3
"""
Chapter Rescue CLI
Easy-to-use interface for rescuing failed chapters
"""

import sys
import argparse
from pathlib import Path

# Add parent directory to path to import from other script modules
sys.path.append(str(Path(__file__).parent.parent))

from analysis.manual_chapter_parser import ManualChapterParser
from analysis.batch_rescue_chapters import rescue_failed_chapters, interactive_rescue

def main():
    """Main CLI interface"""
    
    parser = argparse.ArgumentParser(description='Rescue failed chapters from Claude responses')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Single rescue command
    single_parser = subparsers.add_parser('single', help='Rescue a single chapter')
    single_parser.add_argument('--input', help='Response file path or text')
    single_parser.add_argument('--chapter', type=int, help='Chapter number')
    single_parser.add_argument('--force', action='store_true', help='Force manual parsing even if auto works')
    
    # Batch rescue command  
    batch_parser = subparsers.add_parser('batch', help='Batch rescue all failed chapters')
    
    # Interactive command
    interactive_parser = subparsers.add_parser('interactive', help='Interactive rescue mode')
    
    # Check command
    check_parser = subparsers.add_parser('check', help='Check for problematic chapters')
    
    args = parser.parse_args()
    
    if args.command == 'single':
        rescue_single(args.input, args.chapter, args.force)
    elif args.command == 'batch':
        rescue_failed_chapters()
    elif args.command == 'interactive':
        interactive_rescue()
    elif args.command == 'check':
        check_chapters()
    else:
        parser.print_help()

def rescue_single(input_arg: str, chapter_number: int, force: bool):
    """Rescue a single chapter"""
    
    print(f"🚑 Rescuing Chapter {chapter_number}")
    print("="*40)
    
    manual_parser = ManualChapterParser()
    
    # Check if input is file or text
    if Path(input_arg).exists():
        print(f"📄 Processing file: {input_arg}")
        result = manual_parser.parse_response_file(input_arg, chapter_number, force)
    else:
        print(f"📝 Processing direct text input")
        result = manual_parser.parse_response_text(input_arg, chapter_number, force)
    
    # Show results
    print("\n" + "="*40)
    if result['success']:
        print("✅ SUCCESS!")
        print(f"   Method: {result.get('method', 'unknown')}")
        print(f"   File: {result['chapter_file']}")
        print(f"   Title: {result['title']}")
        
        if 'extraction_method' in result:
            print(f"   Extraction: {result['extraction_method']}")
        
        if 'cleaning_notes' in result:
            for note in result['cleaning_notes']:
                print(f"   📝 {note}")
    else:
        print("❌ FAILED")
        if 'error' in result:
            print(f"   ⚠️  {result['error']}")
        if 'issues_found' in result:
            for issue in result['issues_found']:
                print(f"   ⚠️  {issue}")

def check_chapters():
    """Check for problematic chapters"""
    
    print("🔍 CHECKING FOR PROBLEMATIC CHAPTERS")
    print("="*45)
    
    from check_placeholder_chapters import check_placeholder_chapters
    
    results = check_placeholder_chapters()
    
    if results['problematic'] == 0:
        print("\n🎉 All chapters look good!")
    else:
        print(f"\n⚠️  Found {results['problematic']} problematic chapters")
        print("💡 Run 'python rescue_chapters.py batch' to attempt rescue")

if __name__ == "__main__":
    main()