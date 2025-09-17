#!/usr/bin/env python3
"""
Simple Character RAG System for Infinity Mage Novel

A lightweight, easy-to-use RAG system for character analysis.
Just run and ask questions!
"""

import os
import re
from typing import List, Dict
from pathlib import Path
from dotenv import load_dotenv

# LangChain imports
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from langchain.prompts import ChatPromptTemplate

class SimpleCharacterRAG:
    """Simple RAG system for character analysis from Infinity Mage."""

    def __init__(self):
        """Initialize the RAG system."""
        print("Initializing Infinity Mage Character RAG...")

        # Load environment
        load_dotenv('../.env')
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("ERROR: OPENAI_API_KEY not found. Please set it in your .env file.")

        # Initialize components
        self.llm = ChatOpenAI(api_key=api_key, model="gpt-3.5-turbo", temperature=0.1)
        self.embeddings = OpenAIEmbeddings(api_key=api_key)
        self.vectorstore = None
        self.documents = []

        # Data paths
        self.data_dir = Path("../data/translated")
        if not self.data_dir.exists():
            raise FileNotFoundError(f"ERROR: Data directory not found: {self.data_dir}")

        # Character analysis prompt
        self.prompt = ChatPromptTemplate.from_template("""
You are an expert on the "Infinity Mage" novel. Answer questions about characters based on the provided text.

TEXT EXCERPTS:
{context}

QUESTION: {question}

INSTRUCTIONS:
- Focus on character information (appearance, abilities, relationships, background)
- Quote specific details from the text when possible
- Mention chapter references if available
- If information isn't in the excerpts, say so clearly

ANSWER:
""")

        print("RAG system initialized!")

    def load_documents(self, max_chapters: int = 300) -> List[Document]:
        """Load and process documents."""
        print(f"Loading up to {max_chapters} chapters...")

        # Get markdown files
        md_files = sorted([f for f in os.listdir(self.data_dir) if f.endswith('.md')])

        if not md_files:
            raise FileNotFoundError("ERROR: No markdown files found in data directory")

        print(f"📄 Found {len(md_files)} total chapters")

        # Load documents
        documents = []
        for filename in md_files[:max_chapters]:
            filepath = self.data_dir / filename

            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Parse frontmatter
                title, content_body = self._parse_markdown(content)

                # Find characters
                characters = self._find_characters(content_body)

                doc = Document(
                    page_content=content_body,
                    metadata={
                        'source': filename,
                        'title': title,
                        'characters': ', '.join(characters) if characters else 'none'
                    }
                )
                documents.append(doc)

            except Exception as e:
                print(f"WARNING: Error loading {filename}: {e}")

        self.documents = documents
        print(f"Loaded {len(documents)} chapters")
        return documents

    def _parse_markdown(self, content: str) -> tuple:
        """Extract title from markdown frontmatter."""
        frontmatter_match = re.match(r'^---\n(.*?)\n---\n(.*)', content, re.DOTALL)

        if frontmatter_match:
            frontmatter = frontmatter_match.group(1)
            content_body = frontmatter_match.group(2)

            # Extract title
            title_match = re.search(r'title:\s*(.+)', frontmatter)
            title = title_match.group(1).strip() if title_match else "Unknown Chapter"

            return title, content_body
        else:
            return "Unknown Chapter", content

    def _find_characters(self, text: str) -> List[str]:
        """Find character names in text."""
        # Main characters from Infinity Mage
        character_patterns = [
            r'\bShirone\b', r'\bShiro\b',
            r'\bRian\b', r'\bRyan\b',
            r'\bAmy\b', r'\bAmie\b',
            r'\bVincent\b', r'\bOlina\b',
            r'\bAlpheas\b', r'\bEthella\b',
            r'\bCloset\b', r'\bSena\b',
            r'\bMarsha\b', r'\bNade\b'
        ]

        found_characters = []
        for pattern in character_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    found_characters.append(matches[0])

        return list(set(found_characters))

    def create_vectorstore(self):
        """Create vector embeddings from documents."""
        if not self.documents:
            self.load_documents()

        print("🔄 Creating vector embeddings...")

        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )

        chunks = text_splitter.split_documents(self.documents)
        print(f"Created {len(chunks)} text chunks")

        # Create vector store
        self.vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory="./character_db"
        )

        print("Vector store created!")

    def query(self, question: str, k: int = 5) -> str:
        """Ask a question about the characters."""
        if not self.vectorstore:
            self.create_vectorstore()

        print(f"Searching for: {question}")

        # Retrieve relevant documents
        docs = self.vectorstore.similarity_search(question, k=k)

        # Create context
        context = "\n\n".join([
            f"[{doc.metadata.get('title', 'Unknown')}]\n{doc.page_content}"
            for doc in docs
        ])

        # Generate answer
        response = self.llm.invoke(
            self.prompt.format_messages(context=context, question=question)
        )

        return response.content

    def list_characters(self) -> List[str]:
        """List all found characters."""
        if not self.documents:
            self.load_documents()

        all_characters = set()
        for doc in self.documents:
            char_string = doc.metadata.get('characters', 'none')
            if char_string != 'none':
                characters = char_string.split(', ')
                all_characters.update(characters)

        return sorted(list(all_characters))

    def interactive_mode(self):
        """Run in interactive mode."""
        print("\n" + "="*60)
        print("Welcome to Infinity Mage Character RAG!")
        print("Ask questions about characters. Type 'quit' to exit.")
        print("="*60)

        # Show available characters
        characters = self.list_characters()
        if characters:
            print(f"Found characters: {', '.join(characters)}")

        print("\nExample questions:")
        print("• Who is Shirone?")
        print("• What are Amy's abilities?")
        print("• Tell me about Vincent and Olina")
        print("• What is Alpheas Magic School?")

        while True:
            try:
                question = input("\nYour question: ").strip()

                if not question:
                    continue

                if question.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break

                if question.lower() in ['help', 'h']:
                    print("\nExample questions:")
                    print("• Who is Shirone?")
                    print("• What are Amy's abilities?")
                    print("• Tell me about Vincent and Olina")
                    print("• What is Alpheas Magic School?")
                    continue

                if question.lower() in ['list', 'characters']:
                    print(f"Characters: {', '.join(characters)}")
                    continue

                print("🔄 Processing...")
                answer = self.query(question)
                print(f"\nAnswer:\n{answer}")

            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"ERROR: {e}")


def main():
    """Main function."""
    try:
        # Initialize RAG system
        rag = SimpleCharacterRAG()

        # Load documents
        rag.load_documents()

        # Run interactive mode
        rag.interactive_mode()

    except Exception as e:
        print(f"ERROR: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure your .env file contains OPENAI_API_KEY")
        print("2. Check that /data/translated/ contains .md files")
        print("3. Ensure you have internet connection")


if __name__ == "__main__":
    main()