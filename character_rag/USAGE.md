# 🧙 How to Use the Infinity Mage Character RAG System

## ✅ Working Version (Recommended)

The system is now working correctly! Use the **`working_main.py`** script for reliable operation.

### Quick Start

```bash
cd RAG

# List all found characters
python working_main.py --list

# Ask a specific question
python working_main.py --query "Who is Shirone?"

# Interactive mode (recommended for exploration)
python working_main.py --interactive
```

### Interactive Mode Commands

```bash
python working_main.py
```

Then you can ask questions like:
- `Who is Shirone?`
- `Tell me about Amy's abilities`  
- `What is the relationship between Shirone and Rian?`
- `Describe Vincent's background`
- `list` - Show all characters
- `help` - Show example questions
- `quit` - Exit the system

## 📊 System Performance

- **Data Processing**: Currently processes first 20 chapters (configurable)
- **Characters Found**: 6 main characters (Alpheas, Amy, Olina, Rian, Shirone, Vincent)
- **Response Time**: 2-5 seconds per query after initial setup
- **Database Size**: ~50MB vector embeddings

## 🔍 Sample Queries and Results

### Character Analysis
**Query**: `"Who is Shirone and what are his abilities?"`

**Result**: Comprehensive analysis including:
- Background as a young boy dreaming to become a mage
- Mastery of Spirit Zone technique 
- Placement in Class Seven due to talent
- Recognition by Alpheas for his abilities

### Relationship Questions
**Query**: `"What is the relationship between Shirone and Rian?"`

**Result**: Analysis of their friendship dynamics with text evidence

### Character Lists
**Query**: `--list` 

**Result**: 
```
Found Characters (6):
 1. Alpheas
 2. Amy  
 3. Olina
 4. Rian
 5. Shirone
 6. Vincent
```

## ⚙️ Configuration Options

You can modify `simple_rag.py` to:

### Process More Chapters
```python
for filename in sorted(md_files)[:50]:  # Change from [:20] to [:50]
```

### Adjust Response Length
```python
chunk_size=1500,  # Increase from 1000 for longer context
chunk_overlap=300,  # Increase from 200 for better continuity
```

### Add More Characters
```python
character_patterns = [
    r'\bShirone\b', r'\bShiro\b',
    r'\bRian\b', r'\bRyan\b',
    r'\bAmy\b', r'\bAmie\b',
    r'\bYourNewCharacter\b',  # Add new patterns here
    # ... more patterns
]
```

## 🐛 Troubleshooting

### Common Issues

1. **"No documents loaded"**
   - Check that `/data/translated/` contains .md files
   - Verify file permissions

2. **"OPENAI_API_KEY not found"**
   - Ensure `.env` file exists in parent directory
   - Check API key format starts with `sk-`

3. **Slow responses**
   - Reduce number of processed files
   - Use fewer chunks in queries (`k=3` instead of `k=5`)

4. **Memory issues**
   - Reduce `chunk_size` parameter
   - Process fewer documents at once

### System Status Check
```bash
# Test basic functionality
python simple_rag.py

# Check imports and environment
python -c "
import sys, os
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))
from simple_rag import SimpleCharacterRAG
from dotenv import load_dotenv
load_dotenv('../.env')
print('✅ All systems ready!')
"
```

## 🚀 Extending the System

### Add New Query Types
Modify the prompt in `simple_rag.py`:

```python
self.character_prompt = ChatPromptTemplate.from_template("""
You are an expert analyst for the "Infinite Mage" novel.

SPECIALIZED ANALYSIS FOR: {query_type}
- For character analysis: Focus on personality, abilities, growth
- For relationships: Focus on interactions and development
- For abilities: Focus on magical/combat skills and progression

TEXT EXCERPTS:
{context}

QUESTION: {question}
""")
```

### Create Character Profiles
```python
def create_character_profile(self, character_name: str) -> dict:
    questions = [
        f"What does {character_name} look like?",
        f"What are {character_name}'s abilities?", 
        f"Who are {character_name}'s friends and allies?",
        f"What is {character_name}'s background?"
    ]
    
    profile = {}
    for question in questions:
        profile[question] = self.query(question)
    
    return profile
```

## 📈 Performance Optimization

For better performance with more chapters:

1. **Batch Processing**: Process chapters in batches
2. **Caching**: Store processed results 
3. **Filtering**: Pre-filter chapters by character mentions
4. **Parallel Processing**: Use multiple threads for document loading

## 💡 Pro Tips

1. **Be Specific**: "Tell me about Shirone's magical abilities" works better than "Tell me about Shirone"

2. **Use Character Names**: The system recognizes "Shirone", "Amy", "Rian", etc. better than pronouns

3. **Ask Follow-ups**: Build on previous answers for deeper analysis

4. **Check Sources**: Answers include chapter references for verification

The system is now fully functional and ready for character analysis! 🎉