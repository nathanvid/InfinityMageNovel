#!/usr/bin/env python3
"""
Example usage of the Simple Character RAG system
"""

from simple_character_rag import SimpleCharacterRAG


def main():
    """Demonstrate RAG usage."""
    print("Infinity Mage Character RAG - Example Usage")
    print("=" * 50)

    # Initialize RAG
    rag = SimpleCharacterRAG()

    # Load documents (using fewer chapters for quick demo)
    rag.load_documents(max_chapters=10)

    # Show found characters
    characters = rag.list_characters()
    print(f"\nFound {len(characters)} characters: {', '.join(characters)}")

    # Example queries
    example_questions = [
        "Who is Shirone?",
        "What are Vincent and Olina's roles in the story?",
        "Tell me about Alpheas"
    ]

    print(f"\nRunning {len(example_questions)} example queries...")

    for i, question in enumerate(example_questions, 1):
        print(f"\n" + "-" * 50)
        print(f"Question {i}: {question}")
        print("-" * 50)

        try:
            answer = rag.query(question)
            print(f"Answer: {answer[:200]}...")  # Show first 200 chars
            print("Query successful")
        except Exception as e:
            print(f"ERROR: Query failed: {e}")

    print(f"\n" + "=" * 50)
    print("Example complete!")
    print("\nTry interactive mode with: python rag.py")


if __name__ == "__main__":
    main()