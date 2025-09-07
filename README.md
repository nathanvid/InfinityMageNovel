# Infinity Mage Translation Project

A comprehensive translation workflow system for the Korean webnovel "Infinity Mage" (무한마법사).

## Project Structure

```
InfinityMageNovel/
├── scripts/
│   ├── translation/           # Core translation workflow
│   │   ├── infinity_translator.py
│   │   ├── infinity_response_parser.py
│   │   ├── infinity_prompt_generator.py
│   │   └── infinity_automation_macro.py
│   ├── utilities/             # File management utilities
│   │   ├── copy_chapters_range.py
│   │   ├── replace_word_global.py
│   │   ├── fix_chapter_titles_global.py
│   │   └── fix_chapter_titles.py
│   ├── analysis/              # Analysis and rescue tools
│   │   ├── check_missing_chapters.py
│   │   ├── batch_rescue_chapters.py
│   │   ├── manual_chapter_parser.py
│   │   └── deduplicate_characters.py
│   ├── infinity_config.py     # Configuration management
│   ├── infinity_glossary_manager.py  # Glossary management
│   └── cursor_position_finder.py
├── data/
│   ├── source/               # Original Korean content
│   │   ├── volumes/          # Volume files (1-51)
│   │   └── chapters_raw/     # Raw chapter files
│   ├── translated/           # Translated chapters
│   ├── glossaries/           # Translation dictionaries
│   ├── backups/              # Backup files
│   ├── responses/            # AI translation responses
│   └── prompts/              # Translation prompts
├── docs/                     # Documentation
├── tests/                    # Test files
├── demo/                     # Demo and examples
├── logs/                     # Processing logs
├── RAG/                      # ChatBot project on the universe of Infinite mage
└── requirements.txt
```

## Quick Start

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Configure settings
python scripts/infinity_config.py
```

### Translation Workflow
```bash
# Run automated translation
python scripts/translation/infinity_automation_macro.py

# Check for missing chapters
python scripts/analysis/check_missing_chapters.py

# Fix chapter titles globally
python scripts/utilities/fix_chapter_titles_global.py --apply
```

### Utilities
```bash
# Copy chapter range
python scripts/utilities/copy_chapters_range.py 1 50 "output_folder"

# Replace words globally
python scripts/utilities/replace_word_global.py "old_word" "new_word" --apply

# Manage glossary
python scripts/infinity_glossary_manager.py
```

## Features

- **Automated Translation**: AI-powered Korean to English translation
- **Glossary Management**: Consistent character names and terminology
- **Chapter Analysis**: Missing chapter detection and rescue
- **Title Standardization**: Consistent chapter title formatting
- **Batch Processing**: Handle multiple chapters efficiently
- **Backup System**: Automatic backups before major changes

## Translation Progress

- **Total Chapters**: 1,277
- **Translated**: Check `data/glossaries/translation_progress.json`
- **Quality Control**: Automated consistency checks

## Documentation

See `docs/` folder for detailed documentation:
- Translation workflow guide
- Script usage examples  
- Configuration options
- Troubleshooting guide

## License

This project is for educational and personal translation purposes.