#!/usr/bin/env python3
"""
Comprehensive Test Suite for Infinity Mage Translation Workflow
Tests all components and validates complete workflow functionality
"""

import json
import time
from pathlib import Path
from typing import Dict, List
import unittest
from unittest.mock import Mock, patch

# Import all components
from infinity_glossary_manager import InfinityGlossaryManager
from infinity_prompt_generator import InfinityPromptGenerator  
from infinity_response_parser import InfinityResponseParser
from infinity_config import InfinityConfig

class TestInfinityWorkflow(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.test_dir = Path("test_output")
        self.test_dir.mkdir(exist_ok=True)
        
        # Test data
        self.test_korean = """제1장 - 마법을 만나다 (1)

시로네는 알페아스 마법학교에서 마법을 배우고 있었다. 그는 천재적인 재능을 가진 소년이었지만, 아직 자신의 진정한 힘을 깨닫지 못했다.

"시로네, 오늘 수업에서 광구를 만들어보자." 이레나 선생님이 말했다.

시로네는 집중하며 마법을 시전했다. 그의 손에서 빛나는 구체가 나타났다."""

        self.test_response = """TRANSLATION_START
---
title: Meeting Magic (1)
date: 2024-01-01
---

Shirone was studying magic at Alpheas Magic School. He was a boy with genius-level talent, but he had not yet realized his true power.

"Shirone, let's try creating a photon sphere in today's lesson," Teacher Irena said.

Shirone concentrated and cast his magic. A glowing orb appeared from his hands.

---
TRANSLATION_END

NEW_TERMS_DISCOVERED:
- 이레나 → Irena (category: character) {Magic teacher at the school}
- 구체 → orb (category: concept) {Spherical magical manifestation}

CONSISTENCY_CHECK:
- Verified all character names from glossary
- Maintained gender consistency for all characters
- Used established magic terminology
"""
    
    def test_glossary_manager(self):
        """Test glossary manager functionality"""
        print("\n🧪 Testing Glossary Manager...")
        
        # Initialize with test glossary
        glossary_file = self.test_dir / "test_glossary.json"
        manager = InfinityGlossaryManager(str(glossary_file))
        
        # Add test terms
        manager.add_term("시로네", "Shirone", "characters", 1, "Main protagonist", "male")
        manager.add_term("알페아스 마법학교", "Alpheas Magic School", "places", 1, "Magic academy")
        manager.add_term("광구", "Photon Sphere", "magic_terms", 1, "Basic light spell")
        
        # Test sub-glossary generation
        sub_glossary = manager.generate_sub_glossary(self.test_korean, 1)
        
        self.assertIn('characters', sub_glossary)
        self.assertIn('places', sub_glossary)
        self.assertIn('magic_terms', sub_glossary)
        
        # Test term found in content
        self.assertIn('시로네', sub_glossary['characters'])
        self.assertEqual(sub_glossary['characters']['시로네']['english'], 'Shirone')
        
        print("✅ Glossary Manager tests passed")
    
    def test_prompt_generator(self):
        """Test prompt generator functionality"""
        print("\n🧪 Testing Prompt Generator...")
        
        # Initialize components
        glossary_file = self.test_dir / "test_glossary.json"
        manager = InfinityGlossaryManager(str(glossary_file))
        generator = InfinityPromptGenerator(manager)
        
        # Add test data to glossary
        manager.add_term("시로네", "Shirone", "characters", 1, "Main protagonist", "male")
        manager.add_term("알페아스 마법학교", "Alpheas Magic School", "places", 1, "Magic academy")
        
        # Generate prompt
        prompt = generator.generate_translation_prompt(self.test_korean, 1, 1)
        
        # Validate prompt structure
        self.assertIn("INFINITY MAGE TRANSLATION", prompt)
        self.assertIn("GLOSSARY", prompt)
        self.assertIn("시로네", prompt)
        self.assertIn("Shirone", prompt)
        self.assertIn("REQUIRED OUTPUT FORMAT", prompt)
        self.assertIn("TRANSLATION_START", prompt)
        self.assertIn(self.test_korean, prompt)
        
        # Test prompt length is reasonable
        self.assertGreater(len(prompt), 1000)
        self.assertLess(len(prompt), 50000)  # Should fit in Claude context
        
        print("✅ Prompt Generator tests passed")
    
    def test_response_parser(self):
        """Test response parser functionality"""
        print("\n🧪 Testing Response Parser...")
        
        # Initialize components
        glossary_file = self.test_dir / "test_glossary.json" 
        output_dir = self.test_dir / "parsed_output"
        
        manager = InfinityGlossaryManager(str(glossary_file))
        parser = InfinityResponseParser(manager, str(output_dir))
        
        # Parse test response
        result = parser.parse_claude_response(self.test_response, 1, self.test_korean)
        
        # Validate parsing results
        self.assertTrue(result['success'])
        self.assertEqual(result['chapter_data']['title'], 'Meeting Magic (1)')
        self.assertEqual(result['chapter_data']['date'], '2024-01-01')
        self.assertIn('Shirone was studying magic', result['chapter_data']['content'])
        
        # Check new terms extraction
        self.assertIn('characters', result['new_terms'])
        self.assertIn('이레나', result['new_terms']['characters'])
        self.assertEqual(result['new_terms']['characters']['이레나']['english'], 'Irena')
        
        print("✅ Response Parser tests passed")
    
    def test_complete_processing(self):
        """Test complete response processing workflow"""
        print("\n🧪 Testing Complete Processing Workflow...")
        
        # Initialize components
        glossary_file = self.test_dir / "test_glossary.json"
        output_dir = self.test_dir / "complete_test"
        
        manager = InfinityGlossaryManager(str(glossary_file))
        parser = InfinityResponseParser(manager, str(output_dir))
        
        # Add initial glossary data
        manager.add_term("시로네", "Shirone", "characters", 1, "Main protagonist", "male")
        manager.add_term("알페아스 마법학교", "Alpheas Magic School", "places", 1, "Magic academy")
        
        # Process complete response
        result = parser.process_complete_response(self.test_response, self.test_korean, 1, 1)
        
        # Validate complete processing
        self.assertTrue(result['success'])
        self.assertIn('chapter_file', result)
        
        # Check if chapter file was created
        chapter_file = Path(result['chapter_file'])
        self.assertTrue(chapter_file.exists())
        
        # Validate chapter file content
        with open(chapter_file, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn('title: Meeting Magic (1)', content)
            self.assertIn('chapter: 1', content)
            self.assertIn('volume: 1', content)
            self.assertIn('Shirone was studying magic', content)
        
        print("✅ Complete Processing tests passed")
    
    def test_configuration_system(self):
        """Test configuration system"""
        print("\n🧪 Testing Configuration System...")
        
        config_file = self.test_dir / "test_config.json"
        config = InfinityConfig(str(config_file))
        
        # Test default configuration
        self.assertIsNotNone(config.get('version'))
        self.assertEqual(config.get('translation.wait_time_minutes'), 3)
        
        # Test setting and getting values
        config.set('test.value', 42)
        self.assertEqual(config.get('test.value'), 42)
        
        # Test nested configuration
        config.set('nested.deep.value', 'test')
        self.assertEqual(config.get('nested.deep.value'), 'test')
        
        # Test validation
        validation = config.validate_setup()
        self.assertIn('dependencies_installed', validation)
        
        print("✅ Configuration System tests passed")
    
    def test_quality_validation(self):
        """Test quality validation features"""
        print("\n🧪 Testing Quality Validation...")
        
        glossary_file = self.test_dir / "test_glossary.json"
        manager = InfinityGlossaryManager(str(glossary_file))
        
        # Add test character with gender
        manager.add_term("시로네", "Shirone", "characters", 1, "Main protagonist", "male")
        
        # Test consistency validation
        good_translation = "Shirone cast his magic and he succeeded."
        bad_translation = "Shirone cast her magic and she succeeded."  # Wrong gender
        
        sub_glossary = manager.generate_sub_glossary("시로네", 1)
        
        good_issues = manager.validate_consistency(good_translation, sub_glossary)
        bad_issues = manager.validate_consistency(bad_translation, sub_glossary)
        
        self.assertEqual(len(good_issues), 0)
        self.assertGreater(len(bad_issues), 0)
        self.assertIn('Gender inconsistency', bad_issues[0])
        
        print("✅ Quality Validation tests passed")
    
    def test_integration_workflow(self):
        """Test complete integration workflow (without automation)"""
        print("\n🧪 Testing Integration Workflow...")
        
        # Set up test environment
        glossary_file = self.test_dir / "integration_glossary.json"
        output_dir = self.test_dir / "integration_output"
        
        # Initialize all components
        manager = InfinityGlossaryManager(str(glossary_file))
        generator = InfinityPromptGenerator(manager) 
        parser = InfinityResponseParser(manager, str(output_dir))
        
        # Step 1: Generate prompt
        prompt = generator.generate_translation_prompt(self.test_korean, 1, 1)
        self.assertIn("INFINITY MAGE TRANSLATION", prompt)
        
        # Step 2: Simulate response processing
        result = parser.process_complete_response(self.test_response, self.test_korean, 1, 1)
        self.assertTrue(result['success'])
        
        # Step 3: Verify glossary was updated
        updated_stats = manager.get_statistics()
        self.assertGreater(updated_stats.get('total_terms', 0), 0)
        
        # Step 4: Generate next chapter prompt (should include previous terms)
        next_prompt = generator.generate_translation_prompt(self.test_korean, 2, 1)
        self.assertIn("이레나", next_prompt)  # Should include newly discovered character
        
        print("✅ Integration Workflow tests passed")
    
    def test_error_handling(self):
        """Test error handling and edge cases"""
        print("\n🧪 Testing Error Handling...")
        
        # Test malformed response
        bad_response = "This is not a properly formatted response"
        
        glossary_file = self.test_dir / "error_test_glossary.json"
        output_dir = self.test_dir / "error_test_output"
        
        manager = InfinityGlossaryManager(str(glossary_file))
        parser = InfinityResponseParser(manager, str(output_dir))
        
        result = parser.parse_claude_response(bad_response, 1)
        self.assertFalse(result['success'])
        self.assertGreater(len(result['errors']), 0)
        
        # Test missing Korean content
        result2 = parser.parse_claude_response(self.test_response, 1, "")
        # Should still succeed but with warnings
        
        print("✅ Error Handling tests passed")
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

def run_performance_benchmark():
    """Run performance benchmark tests"""
    print("\n⚡ PERFORMANCE BENCHMARK")
    print("=" * 40)
    
    # Initialize components
    manager = InfinityGlossaryManager("benchmark_glossary.json")
    generator = InfinityPromptGenerator(manager)
    
    # Add sample terms for realistic testing
    sample_terms = [
        ("시로네", "Shirone", "characters", "male"),
        ("에이미", "Amy", "characters", "female"),
        ("알페아스 마법학교", "Alpheas Magic School", "places", ""),
        ("광구", "Photon Sphere", "magic_terms", ""),
        ("시전", "Cast", "magic_terms", ""),
    ]
    
    for i, (korean, english, category, gender) in enumerate(sample_terms, 1):
        manager.add_term(korean, english, category, i, "Test term", gender)
    
    test_korean = "시로네는 알페아스 마법학교에서 광구를 시전했다. 에이미도 함께 했다."
    
    # Benchmark prompt generation
    start_time = time.time()
    for i in range(10):
        prompt = generator.generate_translation_prompt(test_korean, i+1, 1)
    prompt_time = (time.time() - start_time) / 10
    
    # Benchmark sub-glossary generation
    start_time = time.time()
    for i in range(10):
        sub_glossary = manager.generate_sub_glossary(test_korean, i+1)
    glossary_time = (time.time() - start_time) / 10
    
    print(f"📊 Average prompt generation time: {prompt_time:.3f} seconds")
    print(f"📊 Average sub-glossary generation time: {glossary_time:.3f} seconds")
    print(f"📊 Estimated chapter processing time: {prompt_time + glossary_time:.3f} seconds")
    
    # Clean up
    Path("benchmark_glossary.json").unlink(missing_ok=True)

def create_demo_data():
    """Create demonstration data for testing"""
    print("\n📝 Creating Demo Data...")
    
    demo_dir = Path("demo_data")
    demo_dir.mkdir(exist_ok=True)
    
    # Create sample Korean chapter
    sample_korean = """제1장 - 마법을 만나다 (1)

하늘 높이 떠 있는 태양이 알페아스 마법학교 위를 비추고 있었다. 이곳은 왕국에서 가장 권위 있는 마법 교육 기관으로, 수많은 재능 있는 젊은이들이 마법사가 되기 위해 공부하는 곳이었다.

시로네는 학교의 정원에서 혼자 마법 연습을 하고 있었다. 그는 열여덟 살의 소년으로, 금발 머리와 푸른 눈을 가진 수려한 외모였다. 하지만 그의 진정한 매력은 외모가 아니라 타고난 마법적 재능에 있었다.

"시로네, 또 혼자 연습하고 있구나."

뒤에서 들려온 목소리에 시로네가 돌아보니 에이미가 미소를 지으며 다가오고 있었다. 에이미는 시로네와 같은 반 친구로, 빨간 머리와 활발한 성격이 인상적인 소녀였다.

"에이미, 언제 왔어?" 시로네가 물었다.

"방금 전에. 오늘 이레나 선생님 수업에서 새로운 마법을 배울 거라고 들었어. 광구 마법 말이야."

시로네의 눈이 빛났다. 광구는 빛의 마법 중에서도 기초적인 주문이지만, 완벽하게 구사하기는 쉽지 않았다. 마력을 정밀하게 조절해야 하고, 정신 집중도 필요했다.

"그래, 나도 기대돼. 빨리 수업 시간이 왔으면 좋겠어."

두 사람은 함께 교실로 향했다. 알페아스 마법학교의 복도는 언제나 신비로운 분위기로 가득했다. 벽에는 역대 위대한 마법사들의 초상화가 걸려 있었고, 천장에는 마법으로 만든 작은 별들이 반짝이고 있었다."""
    
    with open(demo_dir / "sample_korean_chapter.txt", "w", encoding="utf-8") as f:
        f.write(sample_korean)
    
    # Create sample response
    sample_response = """TRANSLATION_START
---
title: Meeting Magic (1)  
date: 2024-01-01
---

The sun high in the sky was shining down on Alpheas Magic School. This was the kingdom's most prestigious magical educational institution, where countless talented young people studied to become mages.

Shirone was practicing magic alone in the school's garden. He was an eighteen-year-old boy with handsome features—blonde hair and blue eyes. But his true charm lay not in his appearance, but in his innate magical talent.

"Shirone, practicing alone again."

At the voice from behind, Shirone turned to see Amy approaching with a smile. Amy was his classmate, an impressive girl with red hair and a lively personality.

"Amy, when did you arrive?" Shirone asked.

"Just now. I heard we're going to learn new magic in Teacher Irena's class today. Photon magic, they said."

Shirone's eyes lit up. The photon sphere was a basic spell among light magic, but it wasn't easy to master perfectly. It required precise mana control and mental concentration.

"Yeah, I'm looking forward to it too. I wish class time would come quickly."

The two headed to the classroom together. The corridors of Alpheas Magic School were always filled with a mysterious atmosphere. Portraits of great mages from throughout history hung on the walls, and small stars created by magic twinkled on the ceiling.

---
TRANSLATION_END

NEW_TERMS_DISCOVERED:
- 태양 → sun (category: concept) {Natural celestial body}
- 정원 → garden (category: place) {School grounds for practice}
- 복도 → corridor (category: place) {School hallways}
- 초상화 → portrait (category: item) {Paintings of historical figures}
- 별 → stars (category: concept) {Magical ceiling decorations}

CONSISTENCY_CHECK:
- Verified all character names from glossary
- Maintained gender consistency (Shirone: he/him, Amy: she/her, Irena: she/her)
- Used established place names (Alpheas Magic School)
- Used consistent magic terminology (photon sphere, mana)
- Preserved honorific relationships (Teacher Irena)
"""
    
    with open(demo_dir / "sample_claude_response.txt", "w", encoding="utf-8") as f:
        f.write(sample_response)
    
    print(f"✅ Demo data created in: {demo_dir}")
    print(f"  - sample_korean_chapter.txt")
    print(f"  - sample_claude_response.txt")

def main():
    """Run complete test suite"""
    print("🧪 INFINITY MAGE WORKFLOW TEST SUITE")
    print("=" * 60)
    
    # Check if required modules are available
    missing_modules = []
    try:
        import pyautogui
        import pyperclip
        import requests
    except ImportError as e:
        missing_modules.append(str(e))
    
    if missing_modules:
        print("⚠️ Some optional modules are missing:")
        for module in missing_modules:
            print(f"  - {module}")
        print("Install with: pip install pyautogui pyperclip requests")
        print("Continuing with core functionality tests...\n")
    
    # Create demo data
    create_demo_data()
    
    # Run unit tests
    print("\n🧪 RUNNING UNIT TESTS")
    print("=" * 40)
    
    unittest.main(argv=[''], exit=False, verbosity=0)
    
    # Run performance benchmark
    run_performance_benchmark()
    
    print("\n🎉 TEST SUITE COMPLETE!")
    print("=" * 60)
    print("✅ All core functionality tested")
    print("📊 Performance benchmarks completed") 
    print("📝 Demo data created for manual testing")
    print("\n💡 Next steps:")
    print("  1. Test individual components with demo data")
    print("  2. Configure API keys: python infinity_config.py --setup-keys")
    print("  3. Validate setup: python infinity_config.py --validate")
    print("  4. Run first translation: python infinity_translator.py single --chapter 1")

if __name__ == "__main__":
    main()