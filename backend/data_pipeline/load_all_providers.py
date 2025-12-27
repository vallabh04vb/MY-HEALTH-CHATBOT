"""
Multi-Provider ChromaDB Loader

This script demonstrates the scalability of the system by loading
policies from multiple insurance providers into a single ChromaDB collection.

The system automatically filters by provider when querying, making it
trivial to add new providers without changing any backend code.
"""

import json
import sys
import os
from pathlib import Path
from typing import List, Dict
import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter

class MultiProviderLoader:
    """Load policies from multiple providers into ChromaDB"""

    # List of providers to load
    PROVIDERS = [
        {
            'name': 'UHC',
            'file': 'sample_uhc_policies.json',
            'display_name': 'UnitedHealthcare'
        },
        {
            'name': 'AETNA',
            'file': 'sample_aetna_policies.json',
            'display_name': 'Aetna'
        },
        {
            'name': 'CIGNA',
            'file': 'sample_cigna_policies.json',
            'display_name': 'Cigna'
        }
    ]

    def __init__(self):
        """Initialize multi-provider loader"""
        # Use CHROMA_PERSIST_DIRECTORY from env, or default to relative path
        project_root = Path(__file__).parent.parent
        self.persist_directory = os.getenv(
            "CHROMA_PERSIST_DIRECTORY",
            str(project_root / "chroma_data")
        )
        self.collection_name = os.getenv("CHROMA_COLLECTION_NAME", "insurance_policies")

        # Text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", " ", ""],
            length_function=len
        )

        # Initialize ChromaDB
        self.client = None
        self.collection = None
        self._initialize_db()

    def _initialize_db(self):
        """Initialize ChromaDB client"""
        print(f"Initializing ChromaDB at: {self.persist_directory}")

        # Use new ChromaDB 1.x API
        self.client = chromadb.PersistentClient(path=self.persist_directory)

        # Delete existing collection to start fresh
        try:
            self.client.delete_collection(name=self.collection_name)
            print(f"  Deleted existing collection: {self.collection_name}")
        except:
            pass

        # Create new collection
        self.collection = self.client.create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        print(f"  Created new collection: {self.collection_name}\n")

    def load_all_providers(self):
        """Load policies from all providers"""
        print("="*80)
        print("MULTI-PROVIDER CHROMADB LOADER")
        print("="*80)
        print("This demonstrates the scalability of the system:\n")
        print("✅ Same ChromaDB collection holds ALL providers")
        print("✅ Filtering by provider is automatic")
        print("✅ Adding new providers requires ZERO code changes\n")
        print("="*80 + "\n")

        total_policies = 0
        total_chunks = 0

        for provider_info in self.PROVIDERS:
            policies_loaded, chunks_loaded = self.load_provider(provider_info)
            total_policies += policies_loaded
            total_chunks += chunks_loaded

        # Data is automatically persisted with PersistentClient

        print("\n" + "="*80)
        print("LOADING COMPLETE")
        print("="*80)
        print(f"Total Providers: {len(self.PROVIDERS)}")
        print(f"Total Policies: {total_policies}")
        print(f"Total Chunks: {total_chunks}")
        print(f"ChromaDB Location: {self.persist_directory}")
        print("="*80 + "\n")

        # Demonstrate querying by provider
        self.demonstrate_provider_filtering()

    def load_provider(self, provider_info: Dict) -> tuple:
        """Load policies for a single provider"""
        provider_name = provider_info['name']
        provider_file = provider_info['file']
        display_name = provider_info['display_name']

        print(f"📂 Loading {display_name} ({provider_name})")
        print("-" * 80)

        # Load JSON file
        data_dir = Path(__file__).parent.parent / "data" / "raw"
        json_file = data_dir / provider_file

        if not json_file.exists():
            print(f"  ⚠️  File not found: {provider_file} - Skipping")
            return 0, 0

        with open(json_file, 'r', encoding='utf-8') as f:
            policies = json.load(f)

        print(f"  Found {len(policies)} policies")

        # Chunk policies
        all_chunks = []
        for policy in policies:
            chunks = self.chunk_policy(policy, provider_name)
            all_chunks.extend(chunks)
            print(f"  {policy['policy_id']}: {len(chunks)} chunks")

        # Load into ChromaDB
        if all_chunks:
            self.load_chunks(all_chunks)
            print(f"  ✅ Loaded {len(all_chunks)} chunks for {provider_name}\n")

        return len(policies), len(all_chunks)

    def chunk_policy(self, policy: Dict, provider: str) -> List[Dict]:
        """Chunk a single policy"""
        content = policy.get('content', '')

        # Add section content
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

        # Create chunk documents
        chunks = []
        for i, chunk_text in enumerate(text_chunks):
            chunks.append({
                'text': chunk_text,
                'metadata': {
                    'policy_id': policy.get('policy_id', 'unknown'),
                    'title': policy.get('title', 'Unknown Policy'),
                    'source_url': policy.get('url', ''),
                    'provider': provider,  # ← KEY: Provider tag!
                    'chunk_index': i,
                    'total_chunks': len(text_chunks),
                    'scraped_at': policy.get('scraped_at', '')
                }
            })

        return chunks

    def load_chunks(self, chunks: List[Dict]):
        """Load chunks into ChromaDB"""
        documents = [chunk['text'] for chunk in chunks]
        metadatas = [chunk['metadata'] for chunk in chunks]
        ids = [
            f"{chunk['metadata']['policy_id']}_chunk_{chunk['metadata']['chunk_index']}"
            for chunk in chunks
        ]

        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

    def demonstrate_provider_filtering(self):
        """Demonstrate how provider filtering works"""
        print("\n" + "="*80)
        print("DEMONSTRATION: PROVIDER FILTERING")
        print("="*80)
        print("Showing how the same question returns different results per provider:\n")

        question = "What are the BMI requirements for bariatric surgery?"

        for provider_info in self.PROVIDERS:
            provider = provider_info['name']
            display_name = provider_info['display_name']

            print(f"\n🔍 Query for {display_name} ({provider}):")
            print("-" * 80)

            results = self.collection.query(
                query_texts=[question],
                n_results=2,
                where={"provider": provider}  # ← FILTERING BY PROVIDER!
            )

            if results['documents'] and len(results['documents'][0]) > 0:
                for i, (doc, meta) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
                    print(f"\nResult {i+1}:")
                    print(f"Policy: {meta['title']}")
                    print(f"Excerpt: {doc[:150]}...")
            else:
                print(f"No results found for {provider}")

        print("\n" + "="*80)
        print("✅ Same ChromaDB, different results based on provider filter!")
        print("✅ Adding new providers = Just add JSON file + update PROVIDERS list")
        print("="*80)


def main():
    """Main execution"""
    loader = MultiProviderLoader()
    loader.load_all_providers()

    print("\n" + "🎯 " + "="*76)
    print("SCALABILITY DEMONSTRATED:")
    print("-" * 80)
    print("1. ✅ Multiple providers in ONE ChromaDB collection")
    print("2. ✅ Automatic filtering by provider metadata")
    print("3. ✅ ZERO backend code changes to add new providers")
    print("4. ✅ Frontend just needs to pass provider parameter")
    print("5. ✅ Same query, different results per provider")
    print("\nTo add new provider:")
    print("  1. Create sample_[provider]_policies.json")
    print("  2. Add to PROVIDERS list in this file")
    print("  3. Run: python load_all_providers.py")
    print("  4. Done! No API changes needed!")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
