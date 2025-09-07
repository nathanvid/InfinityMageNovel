#!/usr/bin/env python3
"""
Configuration System for Infinity Mage Translation
Manages settings, API keys, and system configuration
"""

import json
import os
from pathlib import Path
from typing import Dict, Optional, Any

class InfinityConfig:
    def __init__(self, config_file: str = "infinity_config.json"):
        self.config_file = Path(config_file)
        self.config = self._load_or_create_config()
        
    def _load_or_create_config(self) -> Dict:
        """Load existing config or create default configuration"""
        
        default_config = {
            "version": "1.0",
            "created_date": "2024-01-01",
            
            # File Paths
            "paths": {
                "korean_chapters_dir": "Infinity Mage Chapters 1-1277",
                "translated_chapters_dir": "translated_chapters",
                "glossary_file": "translation_glossary.json",
                "progress_file": "translation_progress.json",
                "backup_dir": "backups"
            },
            
            # Translation Settings
            "translation": {
                "quality_checks_enabled": True,
                "consistency_validation": True,
                "auto_backup": True,
                "batch_size": 1,
                "wait_time_minutes": 3,
                "chapter_pause_seconds": 30,
                "max_terms_per_category": 15,
                "context_chapters": 10
            },
            
            # Automation Settings
            "automation": {
                "claude_cli_automation": True,
                "pastbin_integration": True,
                "arc_browser_shortcut": "capslock+a",
                "max_retries": 3,
                "screenshot_debugging": False,
                "element_detection_timeout": 10
            },
            
            # API Keys (empty by default for security)
            "api_keys": {
                "pastbin_api_key": ""
            },
            
            # Quality Control
            "quality": {
                "minimum_translation_length": 100,
                "maximum_translation_ratio": 3.0,
                "minimum_translation_ratio": 0.5,
                "require_consistency_check": True,
                "auto_detect_korean_text": True,
                "placeholder_detection": True
            },
            
            # Output Format
            "output": {
                "markdown_format": True,
                "include_metadata": True,
                "date_format": "%Y-%m-%d",
                "filename_pattern": "chapter_{chapter:03d}.md",
                "volume_filename_pattern": "volume_{volume:02d}_chapter_{chapter:03d}.md"
            },
            
            # Glossary Settings
            "glossary": {
                "auto_update": True,
                "backup_on_update": True,
                "export_readable": True,
                "track_usage_statistics": True,
                "validate_consistency": True,
                "gender_validation": True
            },
            
            # Debug Settings
            "debug": {
                "verbose_logging": False,
                "save_prompts": True,
                "save_responses": True,
                "timing_analysis": False,
                "error_screenshots": True
            }
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    merged_config = self._merge_configs(default_config, loaded_config)
                    return merged_config
            except Exception as e:
                print(f"⚠️ Error loading config {self.config_file}: {e}")
                print("🔧 Creating new config with defaults...")
        
        # Create new config file
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
            print(f"📝 Created new configuration: {self.config_file}")
        except Exception as e:
            print(f"❌ Could not create config file: {e}")
        
        return default_config
    
    def _merge_configs(self, default: Dict, loaded: Dict) -> Dict:
        """Recursively merge loaded config with defaults"""
        result = default.copy()
        
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """Get configuration value using dot notation (e.g., 'translation.wait_time_minutes')"""
        keys = key_path.split('.')
        value = self.config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path: str, value: Any, save: bool = True) -> bool:
        """Set configuration value using dot notation"""
        keys = key_path.split('.')
        config_ref = self.config
        
        try:
            # Navigate to the parent of the target key
            for key in keys[:-1]:
                if key not in config_ref:
                    config_ref[key] = {}
                config_ref = config_ref[key]
            
            # Set the final value
            config_ref[keys[-1]] = value
            
            if save:
                self.save()
            
            return True
            
        except Exception as e:
            print(f"❌ Error setting config {key_path}: {e}")
            return False
    
    def save(self) -> bool:
        """Save current configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ Error saving config: {e}")
            return False
    
    def setup_api_keys(self):
        """Interactive setup for API keys"""
        print("🔐 API KEY SETUP")
        print("=" * 40)
        
        # Pastbin API Key
        current_pastbin = self.get('api_keys.pastbin_api_key', '')
        if current_pastbin:
            print(f"Current Pastbin API Key: {current_pastbin[:10]}...")
        else:
            print("Current Pastbin API Key: Not set")
        
        new_pastbin = input("Enter new Pastbin API Key (or press Enter to keep current): ").strip()
        if new_pastbin:
            self.set('api_keys.pastbin_api_key', new_pastbin)
            print("✅ Pastbin API key updated")
        
        
        self.save()
        print("💾 Configuration saved")
    
    def validate_setup(self) -> Dict[str, bool]:
        """Validate that all required components are properly configured"""
        validation_results = {}
        
        # Check file paths
        korean_dir = Path(self.get('paths.korean_chapters_dir'))
        validation_results['korean_chapters_exist'] = korean_dir.exists()
        
        translated_dir = Path(self.get('paths.translated_chapters_dir'))
        validation_results['output_dir_writable'] = self._test_directory_writable(translated_dir)
        
        # Check glossary
        glossary_file = Path(self.get('paths.glossary_file'))
        validation_results['glossary_accessible'] = self._test_file_accessible(glossary_file)
        
        # Check API keys
        pastbin_key = self.get('api_keys.pastbin_api_key', '')
        validation_results['pastbin_configured'] = bool(pastbin_key)
        
        # Check dependencies
        validation_results['dependencies_installed'] = self._check_dependencies()
        
        return validation_results
    
    def _test_directory_writable(self, directory: Path) -> bool:
        """Test if directory is writable"""
        try:
            directory.mkdir(parents=True, exist_ok=True)
            test_file = directory / '.test_write'
            test_file.write_text('test')
            test_file.unlink()
            return True
        except Exception:
            return False
    
    def _test_file_accessible(self, file: Path) -> bool:
        """Test if file is accessible (readable/writable)"""
        try:
            if file.exists():
                # Test read
                with open(file, 'r', encoding='utf-8') as f:
                    f.read(1)
                
                # Test write (append mode to not overwrite)
                with open(file, 'a', encoding='utf-8') as f:
                    pass
            else:
                # Test create
                file.parent.mkdir(parents=True, exist_ok=True)
                file.write_text('{}')
            
            return True
        except Exception:
            return False
    
    def _check_dependencies(self) -> bool:
        """Check if required Python dependencies are installed"""
        required_modules = [
            'pyautogui',
            'pyperclip', 
            'requests'
        ]
        
        for module in required_modules:
            try:
                __import__(module)
            except ImportError:
                return False
        
        return True
    
    def print_setup_report(self):
        """Print comprehensive setup validation report"""
        validation = self.validate_setup()
        
        print("\n🔍 INFINITY MAGE SETUP VALIDATION")
        print("=" * 50)
        
        status_icon = lambda x: "✅" if x else "❌"
        
        print(f"{status_icon(validation['korean_chapters_exist'])} Korean chapters directory: {self.get('paths.korean_chapters_dir')}")
        print(f"{status_icon(validation['output_dir_writable'])} Output directory writable: {self.get('paths.translated_chapters_dir')}")
        print(f"{status_icon(validation['glossary_accessible'])} Glossary file accessible: {self.get('paths.glossary_file')}")
        print(f"{status_icon(validation['pastbin_configured'])} Pastbin API key configured")
        print(f"{status_icon(validation['dependencies_installed'])} Python dependencies installed")
        
        all_good = all(validation.values())
        print(f"\n{'🎉 SETUP COMPLETE!' if all_good else '⚠️ SETUP ISSUES DETECTED'}")
        
        if not all_good:
            print("\n📝 SETUP RECOMMENDATIONS:")
            if not validation['korean_chapters_exist']:
                print(f"  - Create or verify Korean chapters directory: {self.get('paths.korean_chapters_dir')}")
            if not validation['output_dir_writable']:
                print(f"  - Ensure output directory is writable: {self.get('paths.translated_chapters_dir')}")
            if not validation['glossary_accessible']:
                print(f"  - Check glossary file permissions: {self.get('paths.glossary_file')}")
            if not validation['pastbin_configured']:
                print("  - Run: python infinity_config.py --setup-keys to configure API keys")
            if not validation['dependencies_installed']:
                print("  - Run: pip install pyautogui pyperclip requests")
    
    def export_config_template(self, template_file: str = "infinity_config_template.json"):
        """Export a template configuration file with comments"""
        template = {
            "_comment": "Infinity Mage Translation Configuration Template",
            "_instructions": "Copy this file to infinity_config.json and customize the values",
            
            "version": "1.0",
            
            "paths": {
                "_comment": "File and directory paths",
                "korean_chapters_dir": "Infinity Mage Chapters 1-1277",
                "translated_chapters_dir": "translated_chapters", 
                "glossary_file": "translation_glossary.json",
                "progress_file": "translation_progress.json",
                "backup_dir": "backups"
            },
            
            "translation": {
                "_comment": "Translation behavior settings",
                "wait_time_minutes": 3,
                "batch_size": 1,
                "max_terms_per_category": 15,
                "context_chapters": 10
            },
            
            "automation": {
                "_comment": "Automation and GUI settings",
                "claude_cli_automation": True,
                "pastbin_integration": True,
                "arc_browser_shortcut": "capslock+a",
                "max_retries": 3
            },
            
            "api_keys": {
                "_comment": "API keys - KEEP SECURE! Add to environment variables or this file",
                "_security_note": "Consider using environment variables: PASTBIN_API_KEY",
                "pastbin_api_key": "YOUR_PASTBIN_API_KEY_HERE"
            },
            
            "quality": {
                "_comment": "Quality control settings",
                "minimum_translation_length": 100,
                "require_consistency_check": True,
                "auto_detect_korean_text": True
            }
        }
        
        try:
            with open(template_file, 'w', encoding='utf-8') as f:
                json.dump(template, f, indent=2, ensure_ascii=False)
            print(f"📝 Configuration template exported to: {template_file}")
        except Exception as e:
            print(f"❌ Error exporting template: {e}")

def main():
    """CLI interface for configuration management"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Infinity Mage Configuration Manager")
    parser.add_argument('--setup-keys', action='store_true', help='Interactive API key setup')
    parser.add_argument('--validate', action='store_true', help='Validate current setup')
    parser.add_argument('--export-template', action='store_true', help='Export configuration template')
    parser.add_argument('--get', help='Get configuration value (dot notation)')
    parser.add_argument('--set', nargs=2, metavar=('KEY', 'VALUE'), help='Set configuration value')
    
    args = parser.parse_args()
    
    config = InfinityConfig()
    
    if args.setup_keys:
        config.setup_api_keys()
    
    elif args.validate:
        config.print_setup_report()
    
    elif args.export_template:
        config.export_config_template()
    
    elif args.get:
        value = config.get(args.get)
        print(f"{args.get} = {value}")
    
    elif args.set:
        key, value = args.set
        # Try to parse as JSON for complex values
        try:
            parsed_value = json.loads(value)
        except json.JSONDecodeError:
            parsed_value = value
        
        if config.set(key, parsed_value):
            print(f"✅ Set {key} = {parsed_value}")
        else:
            print(f"❌ Failed to set {key}")
    
    else:
        # Default: show current configuration summary
        print("⚙️ INFINITY MAGE CONFIGURATION")
        print("=" * 40)
        print(f"Config file: {config.config_file}")
        print(f"Korean chapters: {config.get('paths.korean_chapters_dir')}")
        print(f"Output directory: {config.get('paths.translated_chapters_dir')}")
        print(f"Wait time: {config.get('translation.wait_time_minutes')} minutes")
        print(f"Automation enabled: {config.get('automation.claude_cli_automation')}")
        print(f"Quality checks: {config.get('translation.quality_checks_enabled')}")
        
        print("\n📋 Available commands:")
        print("  --validate         Validate setup")
        print("  --setup-keys      Configure API keys")
        print("  --export-template Export config template")

if __name__ == "__main__":
    main()