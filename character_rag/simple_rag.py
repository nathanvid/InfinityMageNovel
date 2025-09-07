#!/usr/bin/env python3
"""
Simple working RAG system for character analysis.

This is a streamlined version that should work reliably.
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any
import re
from dotenv import load_dotenv

# Langchain imports
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from langchain.prompts import ChatPromptTemplate

class SimpleCharacterRAG:
    """Simple RAG system for character analysis."""
    
    def __init__(self, openai_api_key: str, data_directory: str):
        """Initialize the RAG system."""
        self.openai_api_key = openai_api_key
        self.data_directory = data_directory
        
        # Initialize components
        self.llm = ChatOpenAI(
            api_key=openai_api_key,
            model="gpt-3.5-turbo",
            temperature=0.1
        )
        
        self.embeddings = OpenAIEmbeddings(api_key=openai_api_key)
        self.vectorstore = None
        self.documents = []
        
        # Character analysis prompt
        self.character_prompt = ChatPromptTemplate.from_template("""
You are an expert analyst for the "Infinite Mage" novel. Based on the provided text excerpts, answer the question about the character.

TEXT EXCERPTS:
{context}

QUESTION: {question}

ANSWER:
Provide a comprehensive answer based on the excerpts. Include:
1. Direct information from the text
2. Chapter references where possible
3. If information isn't available, clearly state so

Answer:
""")
    
    def load_documents(self) -> List[Document]:
        """Load documents from the data directory."""
        documents = []
        
        print(f"📚 Loading documents from {self.data_directory}")
        
        # Get all markdown files
        md_files = [f for f in os.listdir(self.data_directory) if f.endswith('.md')]
        print(f"Found {len(md_files)} markdown files")
        
        for filename in sorted(md_files)[:20]:  # Limit to first 20 for testing
            filepath = os.path.join(self.data_directory, filename)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse frontmatter
                title, content_body = self._parse_markdown(content)
                
                # Find character mentions
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
                print(f"Error loading {filename}: {e}")
        
        self.documents = documents
        print(f"✅ Loaded {len(documents)} documents")
        return documents
    
    def _parse_markdown(self, content: str) -> tuple[str, str]:
        """Parse markdown with frontmatter."""
        frontmatter_match = re.match(r'^---\n(.*?)\n---\n(.*)', content, re.DOTALL)
        
        if frontmatter_match:
            frontmatter = frontmatter_match.group(1)
            content_body = frontmatter_match.group(2)
            
            # Extract title
            title_match = re.search(r'title:\s*(.+)', frontmatter)
            title = title_match.group(1).strip() if title_match else "Unknown"
            
            return title, content_body
        else:
            return "Unknown", content
    
    def _find_characters(self, text: str) -> List[str]:
        """Find character names in text."""
        # Common character patterns from the novel
        character_patterns = [
            r'\bShirone\b', r'\bShiro\b',
            r'\bRian\b', r'\bRyan\b',
            r'\bAmy\b', r'\bAmie\b',
            r'\bVincent\b', r'\bOlina\b',
            r'\bAlpheas\b'
        ]
        
        characters = []
        for pattern in character_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                # Extract the actual match
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    characters.append(matches[0])
        
        return list(set(characters))
    
    def create_vectorstore(self):
        """Create vector store from documents."""
        if not self.documents:
            self.load_documents()
        
        print("🔄 Creating vector store...")
        
        # Split documents
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        
        chunks = text_splitter.split_documents(self.documents)
        print(f"Created {len(chunks)} chunks")
        
        # Create vector store
        self.vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory="./simple_rag_db"
        )
        
        print("✅ Vector store created")
    
    def query(self, question: str, k: int = 5) -> str:
        """Query the RAG system."""
        if not self.vectorstore:
            self.create_vectorstore()
        
        print(f"🔍 Querying: {question}")
        
        # Retrieve relevant documents
        docs = self.vectorstore.similarity_search(question, k=k)
        
        # Create context
        context = "\n\n".join([
            f"[{doc.metadata.get('title', 'Unknown')}]\n{doc.page_content}"
            for doc in docs
        ])
        
        # Generate answer
        prompt = self.character_prompt.format(context=context, question=question)
        response = self.llm.invoke(prompt)
        
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

def main():
    """Main function for testing."""
    print("🧙 Simple Infinite Mage Character RAG System")
    print("=" * 50)
    
    # Load environment
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print("✅ Environment loaded")
    
    # Get API key
    openai_key = os.getenv('OPENAI_API_KEY')
    if not openai_key:
        print("❌ OPENAI_API_KEY not found")
        return
    
    # Set data directory
    data_dir = str(Path(__file__).parent.parent / 'data' / 'translated')
    if not os.path.exists(data_dir):
        print(f"❌ Data directory not found: {data_dir}")
        return
    
    # Initialize RAG system
    rag = SimpleCharacterRAG(openai_key, data_dir)
    
    # Load documents
    docs = rag.load_documents()
    if not docs:
        print("❌ No documents loaded")
        return
    
    # Show found characters
    characters = rag.list_characters()
    print(f"📋 Found characters: {', '.join(characters)}")
    
    # Test queries
    test_queries = [
        "Who is Shirone?",
        "Tell me about Amy",
        "What is the relationship between Shirone and Rian?"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Query: {query}")
        try:
            answer = rag.query(query)
            print(f"📝 Answer: {answer[:300]}...")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()