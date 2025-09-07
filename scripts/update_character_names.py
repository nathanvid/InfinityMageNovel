#!/usr/bin/env python3
"""
Character Name/Surname Management Script
Use this script to update character names and surnames in the glossary
"""

from infinity_glossary_manager import InfinityGlossaryManager

def show_all_characters():
    """Show all characters with their current names and surnames"""
    manager = InfinityGlossaryManager()
    
    print("=== CURRENT CHARACTERS ===")
    characters = manager.glossary.get('characters', {})
    
    for korean, data in characters.items():
        name = data.get('name', '')
        surname = data.get('surname', '')
        english = data.get('english', '')
        
        print(f"Korean: {korean}")
        print(f"  English: {english}")
        print(f"  Name: '{name}' | Surname: '{surname}'")
        print(f"  Gender: {data.get('gender', 'unknown')}")
        print()

def update_character(korean_name, name=None, surname=None):
    """Update a character's name and/or surname"""
    manager = InfinityGlossaryManager()
    return manager.update_character_name(korean_name, name, surname)

# Example usage functions
def example_updates():
    """Example of how to update character names"""
    print("=== EXAMPLE UPDATES ===")
    
    # Example: If we discover a character's full name
    # update_character('시로네', name='Sirone', surname='Arian')
    
    # Example: If we discover someone has a title that should be part of their surname
    # update_character('알페아스', name='Alpheas', surname='von Arcane')
    
    print("Uncomment the lines above to test updates")
    print()
    
if __name__ == "__main__":
    show_all_characters()
    example_updates()
    
    print("=== USAGE INSTRUCTIONS ===")
    print("To update character names, use the update_character function:")
    print("update_character('korean_name', name='FirstName', surname='LastName')")
    print("- You can update just name, just surname, or both")
    print("- Set surname='' to clear a surname")
    print("- The English translation will be automatically updated")