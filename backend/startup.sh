#!/bin/bash

echo "========================================="
echo "Starting UHC Chatbot Backend"
echo "========================================="

# Check if ChromaDB needs initialization
INIT_NEEDED=0

python -c "
import chromadb
import os

persist_dir = os.getenv('CHROMA_PERSIST_DIRECTORY', 'chroma_data')
collection_name = os.getenv('CHROMA_COLLECTION_NAME', 'insurance_policies')

try:
    client = chromadb.PersistentClient(path=persist_dir)
    collection = client.get_collection(name=collection_name)
    count = collection.count()
    print(f'✅ ChromaDB has {count} documents')

    if count == 0:
        print('⚠️  ChromaDB is empty - initializing...')
        exit(1)  # Trigger data loading
    exit(0)  # ChromaDB is ready
except Exception as e:
    print(f'❌ ChromaDB not initialized: {e}')
    exit(1)  # Trigger data loading
" || INIT_NEEDED=1

# If ChromaDB needs initialization, load data
if [ $INIT_NEEDED -eq 1 ]; then
    echo "========================================="
    echo "Initializing ChromaDB with policy data..."
    echo "========================================="
    python data_pipeline/load_all_providers.py || {
        echo "❌ Failed to initialize ChromaDB"
        exit 1
    }
    echo "✅ ChromaDB initialization complete!"
fi

# Start the FastAPI server
echo "========================================="
echo "Starting FastAPI server..."
echo "========================================="
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT
