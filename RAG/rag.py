#!/usr/bin/env python3
"""
Infinity Mage Character RAG - Simple Interface

Usage:
  python rag.py                    # Interactive mode
  python rag.py "Who is Shirone?"  # Single question
"""

import sys
from simple_character_rag import SimpleCharacterRAG


def main():
    """Main entry point."""
    try:
        # Initialize RAG
        rag = SimpleCharacterRAG()
        rag.load_documents()

        # Check if question provided as argument
        if len(sys.argv) > 1:
            question = ' '.join(sys.argv[1:])
            print(f"Question: {question}")
            answer = rag.query(question)
            print(f"\nAnswer:\n{answer}")
        else:
            # Interactive mode
            rag.interactive_mode()

    except Exception as e:
        print(f"ERROR: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())