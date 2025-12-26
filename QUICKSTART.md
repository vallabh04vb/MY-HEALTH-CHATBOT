# Quick Start - Get Running in 5 Minutes

## TL;DR - Copy & Paste These Commands

### Step 1: Backend Setup (Terminal 1)
```bash
cd /Users/vallabhbehere/Workspace/MYSPACE/CombineHealth.ai/MY-HEALTH-CHATBOT/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# ⚠️ IMPORTANT: Edit .env and add your llmops_lite credentials:
# LITELLM_PROXY_BASE_URL=your-url
# LITELLM_PROXY_SECRET_KEY=your-key

# Create sample data for testing (skip scraping for now)
mkdir -p data/raw

# Start server
uvicorn app.main:app --reload
```

### Step 2: Frontend Setup (Terminal 2)
```bash
cd /Users/vallabhbehere/Workspace/MYSPACE/CombineHealth.ai/MY-HEALTH-CHATBOT/frontend

# Install dependencies
npm install

# Configure environment
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Start development server
npm run dev
```

### Step 3: Open Browser
```
Frontend: http://localhost:3000
Backend API Docs: http://localhost:8000/docs
```

---

## First-Time Setup Checklist

Before starting, make sure you have:

1. **llmops_lite configured**
   ```bash
   # Check if llmops_lite exists
   ls /Users/vallabhbehere/Workspace/MYSPACE/CombineHealth.ai/llmops_lite

   # Check if .env file has credentials
   cat /Users/vallabhbehere/Workspace/MYSPACE/CombineHealth.ai/llmops_lite/.env | grep LITELLM_PROXY
   ```

2. **Python 3.11+ installed**
   ```bash
   python3 --version
   # Should show: Python 3.11.x or higher
   ```

3. **Node.js 18+ installed**
   ```bash
   node --version
   # Should show: v18.x.x or higher
   ```

---

## What to Expect

### When Backend Starts:
```
✅ llmops_lite imported successfully
✅ ChromaDB initialized: 0 documents (empty - that's OK for now)
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### When Frontend Starts:
```
- ready started server on 0.0.0.0:3000, url: http://localhost:3000
- event compiled client and server successfully in 2.5 s
```

---

## Quick Tests

### Test 1: Backend Health
```bash
curl http://localhost:8000/api/health
```

### Test 2: Frontend in Browser
```
Visit: http://localhost:3000
Should see: Chat interface with "UHC Insurance Policy Assistant" header
```

---

## Troubleshooting

### "llmops_lite not found"
```bash
# Make sure llmops_lite is in parent directory
ls ../llmops_lite
# If not, copy it from wherever it is
```

### "CORS error" in browser
```bash
# Edit backend/.env
# Make sure: CORS_ORIGINS=http://localhost:3000
```

### "ChromaDB collection not found"
```
This is OK for initial testing! The chatbot will start without data.
To add real data, follow LOCAL_TESTING_GUIDE.md Step 4
```

---

## Next Steps

Once you see both servers running:
1. Follow **LOCAL_TESTING_GUIDE.md** for comprehensive testing
2. Load actual UHC policy data
3. Test end-to-end with real queries

---

## Stop Servers

```bash
# In each terminal, press: Ctrl + C
```

## Restart Servers

```bash
# Backend (Terminal 1)
cd backend
source venv/bin/activate
uvicorn app.main:app --reload

# Frontend (Terminal 2)
cd frontend
npm run dev
```
