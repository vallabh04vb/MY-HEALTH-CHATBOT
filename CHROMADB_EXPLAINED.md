# ChromaDB Explained - Complete Guide

## 🤔 What is ChromaDB? (Simple Explanation)

Imagine you have 1000 insurance policy documents. A user asks: **"Is bariatric surgery covered?"**

**Traditional Search (Keywords):**
- Looks for exact words: "bariatric", "surgery", "covered"
- Misses documents that say "weight loss operation" or "obesity procedure"
- ❌ Not smart enough

**Vector Database (ChromaDB):**
- Understands **meaning**, not just words
- Finds documents about weight loss surgery even if they don't say "bariatric"
- ✅ Semantic search (searches by meaning)

---

## 📦 Do You Need to Download ChromaDB?

**No separate download needed!** ChromaDB is just a Python library.

```bash
# It's already in requirements.txt
pip install chromadb

# That's it! No separate server, no installation wizard
```

**How it works:**
- ChromaDB is a **library** (like pandas or numpy)
- When you install it with pip, you're done
- It stores data as **files on your computer**
- No need for a separate database server (like MySQL or MongoDB)

---

## 🧠 How Does ChromaDB Work? (The Magic Behind It)

### Step 1: Text → Numbers (Embeddings)

ChromaDB converts text into **vectors** (arrays of numbers):

```python
Text: "Bariatric surgery is covered for BMI > 35"
         ↓ (AI converts to numbers)
Vector: [0.23, -0.45, 0.67, 0.12, ..., -0.34]  # 384 numbers

Text: "Weight loss procedure requires BMI 35+"
         ↓
Vector: [0.21, -0.47, 0.69, 0.15, ..., -0.32]  # Similar numbers!
```

**Why?** Similar meanings = Similar number patterns

### Step 2: Store Vectors

ChromaDB saves these vectors in files:

```
chroma_data/
├── chroma.sqlite3        # Metadata (titles, URLs)
└── index/*.parquet       # Vectors (the numbers)
```

### Step 3: Search by Meaning

When user asks a question:

```python
User question: "Is weight loss surgery covered?"
              ↓ (convert to vector)
Query vector: [0.22, -0.46, 0.68, 0.13, ..., -0.33]

ChromaDB compares:
- Query vector vs ALL stored vectors
- Finds closest matches (similar numbers = similar meaning)
- Returns: Top 5 most relevant documents
```

---

## 📊 How Data is Stored in ChromaDB

### Storage Structure

```
MY-HEALTH-CHATBOT/
└── chroma_data/               # ← This is your "database"
    ├── chroma.sqlite3         # Metadata (IDs, titles, URLs)
    └── index/
        ├── data.parquet       # Vectors (embeddings)
        └── metadata.parquet   # Additional info
```

### What's Inside?

**Example Document in ChromaDB:**

```python
{
    'id': 'POLICY-001_chunk_0',

    'document': 'Bariatric surgery coverage requires...',  # The text

    'embedding': [0.23, -0.45, 0.67, ...],  # 384 numbers (vector)

    'metadata': {
        'policy_id': 'POLICY-001',
        'title': 'Bariatric Surgery Coverage',
        'source_url': 'https://uhc.com/policy-001',
        'provider': 'UHC',
        'chunk_index': 0
    }
}
```

---

## 🔧 How We Use ChromaDB in Our Project

### Step-by-Step Process

#### **Phase 1: Loading Data (One-Time Setup)**

```python
# File: backend/data_pipeline/load_chromadb.py

# 1. Create ChromaDB client
client = chromadb.Client(
    Settings(
        persist_directory="./chroma_data"  # Save here
    )
)

# 2. Create collection (like a "table" in SQL)
collection = client.create_collection(
    name="insurance_policies"
)

# 3. Add documents
collection.add(
    documents=[
        "Bariatric surgery covered for BMI > 35...",
        "Prior authorization required for MRI...",
        "Genetic testing covered for BRCA..."
    ],
    metadatas=[
        {'policy_id': 'P001', 'title': 'Bariatric Surgery'},
        {'policy_id': 'P002', 'title': 'MRI Authorization'},
        {'policy_id': 'P003', 'title': 'Genetic Testing'}
    ],
    ids=['chunk_0', 'chunk_1', 'chunk_2']
)

# ChromaDB automatically:
# - Converts text to vectors (embeddings)
# - Stores vectors in chroma_data/
# - Creates search index
```

#### **Phase 2: Searching (Every User Query)**

