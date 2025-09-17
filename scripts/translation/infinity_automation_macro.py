#!/usr/bin/env python3
"""
Full Automation Macro for Infinity Mage Translation
Handles complete workflow: prompt generation → clipboard → Arc → Claude CLI → response processing
"""

import time
import subprocess
import sys
from pathlib import Path
from typing import Dict, Optional
import pyautogui
import pyperclip
from infinity_glossary_manager import InfinityGlossaryManager
from infinity_prompt_generator import InfinityPromptGenerator
from infinity_response_parser import InfinityResponseParser

class InfinityAutomationMacro:
    def __init__(self):

        self.project_root = Path(__file__).parent.parent.parent
        # Initialize core components
        self.glossary_manager = InfinityGlossaryManager()
        self.prompt_generator = InfinityPromptGenerator(self.glossary_manager)
        self.response_parser = InfinityResponseParser(self.glossary_manager)
        
        # Automation settings
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.5
        
        # Configuration
        self.wait_time_seconds = 180  # 3 minutes default
        self.max_retries = 3
    
    def save_prompt_to_clipboard(self, content: str) -> bool:
        """Save prompt content directly to clipboard"""
        try:
            # Copy to clipboard using pyperclip
            pyperclip.copy(content)
            print(f"📋 Prompt copied to clipboard ({len(content)} characters)")
            
            # Also save locally as backup
            backup_file = Path(f"prompts/prompt_backup_{int(time.time())}.txt")
            try:
                with open(backup_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"💾 Backup saved to: {backup_file}")
            except Exception as e:
                print(f"⚠️ Backup save failed: {e}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error copying to clipboard: {e}")
            # Fallback: save to file and tell user to copy manually
            fallback_file = Path(f"prompt_manual_{int(time.time())}.txt")
            try:
                with open(fallback_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"💾 Clipboard failed - prompt saved to: {fallback_file}")
                print("🔧 Please manually copy the content from this file")
                return False
            except Exception as file_e:
                print(f"❌ Complete failure - could not save prompt: {file_e}")
                return False
    
    def trigger_capslock_a_shortcut(self) -> bool:
        """Trigger CapsLock+A shortcut to open Arc browser"""
        try:
            print("🌐 Triggering CapsLock+A shortcut to open Arc...")
            
            # Method 1: Use AppleScript (most reliable on macOS)
            applescript = '''
                tell application "System Events"
                    tell application "Arc" to activate
                end tell
            '''
            subprocess.run(['osascript', '-e', applescript], check=True)
            time.sleep(2)
            
            print("✅ Arc browser activated")
            return True
            
        except subprocess.CalledProcessError:
            try:
                # Method 2: Use keyboard simulation
                print("🔄 Trying keyboard simulation...")
                pyautogui.hotkey('capslock', 'a')
                time.sleep(2)
                return True
            except Exception as e:
                print(f"❌ Failed to trigger shortcut: {e}")
                return False
    
    def find_and_click_plus_button(self) -> bool:
        
        try:
            # Check if there's a clickable element at this position
            pyautogui.click(41, 144)  # Move mouse to position
            time.sleep(1)
            
            # Simple verification - assume click was successful
            print("✅ Successfully clicked + button to open Claude CLI")
            return True
            
        except Exception:
            pass
        return False
                
    
    def paste_prompt_and_submit(self) -> bool:
        """Paste prompt content and submit to Claude CLI"""
        try:
            print("📝 Pasting prompt to Claude CLI...")

            pyautogui.click(600, 400)
            time.sleep(0.5)

            # pyautogui.click(818,  534)  # Click input area
            # time.sleep(0.5)

            
            # Paste content
            pyautogui.hotkey('command', 'v')
            time.sleep(1)
            
            # Submit (Enter or specific submit button)
            pyautogui.press('enter')
            
            print("✅ Prompt pasted and submitted")
            return True  
        except Exception as e:
            print(f"❌ Error in paste_prompt_and_submit: {e}")
            return False
    
    def wait_for_response(self, wait_minutes: int = 3) -> bool:
        """Wait for Claude to generate response with progress indication"""
        total_seconds = wait_minutes * 60
        
        print(f"⏳ Waiting {wait_minutes} minutes for Claude to respond...")
        
        for i in range(total_seconds):
            remaining_minutes = (total_seconds - i) // 60
            remaining_seconds = (total_seconds - i) % 60
            
            if i % 30 == 0:  # Update every 30 seconds
                if remaining_minutes > 0:
                    print(f"⏰ {remaining_minutes}m {remaining_seconds}s remaining...")
                else:
                    print(f"⏰ {remaining_seconds}s remaining...")
            
            time.sleep(1)
        
        print("✅ Wait complete! Claude should have responded.")
        return True
    
    def copy_claude_response(self) -> Optional[str]:
        """Copy Claude's response from the interface"""
        try:
            print("📋 Copying Claude's response...")
            
            pyautogui.click(760, 791)
            time.sleep(2)

            pyautogui.click(755, 747)
            time.sleep(2)

            pyautogui.click(930, 759)
            time.sleep(1)

            pyautogui.click(930, 724)
            time.sleep(1)

            pyautogui.click(1262, 80)
            time.sleep(1)

            
            # Get content from clipboard
            response = pyperclip.paste()
            
            if response and len(response.strip()) > 100:  # Reasonable response length
                print(f"✅ Successfully copied response ({len(response)} characters)")
                return response
            
            print("❌ Could not copy Claude's response")
            return None
            
        except Exception as e:
            print(f"❌ Error copying response: {e}")
            return None
    
    def save_response_for_processing(self, response: str, chapter_number: int) -> str:
        """Save response to file for processing"""
        timestamp = int(time.time())
        filename = f"responses/claude_response_chapter_{chapter_number}_{timestamp}.txt"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(response)
            
            print(f"💾 Response saved to: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ Error saving response: {e}")
            return ""
    
    def run_complete_workflow(self, korean_text: str, chapter_number: int, 
                            volume_number: Optional[int] = None, 
                            wait_minutes: int = 2) -> Dict:
        """Run complete automation workflow for one chapter"""
        
        print("=" * 70)
        print(f"🚀 INFINITY MAGE AUTOMATION WORKFLOW - CHAPTER {chapter_number}")
        print("=" * 70)
        
        workflow_result = {
            'success': False,
            'chapter_number': chapter_number,
            'steps_completed': [],
            'errors': [],
            'files_created': []
        }
        
        try:
            # Step 1: Generate prompt
            print("\n📝 STEP 1: Generating translation prompt...")
            prompt = self.prompt_generator.generate_translation_prompt(
                korean_text, chapter_number, volume_number)
            workflow_result['steps_completed'].append('prompt_generated')
            print("✅ Translation prompt generated")
            
            # Step 2: Save to Clipboard
            print("\n📋 STEP 2: Saving prompt to clipboard...")
            if not self.save_prompt_to_clipboard(prompt):
                workflow_result['errors'].append("Failed to save prompt to clipboard")
                return workflow_result
            
            workflow_result['steps_completed'].append('prompt_saved_to_clipboard')
            print("✅ Prompt saved to clipboard and backup file created")
            
            # Step 3: Open Arc browser
            print("\n🌐 STEP 3: Opening Arc browser...")
            if not self.trigger_capslock_a_shortcut():
                workflow_result['errors'].append("Failed to open Arc browser")
                print("⚠️ Please manually open Arc browser and continue")
            else:
                workflow_result['steps_completed'].append('arc_opened')
            
            # Step 4: Find and click + button
            print("\n🔍 STEP 4: Opening new Claude CLI prompt...")
            if not self.find_and_click_plus_button():
                workflow_result['errors'].append("Failed to open Claude CLI")
                print("⚠️ Please manually navigate to Claude CLI and continue")
            else:
                workflow_result['steps_completed'].append('claude_cli_opened')
            
            # Step 5: Paste prompt
            print("\n📤 STEP 5: Pasting prompt to Claude CLI...")
            if not self.paste_prompt_and_submit():
                workflow_result['errors'].append("Failed to paste prompt")
                print("⚠️ Please manually paste the prompt from clipboard")
                print("📋 Prompt is available in clipboard (Cmd+V to paste)")
            else:
                workflow_result['steps_completed'].append('prompt_submitted')
            
            # Step 6: Wait for response
            print(f"\n⏳ STEP 6: Waiting {wait_minutes} minutes for Claude response...")
            self.wait_for_response(wait_minutes)
            workflow_result['steps_completed'].append('wait_completed')
            
            # Step 7: Copy response
            print("\n📋 STEP 7: Copying Claude's response...")
            response = self.copy_claude_response()

            response_file_path = self.project_root / "data/responses/prompt_answer{chapter_number}.txt"
            with response_file_path.open("w", encoding="utf-8") as f:
                f.write(response if response else "No response captured")
            
            if not response:
                workflow_result['errors'].append("Failed to copy response")
                print("⚠️ Please manually copy Claude's response")
                return workflow_result
            
            workflow_result['steps_completed'].append('response_copied')
            
            # Step 8: Save response for processing
            print("\n💾 STEP 8: Saving response...")
            response_file = self.save_response_for_processing(response, chapter_number)
            if response_file:
                workflow_result['files_created'].append(response_file)
                workflow_result['steps_completed'].append('response_saved')
            
            # Step 9: Process response
            print("\n🔄 STEP 9: Processing translation response...")
            processing_result = self.response_parser.process_complete_response(
                response, korean_text, chapter_number, volume_number)
            
            if processing_result['success']:
                workflow_result['steps_completed'].append('response_processed')
                workflow_result['files_created'].append(processing_result['chapter_file'])
                workflow_result['success'] = True
                
                print(f"\n🎉 WORKFLOW COMPLETE FOR CHAPTER {chapter_number}!")
                print(f"📖 Chapter saved: {processing_result['chapter_file']}")
                print(f"📝 New terms added: {processing_result['new_terms_count']}")
                
            else:
                workflow_result['errors'].extend(processing_result['errors'])
                print("❌ Response processing failed")
            
        except KeyboardInterrupt:
            print("\n🛑 Workflow interrupted by user")
            workflow_result['errors'].append("Workflow interrupted")
            
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            workflow_result['errors'].append(f"Unexpected error: {str(e)}")
        
        # Print workflow summary
        print("\n" + "=" * 70)
        print("📊 WORKFLOW SUMMARY")
        print("=" * 70)
        print(f"✅ Steps completed: {len(workflow_result['steps_completed'])}")
        print(f"❌ Errors: {len(workflow_result['errors'])}")
        print(f"📁 Files created: {len(workflow_result['files_created'])}")
        
        if workflow_result['errors']:
            print("\n❌ ERRORS:")
            for error in workflow_result['errors']:
                print(f"  - {error}")
        
        if workflow_result['files_created']:
            print("\n📁 FILES CREATED:")
            for file in workflow_result['files_created']:
                print(f"  - {file}")
        
        return workflow_result

def main():
    """Test the automation macro"""
    if len(sys.argv) < 2:
        print("Usage: python infinity_automation_macro.py <chapter_number> [wait_minutes]")
        print("Example: python infinity_automation_macro.py 1 3")
        sys.exit(1)
    
    try:
        chapter_number = int(sys.argv[1])
        wait_minutes = int(sys.argv[2]) if len(sys.argv) > 2 else 2
        
        # Load Korean text (this would normally come from file)
        korean_text = """제1장 - 마법을 만나다 (1)

시로네는 알페아스 마법학교에서 마법을 배우고 있었다. 그는 천재적인 재능을 가진 소년이었지만, 아직 자신의 진정한 힘을 깨닫지 못했다.

"시로네, 오늘 수업에서 광구를 만들어보자." 선생님이 말했다.

시로네는 집중하며 마법을 시전했다. 그의 손에서 빛나는 구체가 나타났다."""
        
        # Run automation
        macro = InfinityAutomationMacro()
        result = macro.run_complete_workflow(korean_text, chapter_number, 1, wait_minutes)
        
        if result['success']:
            print("\n🎊 Automation completed successfully!")
        else:
            print("\n❌ Automation completed with errors.")
            sys.exit(1)
            
    except ValueError:
        print("❌ Invalid chapter number or wait time")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Automation stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()