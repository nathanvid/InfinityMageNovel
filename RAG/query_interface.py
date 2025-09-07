"""
Query interface for the Infinity Mage Character RAG system.

This module provides user-friendly interfaces for querying character information,
including command-line interface and programmatic query methods.
"""

from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
import argparse
import sys
from tabulate import tabulate

from character_rag import CharacterRAGEngine, CharacterAnalysisResult


@dataclass
class QueryResult:
    """Standardized query result format."""
    query_type: str
    query: str
    result: Union[str, CharacterAnalysisResult, List[str]]
    sources: List[str]
    confidence: float
    processing_time: float


class CharacterQueryInterface:
    """
    User-friendly interface for character queries.
    """
    
    def __init__(self, rag_engine: CharacterRAGEngine):
        """
        Initialize query interface with RAG engine.
        
        Args:
            rag_engine: Initialized CharacterRAGEngine instance
        """
        self.rag_engine = rag_engine
        self.query_history = []
    
    def query_character_info(
        self,
        character_name: str,
        info_type: str = "all",
        detailed: bool = True
    ) -> QueryResult:
        """
        Query information about a specific character.
        
        Args:
            character_name: Name of the character
            info_type: Type of information ('all', 'appearance', 'abilities', 'relationships')
            detailed: Whether to return detailed analysis
            
        Returns:
            QueryResult with character information
        """
        import time
        start_time = time.time()
        
        try:
            if info_type == "all":
                result = self.rag_engine.analyze_character(character_name)
                confidence = result.confidence_score
                sources = result.sources
                
            elif info_type == "abilities":
                result_text = self.rag_engine.analyze_abilities(character_name)
                result = result_text
                confidence = 0.8  # Default confidence for specific queries
                sources = []
                
            elif info_type == "relationships":
                # Get character list to suggest relationship queries
                characters = self.rag_engine.get_character_list()
                result = f"To analyze relationships, use query_relationship() method.\nAvailable characters: {', '.join(characters[:10])}..."
                confidence = 1.0
                sources = []
                
            elif info_type == "timeline":
                result = self.rag_engine.create_character_timeline(character_name)
                confidence = 0.8
                sources = []
                
            else:
                result = f"Unknown info_type: {info_type}. Available types: all, abilities, relationships, timeline"
                confidence = 0.0
                sources = []
                
        except Exception as e:
            result = f"Error querying character information: {str(e)}"
            confidence = 0.0
            sources = []
        
        processing_time = time.time() - start_time
        
        query_result = QueryResult(
            query_type="character_info",
            query=f"{character_name} - {info_type}",
            result=result,
            sources=sources,
            confidence=confidence,
            processing_time=processing_time
        )
        
        self.query_history.append(query_result)
        return query_result
    
    def query_relationship(
        self,
        character1: str,
        character2: str,
        detailed: bool = True
    ) -> QueryResult:
        """
        Query relationship between two characters.
        
        Args:
            character1: First character name
            character2: Second character name
            detailed: Whether to return detailed analysis
            
        Returns:
            QueryResult with relationship information
        """
        import time
        start_time = time.time()
        
        try:
            result = self.rag_engine.analyze_relationship(character1, character2)
            confidence = 0.8  # Default confidence for relationship queries
            sources = []
        except Exception as e:
            result = f"Error analyzing relationship: {str(e)}"
            confidence = 0.0
            sources = []
        
        processing_time = time.time() - start_time
        
        query_result = QueryResult(
            query_type="relationship",
            query=f"{character1} <-> {character2}",
            result=result,
            sources=sources,
            confidence=confidence,
            processing_time=processing_time
        )
        
        self.query_history.append(query_result)
        return query_result
    
    def search_characters_by_description(
        self,
        description: str,
        max_results: int = 5
    ) -> QueryResult:
        """
        Search for characters matching a description.
        
        Args:
            description: Description to search for
            max_results: Maximum number of results to return
            
        Returns:
            QueryResult with matching characters
        """
        import time
        start_time = time.time()
        
        try:
            docs = self.rag_engine.search_characters(description, k=max_results)
            
            # Extract character names from metadata
            character_matches = []
            for doc in docs:
                chars = doc.metadata.get('character_mentions', [])
                chapter = doc.metadata.get('title', 'Unknown')
                for char in chars:
                    if char not in character_matches:
                        character_matches.append(f"{char} (mentioned in {chapter})")
            
            result = character_matches[:max_results] if character_matches else ["No matching characters found"]
            confidence = len(docs) / max_results if docs else 0.0
            sources = [doc.metadata.get('title', 'Unknown') for doc in docs]
            
        except Exception as e:
            result = [f"Error searching characters: {str(e)}"]
            confidence = 0.0
            sources = []
        
        processing_time = time.time() - start_time
        
        query_result = QueryResult(
            query_type="character_search",
            query=description,
            result=result,
            sources=sources,
            confidence=confidence,
            processing_time=processing_time
        )
        
        self.query_history.append(query_result)
        return query_result
    
    def list_all_characters(self) -> QueryResult:
        """
        Get list of all known characters.
        
        Returns:
            QueryResult with character list
        """
        import time
        start_time = time.time()
        
        try:
            characters = self.rag_engine.get_character_list()
            result = sorted(characters)
            confidence = 1.0
            sources = ["Character Database"]
        except Exception as e:
            result = [f"Error getting character list: {str(e)}"]
            confidence = 0.0
            sources = []
        
        processing_time = time.time() - start_time
        
        query_result = QueryResult(
            query_type="character_list",
            query="list all characters",
            result=result,
            sources=sources,
            confidence=confidence,
            processing_time=processing_time
        )
        
        self.query_history.append(query_result)
        return query_result
    
    def get_character_statistics(self) -> QueryResult:
        """
        Get statistics about the character database.
        
        Returns:
            QueryResult with statistics
        """
        import time
        start_time = time.time()
        
        try:
            stats = self.rag_engine.get_character_statistics()
            result = stats
            confidence = 1.0
            sources = ["Character Database"]
        except Exception as e:
            result = {"error": str(e)}
            confidence = 0.0
            sources = []
        
        processing_time = time.time() - start_time
        
        query_result = QueryResult(
            query_type="statistics",
            query="character statistics",
            result=result,
            sources=sources,
            confidence=confidence,
            processing_time=processing_time
        )
        
        self.query_history.append(query_result)
        return query_result
    
    def free_form_query(self, query: str) -> QueryResult:
        """
        Process a free-form natural language query.
        
        Args:
            query: Natural language query
            
        Returns:
            QueryResult with response
        """
        import time
        start_time = time.time()
        
        # Analyze query to determine intent
        query_lower = query.lower()
        
        try:
            # Character-specific queries
            if any(word in query_lower for word in ['who is', 'tell me about', 'describe']):
                # Extract character name
                character_name = self._extract_character_name(query)
                if character_name:
                    result = self.rag_engine.analyze_character(character_name)
                    confidence = result.confidence_score
                    sources = result.sources
                else:
                    result = "Could not identify character name in query."
                    confidence = 0.0
                    sources = []
            
            # Relationship queries
            elif any(word in query_lower for word in ['relationship', 'friends', 'enemies']):
                characters = self._extract_multiple_characters(query)
                if len(characters) >= 2:
                    result = self.rag_engine.analyze_relationship(characters[0], characters[1])
                    confidence = 0.8
                    sources = []
                else:
                    result = "Could not identify two character names for relationship analysis."
                    confidence = 0.0
                    sources = []
            
            # Ability queries
            elif any(word in query_lower for word in ['abilities', 'powers', 'skills', 'magic']):
                character_name = self._extract_character_name(query)
                if character_name:
                    result = self.rag_engine.analyze_abilities(character_name)
                    confidence = 0.8
                    sources = []
                else:
                    result = "Could not identify character name for ability analysis."
                    confidence = 0.0
                    sources = []
            
            # List queries
            elif any(word in query_lower for word in ['list', 'all characters', 'who are']):
                characters = self.rag_engine.get_character_list()
                result = f"Known characters ({len(characters)}): {', '.join(sorted(characters))}"
                confidence = 1.0
                sources = ["Character Database"]
            
            # General search
            else:
                docs = self.rag_engine.search_characters(query, k=5)
                if docs:
                    context = "\n\n".join([doc.page_content[:300] + "..." for doc in docs[:3]])
                    result = f"Found relevant information:\n\n{context}"
                    sources = [doc.metadata.get('title', 'Unknown') for doc in docs]
                    confidence = len(docs) / 5.0
                else:
                    result = "No relevant information found."
                    confidence = 0.0
                    sources = []
                    
        except Exception as e:
            result = f"Error processing query: {str(e)}"
            confidence = 0.0
            sources = []
        
        processing_time = time.time() - start_time
        
        query_result = QueryResult(
            query_type="free_form",
            query=query,
            result=result,
            sources=sources,
            confidence=confidence,
            processing_time=processing_time
        )
        
        self.query_history.append(query_result)
        return query_result
    
    def _extract_character_name(self, query: str) -> Optional[str]:
        """Extract character name from query."""
        characters = self.rag_engine.get_character_list()
        
        # Look for exact matches first
        for char in characters:
            if char.lower() in query.lower():
                return char
        
        # Look for partial matches
        for char in characters:
            if any(part.lower() in query.lower() for part in char.split()):
                return char
        
        return None
    
    def _extract_multiple_characters(self, query: str) -> List[str]:
        """Extract multiple character names from query."""
        characters = self.rag_engine.get_character_list()
        found_characters = []
        
        for char in characters:
            if char.lower() in query.lower():
                found_characters.append(char)
        
        return found_characters
    
    def print_result(self, result: QueryResult, format_type: str = "detailed"):
        """
        Print query result in formatted way.
        
        Args:
            result: QueryResult to print
            format_type: 'simple', 'detailed', or 'json'
        """
        if format_type == "json":
            import json
            print(json.dumps(result.__dict__, indent=2, default=str))
            return
        
        print(f"\n{'='*60}")
        print(f"Query: {result.query}")
        print(f"Type: {result.query_type}")
        print(f"Confidence: {result.confidence:.2f}")
        print(f"Processing Time: {result.processing_time:.3f}s")
        print(f"{'='*60}")
        
        if isinstance(result.result, CharacterAnalysisResult):
            analysis = result.result
            print(f"\n📖 CHARACTER ANALYSIS: {analysis.character_name}")
            print(f"\n📋 Summary:")
            print(analysis.summary)
            print(f"\n👤 Appearance:")
            print(analysis.appearance)
            print(f"\n🏛️ Status:")
            print(analysis.status)
            print(f"\n🤝 Relationships:")
            print(analysis.relationships)
            print(f"\n⚡ Abilities:")
            print(analysis.abilities)
            print(f"\n📈 Development:")
            print(analysis.development)
            
            if format_type == "detailed" and analysis.sources:
                print(f"\n📚 Sources: {', '.join(analysis.sources[:5])}")
                
        elif isinstance(result.result, list):
            if result.query_type == "character_list":
                print(f"\n📋 Characters ({len(result.result)}):")
                # Print in columns
                import textwrap
                wrapped = textwrap.fill(", ".join(result.result), width=70)
                print(wrapped)
            else:
                for i, item in enumerate(result.result, 1):
                    print(f"{i}. {item}")
                    
        elif isinstance(result.result, dict):
            if result.query_type == "statistics":
                print("\n📊 Character Database Statistics:")
                stats = result.result
                data = [
                    ["Total Characters", stats.get('total_characters', 0)],
                    ["Total Relationships", stats.get('total_relationships', 0)],
                    ["Total Abilities", stats.get('total_abilities', 0)],
                    ["Characters with Abilities", stats.get('characters_with_abilities', 0)],
                    ["Characters with Relationships", stats.get('characters_with_relationships', 0)]
                ]
                print(tabulate(data, headers=["Metric", "Count"], tablefmt="grid"))
            else:
                print(f"\n{result.result}")
        else:
            print(f"\n{result.result}")
        
        if format_type == "detailed" and result.sources and result.query_type != "character_list":
            print(f"\n📚 Sources: {', '.join(result.sources[:3])}{'...' if len(result.sources) > 3 else ''}")