```python
# File: backend/app/main.py

# When user asks: "Is bariatric surgery covered?"

# 1. Query ChromaDB
results = collection.query(
    query_texts=["Is bariatric surgery covered?"],
    n_results=5  # Get top 5 matches
)

# ChromaDB does:
# - Converts question to vector
# - Compares with all stored vectors
# - Returns closest matches

# 2. Results look like:
{
    'documents': [
        ["Bariatric surgery covered for BMI > 35..."],
        ["Weight loss procedures require..."],
        ["Obesity treatment guidelines..."]
    ],
    'metadatas': [
        [{'policy_id': 'P001', 'title': 'Bariatric Surgery', ...}],
        [{'policy_id': 'P045', 'title': 'Weight Loss', ...}],
        [{'policy_id': 'P123', 'title': 'Obesity Treatment', ...}]
    ],
    'distances': [0.23, 0.45, 0.67]  # Lower = more similar
}
```

---

## 🎯 Our Project's ChromaDB Flow

### Visual Flow Diagram

```
USER ASKS QUESTION
       ↓
"Is bariatric surgery covered?"
       ↓
┌──────────────────────────────────┐
│  FastAPI Backend (main.py)       │
│                                  │
│  1. Receive question             │
│  2. Query ChromaDB               │
└──────────────┬───────────────────┘
               ↓
┌──────────────────────────────────┐
│  ChromaDB (chroma_data/)         │
│                                  │
│  • Convert question to vector    │
│  • Search 40 policy chunks       │
│  • Find top 5 matches            │
│  • Return documents + metadata   │
└──────────────┬───────────────────┘
               ↓
┌──────────────────────────────────┐
│  llmops_lite (LLM)               │
│                                  │
│  Context: Top 5 policy chunks    │
│  Question: "Is bariatric..."     │
│  → Generate answer               │
└──────────────┬───────────────────┘
               ↓
     ANSWER TO USER
```

---

## 📂 Where is ChromaDB Data Stored?

### Local Development

```bash
MY-HEALTH-CHATBOT/
└── chroma_data/          # ← HERE!
    ├── chroma.sqlite3    # ~50KB (metadata)
    └── index/            # ~5MB (vectors for 40 chunks)
```

**Physical Location:**
```bash
/Users/vallabhbehere/Workspace/MYSPACE/CombineHealth.ai/MY-HEALTH-CHATBOT/chroma_data/
```

### Production Deployment

**Option 1: Include in Git** (Small datasets)
```bash
# Remove from .gitignore
git add chroma_data/
git commit -m "Add ChromaDB data"
git push

# Render/Vercel: Files deployed with code
```

**Option 2: Upload to Cloud Storage** (Large datasets)
```bash
# Upload chroma_data/ to:
- AWS S3
- Google Cloud Storage
- Render Persistent Disk

# Download in production startup script
```

**Option 3: Build in Production** (Our Approach)
```bash
# On Render server:
python data_pipeline/uhc_scraper.py      # Scrape policies
python data_pipeline/load_chromadb.py    # Build ChromaDB

# Creates chroma_data/ on production server
```

---

## 🔍 How We Use ChromaDB in Code

### **1. Initialization (Startup)**

**File:** `backend/app/main.py`

```python
# On server startup
@app.on_event("startup")
async def startup_event():
    # Connect to ChromaDB
    chroma_client = chromadb.Client(
        Settings(
            persist_directory="./chroma_data",  # Load from disk
            chroma_db_impl="duckdb+parquet"     # File-based
        )
    )

    # Get existing collection
    policy_collection = chroma_client.get_collection(
        name="insurance_policies"
    )

    print(f"ChromaDB loaded: {policy_collection.count()} documents")
```

### **2. Searching (Every Request)**

**File:** `backend/app/main.py`

```python
@app.post("/api/ask")
async def ask_question(request: QueryRequest):
    # User question: "Is bariatric surgery covered?"

    # Search ChromaDB
    results = policy_collection.query(
        query_texts=[request.question],
        n_results=5,                        # Top 5 matches
        where={"provider": "UHC"}           # Filter by provider
    )

    # Extract relevant text
    context_chunks = results['documents'][0]
    # → ["Bariatric surgery covered...", "BMI requirements...", ...]

    # Extract sources
    sources = results['metadatas'][0]
    # → [{'policy_id': 'P001', 'title': '...', 'url': '...'}, ...]

    # Send to LLM with context
    answer = llm.generate(question, context=context_chunks)

    return {
        'answer': answer,
        'sources': sources
    }
```

---

## 🚀 How ChromaDB Gets Deployed

### Deployment Architecture

```
LOCAL (Development)
├── chroma_data/ (on your Mac)
└── Backend connects to local files

PRODUCTION (Render)
├── chroma_data/ (on Render server)
└── Backend connects to Render files
```

### Deployment Options

**Option A: Build on Server** ✅ *Recommended*

