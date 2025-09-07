#!/usr/bin/env python3
"""
Character Deduplication System for Infinity Mage Glossary

This script identifies and merges duplicate character entries where we have:
- Given name only (e.g., "시로네" → "Shirone") 
- Full name (e.g., "아리안 시로네" → "Arian Shirone")

The script merges them into the full name entry while preserving usage statistics.
"""

from infinity_glossary_manager import InfinityGlossaryManager
import json
from datetime import datetime

class CharacterDeduplicator:
    def __init__(self):
        self.manager = InfinityGlossaryManager()
        self.duplicates_found = []
        self.backup_created = False
    
    def create_backup(self):
        """Create backup of glossary before modifications"""
        if not self.backup_created:
            backup_path = f"translation_glossary_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(self.manager.glossary, f, ensure_ascii=False, indent=2)
            print(f"📄 Backup created: {backup_path}")
            self.backup_created = True
    
    def find_duplicates(self):
        """Find duplicate character entries"""
        characters = self.manager.glossary.get('characters', {})
        duplicates = []
        
        # Group characters by similar names
        processed = set()
        
        for korean1, data1 in characters.items():
            if korean1 in processed:
                continue
                
            english1 = data1.get('english', '').strip()
            name1 = data1.get('name', '').strip()
            surname1 = data1.get('surname', '').strip()
            
            if not english1:
                continue
            
            # Look for matches
            matches = [korean1]
            
            for korean2, data2 in characters.items():
                if korean2 in processed or korean1 == korean2:
                    continue
                    
                english2 = data2.get('english', '').strip()
                name2 = data2.get('name', '').strip()
                surname2 = data2.get('surname', '').strip()
                
                if not english2:
                    continue
                
                # Check if they represent the same character
                is_duplicate = False
                
                # Case 1: One is given name, other is full name
                if name1 and name2 and name1 == name2:
                    # Same given name
                    if (not surname1 and surname2) or (surname1 and not surname2):
                        is_duplicate = True
                    elif surname1 == surname2:
                        is_duplicate = True
                
                # Case 2: One name contains the other
                elif (name1 in english2 or name2 in english1) and abs(len(english1) - len(english2)) > 2:
                    is_duplicate = True
                
                if is_duplicate:
                    matches.append(korean2)
            
            if len(matches) > 1:
                # Sort by usage count to identify primary entry
                match_data = []
                for korean in matches:
                    data = characters[korean]
                    match_data.append({
                        'korean': korean,
                        'english': data.get('english', ''),
                        'usage_count': data.get('usage_count', 0),
                        'is_full_name': bool(data.get('surname', '').strip()),
                        'data': data
                    })
                
                # Sort by: 1) is full name, 2) usage count
                match_data.sort(key=lambda x: (x['is_full_name'], x['usage_count']), reverse=True)
                duplicates.append(match_data)
                
                for korean in matches:
                    processed.add(korean)
        
        return duplicates
    
    def merge_duplicates(self, duplicate_group, dry_run=True):
        """Merge a group of duplicate characters"""
        if len(duplicate_group) < 2:
            return None
            
        # Use the first entry (highest priority) as primary
        primary = duplicate_group[0]
        secondaries = duplicate_group[1:]
        
        primary_korean = primary['korean']
        primary_data = primary['data'].copy()
        
        merge_info = {
            'primary': f"{primary_korean} → {primary['english']}",
            'merged': [],
            'total_usage': primary['usage_count']
        }
        
        # Merge data from secondary entries
        all_chapters = set(primary_data.get('chapters_used', []))
        total_usage = primary_data.get('usage_count', 0)
        
        for secondary in secondaries:
            secondary_korean = secondary['korean']
            secondary_data = secondary['data']
            
            merge_info['merged'].append(f"{secondary_korean} → {secondary['english']} (usage: {secondary['usage_count']})")
            
            # Merge usage statistics
            total_usage += secondary_data.get('usage_count', 0)
            all_chapters.update(secondary_data.get('chapters_used', []))
            
            # Merge other useful data
            if not primary_data.get('context', '') and secondary_data.get('context', ''):
                primary_data['context'] = secondary_data['context']
            
            # Take the earliest first appearance
            if secondary_data.get('first_appearance', 999) < primary_data.get('first_appearance', 999):
                primary_data['first_appearance'] = secondary_data['first_appearance']
        
        # Update merged data
        primary_data['usage_count'] = total_usage
        primary_data['chapters_used'] = sorted(list(all_chapters))
        primary_data['last_used'] = max(all_chapters) if all_chapters else primary_data.get('last_used', 1)
        
        merge_info['total_usage'] = total_usage
        
        if not dry_run:
            # Update primary entry
            self.manager.glossary['characters'][primary_korean] = primary_data
            
            # Remove secondary entries
            for secondary in secondaries:
                secondary_korean = secondary['korean']
                if secondary_korean in self.manager.glossary['characters']:
                    del self.manager.glossary['characters'][secondary_korean]
            
            self.manager.save_glossary()
        
        return merge_info
    
    def run_deduplication(self, dry_run=True):
        """Run the complete deduplication process"""
        print("🔍 INFINITY MAGE CHARACTER DEDUPLICATION")
        print("=" * 50)
        
        if not dry_run:
            self.create_backup()
        
        print("🔍 Finding duplicate characters...")
        duplicates = self.find_duplicates()
        
        if not duplicates:
            print("✅ No duplicates found!")
            return
        
        print(f"📊 Found {len(duplicates)} duplicate groups")
        print()
        
        total_removed = 0
        
        for i, duplicate_group in enumerate(duplicates):
            print(f"📝 Group {i+1}:")
            
            merge_info = self.merge_duplicates(duplicate_group, dry_run=dry_run)
            if merge_info:
                print(f"   Primary: {merge_info['primary']} (total usage: {merge_info['total_usage']})")
                for merged in merge_info['merged']:
                    print(f"   Merging: {merged}")
                    total_removed += 1
                print()
        
        if dry_run:
            print(f"🔥 DRY RUN: Would remove {total_removed} duplicate entries")
            print("💡 Run with --apply to actually perform the merge")
        else:
            print(f"✅ Successfully removed {total_removed} duplicate entries")
            print("💾 Glossary updated and saved")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Deduplicate character entries in glossary')
    parser.add_argument('--apply', action='store_true', help='Actually perform the deduplication (default is dry run)')
    parser.add_argument('--backup', action='store_true', help='Create backup even for dry run')
    
    args = parser.parse_args()
    
    deduplicator = CharacterDeduplicator()
    
    if args.backup:
        deduplicator.create_backup()
    
    deduplicator.run_deduplication(dry_run=not args.apply)

if __name__ == "__main__":
    main()