# Infinite Mage Character RAG System

A comprehensive Retrieval Augmented Generation (RAG) system designed specifically for character analysis from the Infinite Mage novel. This system uses advanced natural language processing to understand and analyze character information including appearance, status, relationships, abilities, and development arcs.

## Features

### Character Analysis
- **Comprehensive Character Profiles**: Detailed analysis of appearance, social status, abilities, and relationships
- **Character Development Tracking**: Timeline of character growth and key events
- **Relationship Mapping**: Analysis of character relationships and interactions
- **Ability Assessment**: Detailed breakdown of magical, combat, and intellectual abilities

### Advanced RAG Capabilities
- **Multi-Modal Embeddings**: Specialized vector stores for different query types (dialogue, action, description, relationships)
- **Character-Aware Chunking**: Smart text segmentation that preserves character context
- **Query Routing**: Intelligent routing of queries to the most appropriate vector store
- **Confidence Scoring**: Quality assessment of retrieved information

### User Interface
- **Interactive CLI**: Chat-like interface for natural language queries
- **Command Mode**: Direct command-line queries for specific information
- **Programmatic API**: Python interface for integration with other systems

## 📁 Project Structure

```
RAG/
├── character_loader.py      # Document processing with character extraction
├── character_db.py         # Character profile data structures
├── embeddings.py           # Character-centric embedding strategies  
├── character_rag.py        # Main RAG engine
├── query_interface.py      # User interface for queries
├── main.py                 # Entry point and CLI
├── test_system.py         # System tests
├── README.md              # This file
└── character_profiles_db/  # Generated database and embeddings (created after first run)
```

## 🚀 Quick Start

### Prerequisites

1. **Python Environment**: Ensure you're using Python 3.8+
2. **Install Dependencies**:
   ```bash
   pip install -r ../requirements.txt
   ```

3. **Environment Setup**: Ensure your `.env` file contains:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

### First Run

1. **Test the System**:
   ```bash
   cd RAG
   python test_system.py
   ```
   This will verify all components are working correctly.

2. **Initialize the System**:
   ```bash
   python main.py --test
   ```
   This will build the character database and run sample queries.

### Interactive Mode

```bash
python main.py
```

This starts an interactive chat interface where you can ask questions like:
- "Who is Shirone?"
- "Tell me about Amy's abilities"
- "What is the relationship between Shirone and Rian?"
- "List all characters"
- "Characters who use magic"

### Command Mode

For specific queries, use command-line arguments:

```bash
# Analyze a specific character
python main.py --character "Shirone"

# Analyze relationship between two characters  
python main.py --relationship "Shirone" "Amy"

# Search characters by description
python main.py --search "magic user"

# List all characters
python main.py --list-characters

# Get database statistics
python main.py --stats

# Free-form query
python main.py --query "Who are the main characters?"

# Export character profiles
python main.py --export "character_profiles.json"
```

## 🔍 Query Examples

### Character Analysis
```
Query: "Who is Shirone?"
Result: Comprehensive analysis including appearance, status, relationships, abilities, and character development
```

### Relationship Analysis  
```
Query: "What is the relationship between Shirone and Rian?"
Result: Detailed relationship analysis with interaction examples and development over time
```

### Ability Analysis
```
Query: "Tell me about Amy's magical abilities"
Result: Breakdown of magical powers, proficiency levels, and usage examples
```

### Search Queries
```
Query: "Characters who attend magic school"
Result: List of characters with school affiliations and their roles
```

## 🛠️ Advanced Usage

### Force Rebuild
If you want to rebuild the character database from scratch:
```bash
python main.py --force-rebuild
```

### Different OpenAI Models
Use different models for analysis:
```bash
python main.py --model "gpt-4"  # More capable but slower
python main.py --model "gpt-3.5-turbo"  # Default, faster
```

### Custom Data Directory
If your translated chapters are in a different location:
```bash
python main.py --data-dir "/path/to/your/chapters"
```

## 📊 System Architecture

### Data Processing Pipeline
1. **Document Loading**: Extracts character mentions and context from chapters
2. **Character Recognition**: Identifies and standardizes character names across chapters  
3. **Enhanced Chunking**: Creates character-aware text chunks with metadata
4. **Multi-Modal Embeddings**: Builds specialized vector stores for different query types
5. **Character Database**: Aggregates character information into structured profiles

### Query Processing
1. **Query Analysis**: Determines query intent and type
2. **Query Routing**: Selects appropriate vector store
3. **Retrieval**: Finds most relevant text chunks
4. **Generation**: Uses LLM to synthesize comprehensive answers
5. **Post-Processing**: Formats results and calculates confidence scores

## 🧪 Testing

Run the comprehensive test suite:
```bash
python test_system.py
```

This tests:
- Module imports
- Environment configuration  
- Data access
- Character database functionality

## 📈 Performance

### First Run
- Initial processing: ~5-10 minutes (builds embeddings for 346 chapters)
- Database size: ~100MB (vector embeddings)
- Memory usage: ~1-2GB during processing

### Subsequent Runs
- Startup time: ~10-30 seconds (loads existing embeddings)
- Query response: ~2-5 seconds per query
- Memory usage: ~500MB-1GB

## 🔧 Configuration

The system automatically configures itself based on your data, but you can customize:

### Character Recognition
- Modify `character_names` in `CharacterAwareTextSplitter` for better name recognition
- Adjust `character_patterns` in `CharacterAwareMarkdownLoader` for specific naming conventions

### Embedding Settings
- Change `chunk_size` and `chunk_overlap` in text splitters for different granularity
- Modify importance scoring weights in `_calculate_importance_score`

### Query Routing
- Customize keyword classifications in `CharacterQueryRouter._classify_query`
- Adjust retrieval parameters (`k` values) for more or fewer results

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
   ```bash
   pip install -r ../requirements.txt
   ```

2. **OpenAI API Errors**: Check your API key and account credits
   ```bash
   python -c "import openai; print(openai.api_key)"
   ```

3. **Memory Issues**: Reduce `chunk_size` or process fewer documents at once

4. **Slow Performance**: Use `gpt-3.5-turbo` instead of `gpt-4`, or reduce `k` parameters

### Debug Mode
```bash
python -c "
from main import *
rag = initialize_rag_system('your_api_key')
debug_info = rag.debug_query('your query')
print(debug_info)
"
```

## 📚 API Reference

### CharacterRAGEngine
- `analyze_character(name)`: Comprehensive character analysis
- `analyze_relationship(char1, char2)`: Relationship analysis  
- `analyze_abilities(name)`: Ability breakdown
- `create_character_timeline(name)`: Development timeline
- `search_characters(query)`: Search by description

### CharacterQueryInterface  
- `query_character_info()`: Structured character queries
- `query_relationship()`: Relationship queries
- `search_characters_by_description()`: Semantic search
- `free_form_query()`: Natural language processing

## 🤝 Contributing

This system is designed to be extensible. Key areas for enhancement:
- Additional character relationship types
- More sophisticated ability classification
- Enhanced query understanding
- Integration with visualization tools

## 📄 License

Part of the Infinity Mage Translation System project.