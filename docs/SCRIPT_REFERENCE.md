# Script Reference Guide

## Translation Scripts

### infinity_translator.py
Core translation engine that processes Korean text to English.
```bash
python scripts/translation/infinity_translator.py --chapter 1
```

### infinity_automation_macro.py
Automated batch translation workflow.
```bash
python scripts/translation/infinity_automation_macro.py --start 1 --end 10
```

### infinity_response_parser.py
Parses and validates AI translation responses.
```bash
python scripts/translation/infinity_response_parser.py --input responses/
```

## Utility Scripts

### copy_chapters_range.py
Copy chapters within a specified range to a folder.
```bash
# Copy chapters 1-50
python scripts/utilities/copy_chapters_range.py 1 50 "output_folder"

# Preview only
python scripts/utilities/copy_chapters_range.py 1 50 "temp" --list-only

# Overwrite existing files
python scripts/utilities/copy_chapters_range.py 1 50 "output" --overwrite
```

### replace_word_global.py
Replace words/phrases across all chapters.
```bash
# Preview replacements
python scripts/utilities/replace_word_global.py "old_word" "new_word"

# Apply replacements
python scripts/utilities/replace_word_global.py "old_word" "new_word" --apply

# Case-sensitive whole-word replacement
python scripts/utilities/replace_word_global.py "Magic" "Sorcery" --apply --case-sensitive --whole-word
```

### fix_chapter_titles_global.py
Standardize chapter titles across all files.
```bash
# Preview fixes
python scripts/utilities/fix_chapter_titles_global.py

# Apply fixes
python scripts/utilities/fix_chapter_titles_global.py --apply
```

## Analysis Scripts

### check_missing_chapters.py
Identify missing or incomplete chapters.
```bash
python scripts/analysis/check_missing_chapters.py --verbose
```

### batch_rescue_chapters.py
Rescue chapters with parsing issues.
```bash
python scripts/analysis/batch_rescue_chapters.py --auto-fix
```

### deduplicate_characters.py
Remove duplicate character entries from glossary.
```bash
python scripts/analysis/deduplicate_characters.py --merge
```

## Management Scripts

### infinity_glossary_manager.py
Manage translation glossaries and character names.
```bash
# Interactive mode
python scripts/infinity_glossary_manager.py

# Export glossary
python scripts/infinity_glossary_manager.py --export glossary.json
```

### infinity_config.py
Configure translation settings and API keys.
```bash
python scripts/infinity_config.py --setup
```

## Common Parameters

### Global Options
- `--verbose`: Enable detailed output
- `--dry-run`: Preview changes without applying
- `--backup`: Create backup before changes
- `--force`: Override safety checks

### File Paths
- `--source`: Source folder path
- `--output`: Output folder path  
- `--config`: Configuration file path

### Range Operations
- `--start N`: Starting chapter number
- `--end N`: Ending chapter number
- `--chapter N`: Specific chapter number

## Examples

### Complete Translation Workflow
```bash
# 1. Check for missing chapters
python scripts/analysis/check_missing_chapters.py

# 2. Run batch translation
python scripts/translation/infinity_automation_macro.py --start 1 --end 100

# 3. Fix title consistency
python scripts/utilities/fix_chapter_titles_global.py --apply

# 4. Validate results
python scripts/analysis/check_missing_chapters.py --validate
```

### Maintenance Tasks
```bash
# Update character names globally
python scripts/utilities/replace_word_global.py "Shirone" "Sirone" --apply --whole-word

# Copy specific arc chapters
python scripts/utilities/copy_chapters_range.py 100 150 "arc_5_chapters"

# Clean up glossary duplicates
python scripts/analysis/deduplicate_characters.py --merge --backup
```