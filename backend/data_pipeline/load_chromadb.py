"""
Load UHC policies into ChromaDB vector database

This script:
1. Loads scraped policy data
2. Chunks policies into semantic segments
3. Creates embeddings
4. Stores in ChromaDB for semantic search
"""

import json
import sys
from pathlib import Path
from typing import List, Dict
import chromadb
from chromadb.config import Settings
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Add parent directory to path for config imports
sys.path.append(str(Path(__file__).parent.parent))
from app.config import settings

class ChromaDBLoader:
    """Load policy data into ChromaDB"""

    def __init__(
        self,
        persist_directory: str = None,
        collection_name: str = None
    ):
        """
        Initialize ChromaDB loader

        Args:
            persist_directory: Where to store ChromaDB data
            collection_name: Name of the collection
        """
        self.persist_directory = persist_directory or settings.CHROMA_PERSIST_DIRECTORY
        self.collection_name = collection_name or settings.CHROMA_COLLECTION_NAME

        # Text splitter for chunking
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,  # ~250 words per chunk
            chunk_overlap=200,  # Overlap to preserve context
            separators=["\n\n", "\n", ". ", " ", ""],
            length_function=len
        )

        # Initialize ChromaDB
        self.client = None
        self.collection = None
        self._initialize_db()

    def _initialize_db(self):
        """Initialize ChromaDB client and collection"""
        print(f"Initializing ChromaDB at: {self.persist_directory}")

        # Create persistent client
        self.client = chromadb.Client(
            Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=self.persist_directory,
                anonymized_telemetry=False
            )
        )

        # Get or create collection
        try:
            self.collection = self.client.get_collection(name=self.collection_name)
            print(f"  Using existing collection: {self.collection_name}")
            print(f"  Current document count: {self.collection.count()}")
        except:
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}  # Use cosine similarity
            )
            print(f"  Created new collection: {self.collection_name}")

    def load_policies_from_json(self, json_file: Path) -> List[Dict]:
        """Load policies from JSON file"""
        print(f"\nLoading policies from: {json_file}")

        with open(json_file, 'r', encoding='utf-8') as f:
            policies = json.load(f)

        print(f"  Loaded {len(policies)} policies")
        return policies

    def chunk_policy(self, policy: Dict) -> List[Dict]:
        """
        Chunk a single policy into smaller segments

        Args:
            policy: Policy dictionary

        Returns:
            List of chunk dictionaries with text and metadata
        """
        # Extract policy content
        content = policy.get('content', '')

        # Also include section content if available
        sections = policy.get('sections', {})
        if sections:
            section_text = '\n\n'.join([
                f"{key.upper()}\n{value}"
                for key, value in sections.items()
                if value
            ])
            content = f"{content}\n\n{section_text}"

        # Split into chunks
        text_chunks = self.text_splitter.split_text(content)

        # Create chunk documents with metadata
        chunks = []
        for i, chunk_text in enumerate(text_chunks):
            chunks.append({
                'text': chunk_text,
                'metadata': {
                    'policy_id': policy.get('policy_id', 'unknown'),
                    'title': policy.get('title', 'Unknown Policy'),
                    'source_url': policy.get('url', ''),
                    'provider': 'UHC',  # For extensibility
                    'chunk_index': i,
                    'total_chunks': len(text_chunks),
                    'scraped_at': policy.get('scraped_at', '')
                }
            })

        return chunks

    def chunk_all_policies(self, policies: List[Dict]) -> List[Dict]:
        """Chunk all policies"""
        print("\nChunking policies...")

        all_chunks = []

        for policy in policies:
            chunks = self.chunk_policy(policy)
            all_chunks.extend(chunks)

            print(f"  {policy.get('policy_id')}: {len(chunks)} chunks")

        print(f"\n  Total chunks: {len(all_chunks)}")
        return all_chunks

    def load_chunks_to_chromadb(self, chunks: List[Dict], batch_size: int = 100):
        """
        Load chunks into ChromaDB

        Args:
            chunks: List of chunk dictionaries
            batch_size: Number of chunks to add per batch
        """
        print(f"\nLoading {len(chunks)} chunks into ChromaDB...")

        # Process in batches
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]

            # Prepare batch data
            documents = [chunk['text'] for chunk in batch]
            metadatas = [chunk['metadata'] for chunk in batch]
            ids = [
                f"{chunk['metadata']['policy_id']}_chunk_{chunk['metadata']['chunk_index']}"
                for chunk in batch
            ]

            # Add to collection
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )

            print(f"  Loaded batch {i//batch_size + 1}/{(len(chunks)-1)//batch_size + 1}")

        print(f"\n✅ Successfully loaded {len(chunks)} chunks")
        print(f"   Total documents in collection: {self.collection.count()}")

    def persist(self):
        """Persist ChromaDB to disk"""
        print("\nPersisting ChromaDB to disk...")
        self.client.persist()
        print("  ✅ Database persisted")

    def test_query(self, query: str, n_results: int = 3):
        """Test a sample query"""
        print(f"\nTesting query: '{query}'")

        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )

        print(f"\nTop {n_results} results:")
        for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
            print(f"\n{i+1}. Policy: {metadata['title']}")
            print(f"   Excerpt: {doc[:200]}...")

def main():
    """Main loading workflow"""
    print("="*80)
    print("CHROMADB LOADER - UHC INSURANCE POLICIES")
    print("="*80)

    # Initialize loader
    loader = ChromaDBLoader()

    # Load policies from JSON
    data_dir = Path(__file__).parent.parent / "data" / "raw"
    json_file = data_dir / "uhc_policies.json"

    if not json_file.exists():
        print(f"\n❌ ERROR: Policy data file not found: {json_file}")
        print("   Please run uhc_scraper.py first to scrape policies")
        sys.exit(1)

    policies = loader.load_policies_from_json(json_file)

    # Chunk policies
    chunks = loader.chunk_all_policies(policies)

    # Load into ChromaDB
    loader.load_chunks_to_chromadb(chunks)

    # Persist to disk
    loader.persist()

    # Test with sample queries
    print("\n" + "="*80)
    print("TESTING SAMPLE QUERIES")
    print("="*80)

    sample_queries = [
        "What are the criteria for bariatric surgery coverage?",
        "Does UHC cover genetic testing for breast cancer?",
        "Prior authorization requirements for MRI scans"
    ]

    for query in sample_queries:
        loader.test_query(query, n_results=2)

    print("\n" + "="*80)
    print("✅ LOADING COMPLETE")
    print("="*80)
    print(f"ChromaDB Location: {loader.persist_directory}")
    print(f"Collection: {loader.collection_name}")
    print(f"Total Documents: {loader.collection.count()}")

if __name__ == "__main__":
    main()