class CLIInterface:
    """Command-line interface for the Character RAG system."""
    
    def __init__(self, rag_engine: CharacterRAGEngine):
        """Initialize CLI interface."""
        self.query_interface = CharacterQueryInterface(rag_engine)
    
    def run_interactive_mode(self):
        """Run interactive command-line interface."""
        print("🧙 Welcome to the Infinity Mage Character RAG System!")
        print("Type 'help' for available commands, 'quit' to exit.")
        print("=" * 60)
        
        while True:
            try:
                query = input("\n🔍 Enter your query: ").strip()
                
                if not query:
                    continue
                
                if query.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if query.lower() == 'help':
                    self._print_help()
                    continue
                
                # Process the query
                result = self.query_interface.free_form_query(query)
                self.query_interface.print_result(result)
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def _print_help(self):
        """Print help information."""
        help_text = """
🧙 Infinity Mage Character RAG System - Help

EXAMPLE QUERIES:
• "Who is Shirone?" - Get comprehensive character analysis
• "Tell me about Amy's abilities" - Analyze character's powers
• "What is the relationship between Shirone and Rian?" - Relationship analysis
• "List all characters" - Show all known characters
• "Characters who use magic" - Search by description

SPECIFIC COMMANDS:
• help - Show this help message
• quit/exit/q - Exit the system

QUERY TYPES:
• Character Analysis: Ask about specific characters
• Relationship Queries: Ask about character relationships
• Ability Analysis: Ask about character powers/skills
• Character Search: Search by description or traits
• General Information: Statistics, lists, etc.

The system will automatically determine the best way to answer your question!
        """
        print(help_text)
    
    def run_command_mode(self, args):
        """Run single command mode."""
        if args.list_characters:
            result = self.query_interface.list_all_characters()
            self.query_interface.print_result(result, "simple")
            
        elif args.character:
            result = self.query_interface.query_character_info(args.character)
            self.query_interface.print_result(result)
            
        elif args.relationship:
            if len(args.relationship) != 2:
                print("❌ Error: --relationship requires exactly 2 character names")
                return
            result = self.query_interface.query_relationship(args.relationship[0], args.relationship[1])
            self.query_interface.print_result(result)
            
        elif args.search:
            result = self.query_interface.search_characters_by_description(args.search)
            self.query_interface.print_result(result)
            
        elif args.stats:
            result = self.query_interface.get_character_statistics()
            self.query_interface.print_result(result)
            
        elif args.query:
            result = self.query_interface.free_form_query(args.query)
            self.query_interface.print_result(result)


def create_cli_parser():
    """Create command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="Infinity Mage Character RAG System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python query_interface.py --character "Shirone"
  python query_interface.py --relationship "Shirone" "Amy"  
  python query_interface.py --search "magic user"
  python query_interface.py --query "Who are the main characters?"
  python query_interface.py  # Interactive mode
        """
    )
    
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
    
    return parser


def main():
    """Main CLI entry point."""
    # This would be implemented in main.py, but included here for reference
    pass


if __name__ == "__main__":
    main()