```yaml
# render.yaml
services:
  - type: web
    name: uhc-chatbot-api
    buildCommand: |
      pip install -r requirements.txt
      python data_pipeline/uhc_scraper.py
      python data_pipeline/load_chromadb.py
    startCommand: uvicorn app.main:app
```

**Pros:**
- Always fresh data
- No large files in Git

**Cons:**
- Slower first deployment (one-time)

**Option B: Use Persistent Disk**

```yaml
# Render persistent disk
volumes:
  - name: chroma_data
    mountPath: /app/chroma_data
    sizeGB: 1
```

**Pros:**
- Data persists across deploys
- Faster deploys

**Cons:**
- Costs $1/month (1GB)

**Option C: Commit to Git** (Only for small datasets)

```bash
git add chroma_data/
git commit -m "Add ChromaDB data"
```

**Pros:**
- Simple
- No extra steps

**Cons:**
- Large repo size if many policies

---

## 💡 Key Concepts Simplified

### 1. **Collections**
Think of it like a "table" in SQL:

```python
collection = client.create_collection("insurance_policies")
# Like: CREATE TABLE insurance_policies
```

### 2. **Embeddings**
Text converted to numbers:

```python
"Bariatric surgery" → [0.23, -0.45, 0.67, ...]
# 384 numbers that represent the meaning
```

### 3. **Similarity Search**
Finding similar meanings:

```python
Query: "weight loss surgery"
Finds: "bariatric surgery", "obesity procedure", "gastric bypass"
# Even though words are different!
```

### 4. **Metadata**
Extra information stored with each chunk:

```python
metadata = {
    'policy_id': 'P001',
    'title': 'Bariatric Surgery',
    'url': 'https://...',
    'provider': 'UHC'  # ← Filter by this!
}
```

---

## 🎓 Hands-On Exercise

Let's understand by doing:

```bash
# 1. Start Python
cd backend
source venv/bin/activate
python

# 2. Create simple ChromaDB
import chromadb
client = chromadb.Client()

# 3. Create collection
collection = client.create_collection("test")

# 4. Add documents
collection.add(
    documents=[
        "Apple makes iPhones and MacBooks",
        "Microsoft makes Windows and Xbox",
        "Google makes Android and Chrome"
    ],
    ids=["doc1", "doc2", "doc3"]
)

# 5. Search
results = collection.query(
    query_texts=["smartphones and computers"],
    n_results=2
)

print(results['documents'])
# Output: [
#   ["Apple makes iPhones and MacBooks"],
#   ["Google makes Android and Chrome"]
# ]
# ↑ Found Apple & Google (not Microsoft/Xbox) - Smart!
```

---

## 🔧 Common ChromaDB Operations

```python
# Create collection
collection = client.create_collection("my_collection")

# Add documents
collection.add(
    documents=["text1", "text2"],
    metadatas=[{"type": "A"}, {"type": "B"}],
    ids=["id1", "id2"]
)

# Search
results = collection.query(
    query_texts=["search term"],
    n_results=5,
    where={"type": "A"}  # Filter
)

# Count documents
count = collection.count()

# Delete collection
client.delete_collection("my_collection")
```

---

## 🎯 Summary: ChromaDB in Our Project

| Question | Answer |
|----------|--------|
| **Do I download it?** | No, just `pip install chromadb` |
| **Where is data stored?** | `chroma_data/` folder (local files) |
| **How is data stored?** | Vectors (numbers) + metadata in Parquet files |
| **How do we add data?** | `load_chromadb.py` script |
| **How do we search?** | `collection.query()` in `main.py` |
| **How to deploy?** | Include folder OR rebuild on server |
| **Is it a separate server?** | No, embedded in your app |
| **Do I need internet?** | Only for scraping, not for querying |

---

## 🚀 Quick Test to Understand

```bash
# 1. Go to backend
cd backend
source venv/bin/activate

# 2. Create test collection
python

>>> import chromadb
>>> client = chromadb.Client()
>>> collection = client.create_collection("test")

# 3. Add insurance data
>>> collection.add(
...     documents=["Bariatric surgery covered for BMI > 35"],
...     ids=["test1"]
... )

# 4. Search
>>> results = collection.query(
...     query_texts=["Is weight loss surgery covered?"],
...     n_results=1
... )

>>> print(results['documents'])
# Shows: "Bariatric surgery covered..." ← Found it!
```

---

**Key Takeaway:**

ChromaDB is just a **smart search library** that:
- Stores text as numbers (vectors)
- Searches by meaning, not keywords
- Saves data as files (no separate server needed)
- Makes your chatbot super smart! 🧠

**Still confused about anything?** Let me know! 🙋‍♂️
