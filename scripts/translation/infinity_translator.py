#!/usr/bin/env python3
"""
Main Orchestrator for Infinity Mage Translation
Coordinates complete translation workflow with chapter management and quality control
"""

import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import argparse

sys.path.append(str(Path(__file__).parent.parent))

from infinity_glossary_manager import InfinityGlossaryManager
from translation.infinity_prompt_generator import InfinityPromptGenerator
from translation.infinity_response_parser import InfinityResponseParser
from translation.infinity_automation_macro import InfinityAutomationMacro

class InfinityTranslator:
    def __init__(self, config_path: Optional[str] = None):
        # Load configuration
        self.project_root = Path(__file__).parent.parent.parent
        self.config = self._load_config(config_path)
        
        # Initialize core components
        self.glossary_manager = InfinityGlossaryManager(self.config.get('glossary_path'))
        self.prompt_generator = InfinityPromptGenerator(self.glossary_manager)
        self.response_parser = InfinityResponseParser(self.glossary_manager, self.config.get('output_dir', 'translated_chapters'))
        self.automation_macro = InfinityAutomationMacro()
        
        # Chapter tracking
        self.korean_chapters_dir = self.project_root / self.config.get('korean_chapters_dir')
        self.progress_file = self.project_root / 'data' / 'glossaries' / 'translation_progress.json'
        self.progress = self._load_progress()
        
        # Quality settings
        self.quality_checks_enabled = self.config.get('quality_checks_enabled', True)
        self.auto_backup = self.config.get('auto_backup', True)
        
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from file or create default"""
        
        default_config = {
            'version': '1.0',
            'korean_chapters_dir': 'data/source/chapters_raw',
            'output_dir': 'translated_chapters',
            'glossary_path': None,  # Will use default data/glossaries/ path
            'quality_checks_enabled': True,
            'auto_backup': True,
            'batch_size': 1,
            'wait_time_minutes': 3,
            'pastbin_api_key': '',
            'claude_cli_automation': True,
            'parallel_processing': False
        }
        if config_path is None:
            # Get the project root (parent of scripts directory)
            config_path = self.project_root / "data" / "glossaries" / "infinity_config.json"

        config_file = Path(config_path)
        
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    # Merge with defaults
                    config = {**default_config, **user_config}
                    return config
            except Exception as e:
                print(f"⚠️ Error loading config: {e}. Using defaults.")
        else:
            # Create default config file
            try:
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, indent=2, ensure_ascii=False)
                print(f"📝 Created default config: {config_file}")
            except Exception as e:
                print(f"⚠️ Could not create config file: {e}")
        
        return default_config
    
    def _load_progress(self) -> Dict:
        """Load translation progress tracking"""
        default_progress = {
            'last_translated_chapter': 0,
            'total_chapters': 1277,
            'completed_chapters': [],
            'failed_chapters': [],
            'skipped_chapters': [],
            'last_update': None,
            'statistics': {
                'total_terms_discovered': 0,
                'average_processing_time': 0,
                'quality_scores': []
            }
        }
        
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    progress = json.load(f)
                    # Merge with defaults for any missing keys
                    return {**default_progress, **progress}
            except Exception as e:
                print(f"⚠️ Error loading progress: {e}. Starting fresh.")
        
        return default_progress
    
    def _save_progress(self):
        """Save translation progress"""
        self.progress['last_update'] = datetime.now().isoformat()
        try:
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(self.progress, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Error saving progress: {e}")
    
    def get_korean_chapter_content(self, chapter_number: int) -> Optional[str]:
        """Load Korean chapter content from file"""
        # Try different filename patterns
        patterns = [
            f"Chapter - {chapter_number} - *.txt",
            f"Chapter_{chapter_number:03d}.txt",
            f"{chapter_number:03d}_*.txt",
            f"*{chapter_number}*.txt"
        ]
        
        for pattern in patterns:
            matching_files = list(self.korean_chapters_dir.glob(pattern))
            if matching_files:
                try:
                    with open(matching_files[0], 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if content:
                            print(f"📖 Loaded Korean content for Chapter {chapter_number}")
                            return content
                except Exception as e:
                    print(f"⚠️ Error reading {matching_files[0]}: {e}")
        
        print(f"❌ Korean content not found for Chapter {chapter_number}")
        return None
    
    def translate_single_chapter(self, chapter_number: int, volume_number: Optional[int] = None, 
                               use_automation: bool = True, wait_minutes: int = 3) -> Dict:
        """Translate a single chapter with full workflow"""
        
        print(f"\n{'='*70}")
        print(f"📖 TRANSLATING CHAPTER {chapter_number}")
        print(f"{'='*70}")
        
        start_time = time.time()
        
        result = {
            'success': False,
            'chapter_number': chapter_number,
            'volume_number': volume_number,
            'processing_time': 0,
            'files_created': [],
            'new_terms_count': 0,
            'errors': [],
            'warnings': []
        }
        
        try:
            # Load Korean content
            korean_content = self.get_korean_chapter_content(chapter_number)
            if not korean_content:
                result['errors'].append(f"Could not load Korean content for Chapter {chapter_number}")
                return result
            
            if use_automation:
                # Use full automation workflow
                automation_result = self.automation_macro.run_complete_workflow(
                    korean_content, chapter_number, volume_number, wait_minutes)
                
                result.update({
                    'success': automation_result['success'],
                    'files_created': automation_result['files_created'],
                    'errors': automation_result['errors']
                })
                
            else:
                # Manual workflow - generate prompt only
                print("🔄 Running manual workflow (prompt generation only)...")
                
                # Generate prompt
                prompt = self.prompt_generator.generate_translation_prompt(
                    korean_content, chapter_number, volume_number)
                
                # Save prompt to file
                prompt_file = f"manual_prompt_chapter_{chapter_number}.txt"
                with open(prompt_file, 'w', encoding='utf-8') as f:
                    f.write(prompt)
                
                result['files_created'].append(prompt_file)
                print(f"📝 Manual prompt saved to: {prompt_file}")
                print("🔧 Please manually:")
                print("  1. Copy the prompt to Claude CLI")
                print("  2. Save Claude's response to a file")
                print("  3. Run process_manual_response() with the response file")
                
                result['success'] = True  # Partial success
            
            # Update progress tracking
            processing_time = time.time() - start_time
            result['processing_time'] = processing_time
            
            if result['success']:
                if chapter_number not in self.progress['completed_chapters']:
                    self.progress['completed_chapters'].append(chapter_number)
                
                # Remove from failed if it was there
                if chapter_number in self.progress['failed_chapters']:
                    self.progress['failed_chapters'].remove(chapter_number)
                
                self.progress['last_translated_chapter'] = max(
                    self.progress['last_translated_chapter'], chapter_number)
                
                # Update statistics
                stats = self.progress['statistics']
                times = stats.get('processing_times', [])
                times.append(processing_time)
                stats['processing_times'] = times[-10:]  # Keep last 10
                stats['average_processing_time'] = sum(times) / len(times)
                
            else:
                if chapter_number not in self.progress['failed_chapters']:
                    self.progress['failed_chapters'].append(chapter_number)
            
            self._save_progress()
            
            print(f"\n⏱️ Processing time: {processing_time:.1f} seconds")
            
        except Exception as e:
            result['errors'].append(f"Unexpected error: {str(e)}")
            print(f"❌ Unexpected error: {e}")
        
        return result
    
    def translate_chapter_range(self, start_chapter: int, end_chapter: int, 
                              skip_completed: bool = True, use_automation: bool = True) -> List[Dict]:
        """Translate a range of chapters"""
        
        print(f"\n{'='*70}")
        print(f"📚 BATCH TRANSLATION: CHAPTERS {start_chapter}-{end_chapter}")
        print(f"{'='*70}")
        
        results = []
        
        for chapter_num in range(start_chapter, end_chapter + 1):
            # Skip if already completed
            if skip_completed and chapter_num in self.progress['completed_chapters']:
                print(f"⏭️ Skipping Chapter {chapter_num} (already completed)")
                continue
            
            # Translate chapter
            result = self.translate_single_chapter(
                chapter_num, 
                volume_number=self._get_volume_for_chapter(chapter_num),
                use_automation=use_automation,
                wait_minutes=self.config.get('wait_time_minutes', 3)
            )
            
            results.append(result)
            
            # Pause between chapters to avoid overwhelming Claude
            if chapter_num < end_chapter:
                pause_time = self.config.get('chapter_pause_seconds', 10)
                print(f"⏸️ Pausing {pause_time} seconds before next chapter...")
                time.sleep(pause_time)
        
        # Generate batch report
        self._generate_batch_report(results)
        return results
    
    def _get_volume_for_chapter(self, chapter_number: int) -> int:
        """Estimate volume number based on chapter number"""
        # Rough estimation - adjust based on actual volume structure
        if chapter_number <= 50:
            return 1
        elif chapter_number <= 100:
            return 2
        elif chapter_number <= 150:
            return 3
        # Continue pattern...
        else:
            return (chapter_number - 1) // 50 + 1
    
    def process_manual_response(self, response_file: str, chapter_number: int, 
                              volume_number: Optional[int] = None) -> Dict:
        """Process a manually saved Claude response"""
        
        print(f"🔄 Processing manual response for Chapter {chapter_number}...")
        
        try:
            # Load response
            with open(response_file, 'r', encoding='utf-8') as f:
                response_content = f.read()
            
            # Load original Korean
            korean_content = self.get_korean_chapter_content(chapter_number)
            if not korean_content:
                return {'success': False, 'error': 'Korean content not found'}
            
            # Process through response parser
            result = self.response_parser.process_complete_response(
                response_content, korean_content, chapter_number, volume_number)
            
            if result['success']:
                # Update progress
                if chapter_number not in self.progress['completed_chapters']:
                    self.progress['completed_chapters'].append(chapter_number)
                self.progress['last_translated_chapter'] = max(
                    self.progress['last_translated_chapter'], chapter_number)
                self._save_progress()
            
            return result
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_translation_status(self) -> Dict:
        """Get current translation status and statistics"""
        completed = len(self.progress['completed_chapters'])
        total = self.progress['total_chapters']
        failed = len(self.progress['failed_chapters'])
        
        stats = self.glossary_manager.get_statistics()
        
        return {
            'progress': {
                'completed_chapters': completed,
                'total_chapters': total,
                'completion_percentage': (completed / total) * 100,
                'failed_chapters': failed,
                'last_translated': self.progress['last_translated_chapter']
            },
            'glossary_stats': stats,
            'processing_stats': self.progress['statistics']
        }
    
    def _generate_batch_report(self, results: List[Dict]):
        """Generate comprehensive batch processing report"""
        
        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]
        
        report_lines = [
            "# Infinity Mage Batch Translation Report",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Summary",
            f"- **Total Chapters**: {len(results)}",
            f"- **Successful**: {len(successful)}",
            f"- **Failed**: {len(failed)}",
            f"- **Success Rate**: {(len(successful)/len(results)*100):.1f}%",
            ""
        ]
        
        if successful:
            avg_time = sum(r['processing_time'] for r in successful) / len(successful)
            total_terms = sum(r.get('new_terms_count', 0) for r in successful)
            
            report_lines.extend([
                "## Performance",
                f"- **Average Processing Time**: {avg_time:.1f} seconds",
                f"- **Total New Terms Discovered**: {total_terms}",
                f"- **Total Files Created**: {sum(len(r['files_created']) for r in successful)}",
                ""
            ])
        
        if successful:
            report_lines.append("## Successful Chapters")
            for result in successful:
                chapter = result['chapter_number']
                time_taken = result['processing_time']
                files = len(result['files_created'])
                report_lines.append(f"- **Chapter {chapter}**: {time_taken:.1f}s, {files} files created")
            report_lines.append("")
        
        if failed:
            report_lines.append("## Failed Chapters")
            for result in failed:
                chapter = result['chapter_number']
                errors = ', '.join(result['errors'][:2])  # Show first 2 errors
                report_lines.append(f"- **Chapter {chapter}**: {errors}")
            report_lines.append("")
        
        # Current status
        status = self.get_translation_status()
        report_lines.extend([
            "## Overall Progress",
            f"- **Completed Chapters**: {status['progress']['completed_chapters']}/{status['progress']['total_chapters']}",
            f"- **Completion**: {status['progress']['completion_percentage']:.1f}%",
            f"- **Total Terms in Glossary**: {status['glossary_stats'].get('total_terms', 0)}",
        ])
        
        # Save report
        report_file = f"batch_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(report_lines))
            print(f"📊 Batch report saved to: {report_file}")
        except Exception as e:
            print(f"⚠️ Could not save batch report: {e}")

def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="Infinity Mage Translation Orchestrator")
    parser.add_argument('command', choices=['single', 'range', 'status', 'process-manual'], 
                       help='Command to execute')
    parser.add_argument('--chapter', type=int, help='Chapter number (for single)')
    parser.add_argument('--start', type=int, help='Start chapter (for range)')
    parser.add_argument('--end', type=int, help='End chapter (for range)')
    parser.add_argument('--volume', type=int, help='Volume number')
    parser.add_argument('--no-automation', action='store_true', help='Disable automation (manual mode)')
    parser.add_argument('--wait', type=int, default=3, help='Wait time in minutes (default: 3)')
    parser.add_argument('--response-file', help='Response file path (for process-manual)')
    
    args = parser.parse_args()
    
    translator = InfinityTranslator()

    # print("⏳ Initializing... Please wait.")
    # for _ in range(90):
    #     pyautogui.moveTo(100, 100)
    #     time.sleep(60)
    #     pyautogui.moveTo(200, 200)
    #     time.sleep(60)
    # print("✅ Initialization complete.")
    
    if args.command == 'single':
        if not args.chapter:
            print("❌ --chapter required for single command")
            sys.exit(1)
        
        result = translator.translate_single_chapter(
            args.chapter, 
            args.volume, 
            use_automation=not args.no_automation,
            wait_minutes=args.wait
        )
        
        if result['success']:
            print(f"✅ Chapter {args.chapter} translated successfully!")
        else:
            print(f"❌ Chapter {args.chapter} translation failed:")
            for error in result['errors']:
                print(f"  - {error}")
            sys.exit(1)
    
    elif args.command == 'range':
        if not args.start or not args.end:
            print("❌ --start and --end required for range command")
            sys.exit(1)
        
        results = translator.translate_chapter_range(
            args.start, 
            args.end, 
            use_automation=not args.no_automation
        )
        
        successful = sum(1 for r in results if r['success'])
        print(f"✅ Batch complete: {successful}/{len(results)} chapters successful")
    
    elif args.command == 'status':
        status = translator.get_translation_status()
        print("\n📊 TRANSLATION STATUS")
        print("=" * 50)
        print(f"Completed: {status['progress']['completed_chapters']}/{status['progress']['total_chapters']} ({status['progress']['completion_percentage']:.1f}%)")
        print(f"Failed: {status['progress']['failed_chapters']}")
        print(f"Last translated: Chapter {status['progress']['last_translated']}")
        print(f"Total terms in glossary: {status['glossary_stats'].get('total_terms', 0)}")
    
    elif args.command == 'process-manual':
        if not args.response_file or not args.chapter:
            print("❌ --response-file and --chapter required for process-manual command")
            sys.exit(1)
        
        result = translator.process_manual_response(args.response_file, args.chapter, args.volume)
        
        if result['success']:
            print(f"✅ Manual response processed successfully for Chapter {args.chapter}!")
        else:
            print(f"❌ Processing failed: {result.get('error', 'Unknown error')}")
            sys.exit(1)

if __name__ == "__main__":
    main()