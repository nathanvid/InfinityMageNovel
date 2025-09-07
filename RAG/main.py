"""
Main entry point for the Infinity Mage Character RAG system.

This module provides the main interface for initializing and running the
character analysis RAG system with support for both programmatic and CLI usage.
"""

import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv

from character_rag import CharacterRAGEngine
from query_interface import CLIInterface, create_cli_parser


def load_environment():
    """Load environment variables from .env file."""
    # Look for .env file in parent directory
    current_dir = Path(__file__).parent
    env_path = current_dir.parent / '.env'
    
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✅ Loaded environment from {env_path}")
    else:
        print(f"⚠️  .env file not found at {env_path}")
    
    # Verify required environment variables
    openai_key = os.getenv('OPENAI_API_KEY')
    if not openai_key:
        print("❌ Error: OPENAI_API_KEY not found in environment variables")
        print("Please make sure your .env file contains OPENAI_API_KEY=your_key_here")
        sys.exit(1)
    
    return openai_key


def initialize_rag_system(
    openai_api_key: str,
    data_directory: str = None,
    force_rebuild: bool = False,
    model_name: str = "gpt-3.5-turbo"
) -> CharacterRAGEngine:
    """
    Initialize the RAG system.
    
    Args:
        openai_api_key: OpenAI API key
        data_directory: Path to translated chapters directory
        force_rebuild: Whether to force rebuild of embeddings
        model_name: OpenAI model to use
        
    Returns:
        Initialized CharacterRAGEngine
    """
    # Set default data directory
    if data_directory is None:
        current_dir = Path(__file__).parent
        data_directory = str(current_dir.parent / 'data' / 'translated')
    
    # Verify data directory exists
    if not os.path.exists(data_directory):
        print(f"❌ Error: Data directory not found: {data_directory}")
        print("Please ensure the translated chapters are in the correct location.")
        sys.exit(1)
    
    # Count available chapters
    chapter_files = [f for f in os.listdir(data_directory) if f.endswith('.md')]
    print(f"📚 Found {len(chapter_files)} chapter files in {data_directory}")
    
    if len(chapter_files) == 0:
        print("❌ Error: No markdown files found in data directory")
        sys.exit(1)
    
    # Initialize RAG engine
    print("🚀 Initializing Character RAG Engine...")
    
    persist_directory = str(Path(__file__).parent / 'character_profiles_db')
    
    rag_engine = CharacterRAGEngine(
        openai_api_key=openai_api_key,
        data_directory=data_directory,
        persist_directory=persist_directory,
        model_name=model_name
    )
    
    # Initialize system (this may take a while on first run)
    print("🔄 Loading/building character database and embeddings...")
    print("   This may take several minutes on first run...")
    
    try:
        rag_engine.initialize_system(force_rebuild=force_rebuild)
        print("✅ RAG system initialized successfully!")
        
        # Print system statistics
        stats = rag_engine.get_character_statistics()
        print(f"📊 System ready with {stats['total_characters']} characters")
        
        return rag_engine
        
    except Exception as e:
        print(f"❌ Error initializing RAG system: {e}")
        print("\nTroubleshooting tips:")
        print("1. Check your OpenAI API key is correct")
        print("2. Ensure you have internet connectivity")
        print("3. Verify the data directory contains markdown files")
        print("4. Try using --force-rebuild flag to rebuild from scratch")
        sys.exit(1)


def run_sample_queries(rag_engine: CharacterRAGEngine):
    """
    Run sample queries to test the system.
    
    Args:
        rag_engine: Initialized RAG engine
    """
    from query_interface import CharacterQueryInterface
    
    print("\n🧪 Running sample queries to test the system...")
    print("=" * 60)
    
    query_interface = CharacterQueryInterface(rag_engine)
    
    # Sample queries
    sample_queries = [
        "Who is Shirone?",
        "List all characters",
        "Tell me about magic users"
    ]
    
    for i, query in enumerate(sample_queries, 1):
        print(f"\n🔍 Sample Query {i}: {query}")
        result = query_interface.free_form_query(query)
        
        # Print simplified result
        if hasattr(result.result, 'summary'):
            print(f"📋 Result: {result.result.summary[:200]}...")
        elif isinstance(result.result, list):
            print(f"📋 Result: Found {len(result.result)} items")
        else:
            print(f"📋 Result: {str(result.result)[:200]}...")
        
        print(f"⚡ Processing time: {result.processing_time:.2f}s")
        print(f"🎯 Confidence: {result.confidence:.2f}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Infinity Mage Character RAG System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
🧙 Infinity Mage Character RAG System

This system allows you to query comprehensive character information from
the Infinity Mage novel using advanced RAG (Retrieval Augmented Generation) 
techniques.

MODES:
1. Interactive Mode (default): Run without arguments for interactive chat
2. Command Mode: Use specific flags for one-off queries  
3. Test Mode: Use --test to run sample queries

EXAMPLES:
  python main.py                           # Interactive mode
  python main.py --character "Shirone"     # Analyze specific character
  python main.py --query "Who are the main characters?"  # Free-form query
  python main.py --test                    # Run test queries
  python main.py --force-rebuild           # Rebuild database from scratch
        """
    )
    
    # System configuration
    parser.add_argument(
        "--data-dir",
        help="Path to translated chapters directory",
        default=None
    )
    
    parser.add_argument(
        "--model",
        help="OpenAI model to use",
        default="gpt-3.5-turbo",
        choices=["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo-preview"]
    )
    
    parser.add_argument(
        "--force-rebuild",
        action="store_true",
        help="Force rebuild of character database and embeddings"
    )
    
    parser.add_argument(
        "--test",
        action="store_true", 
        help="Run sample queries to test the system"
    )
    
    # Query options (from query_interface.py)
    parser.add_argument(
        "--character", "-c",
        help="Analyze specific character"
    )
    
    parser.add_argument(
        "--relationship", "-r",
        nargs=2,
        metavar=("CHAR1", "CHAR2"),
        help="Analyze relationship between two characters"
    )
    
    parser.add_argument(
        "--search", "-s",
        help="Search characters by description"
    )
    
    parser.add_argument(
        "--list-characters", "-l",
        action="store_true",
        help="List all known characters"
    )
    
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show character database statistics"
    )
    
    parser.add_argument(
        "--query", "-q",
        help="Free-form natural language query"
    )
    
    parser.add_argument(
        "--export",
        help="Export character profiles to JSON file"
    )
    
    args = parser.parse_args()
    
    # Load environment
    print("🔧 Loading environment configuration...")
    openai_api_key = load_environment()
    
    # Initialize RAG system
    rag_engine = initialize_rag_system(
        openai_api_key=openai_api_key,
        data_directory=args.data_dir,
        force_rebuild=args.force_rebuild,
        model_name=args.model
    )
    
    # Handle export request
    if args.export:
        print(f"💾 Exporting character profiles to {args.export}...")
        rag_engine.export_character_profiles(args.export)
        return
    
    # Handle test mode
    if args.test:
        run_sample_queries(rag_engine)
        return
    
    # Initialize CLI interface
    cli = CLIInterface(rag_engine)
    
    # Check if any specific query arguments were provided
    has_query_args = any([
        args.character,
        args.relationship, 
        args.search,
        args.list_characters,
        args.stats,
        args.query
    ])
    
    if has_query_args:
        # Run in command mode
        cli.run_command_mode(args)
    else:
        # Run in interactive mode
        cli.run_interactive_mode()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)