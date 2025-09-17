# Simple Infinity Mage Character RAG

A lightweight, easy-to-use RAG system for asking questions about Infinity Mage characters.

## Features
- Ask questions about characters in natural language
- Analyzes character abilities, relationships, and background
- Works with your 346 translated chapters
- Simple setup - just run and ask!

## Quick Start

```bash
cd RAG

# Interactive mode (recommended)
python rag.py

# Ask a single question
python rag.py "Who is Shirone?"

# Alternative - run the main file directly
python simple_character_rag.py
```

## Example Questions

- "Who is Shirone?"
- "What are Amy's magical abilities?"
- "Tell me about Vincent and Olina"
- "What is Alpheas Magic School?"
- "What is the relationship between Shirone and Rian?"

## How It Works

1. **Loads chapters** from `/data/translated/` (first 30 by default)
2. **Finds characters** automatically (Shirone, Amy, Rian, Vincent, etc.)
3. **Creates embeddings** using OpenAI and ChromaDB
4. **Answers questions** using GPT-3.5-turbo with retrieved context

## Files

- `simple_character_rag.py` - Main RAG system class
- `rag.py` - Simple command-line interface
- `character_db/` - Vector database (created automatically)

## Requirements

Your `.env` file must contain:
```
OPENAI_API_KEY=your_key_here
```

Dependencies are already installed from your `requirements.txt`.

## Usage Examples

### Interactive Mode
```bash
python rag.py

Welcome to Infinity Mage Character RAG!
Found characters: Alpheas, Amy, Olina, Rian, Shirone, Vincent

Your question: Who is Shirone?
Answer: Shirone is the main protagonist...
```

### Command Line
```bash
python rag.py "What magical abilities does Shirone have?"
```

## Performance

- **Setup**: ~30 seconds first time
- **Query speed**: 2-5 seconds
- **Memory**: ~200MB
- **Chapters processed**: 30 (configurable)

## Customization

Edit `simple_character_rag.py` to:

**Process more chapters**:
```python
rag.load_documents(max_chapters=50)  # Default is 30
```

**Add more characters**:
```python
character_patterns = [
    r'\bShirone\b',
    r'\bYourCharacter\b',  # Add new character here
    # ...
]
```

**Change chunk size**:
```python
chunk_size=1500,  # Default is 1000
chunk_overlap=300  # Default is 200
```

That's it! Simple and effective character analysis for your Infinity Mage novel.