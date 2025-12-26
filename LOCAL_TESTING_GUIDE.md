# Local Testing Guide - Complete End-to-End

This guide walks you through testing the entire chatbot locally before deployment.

---

## Prerequisites Checklist

Before starting, ensure you have:

- [ ] Python 3.11+ installed (`python --version`)
- [ ] Node.js 18+ installed (`node --version`)
- [ ] Git installed
- [ ] llmops_lite configured in parent directory
- [ ] LiteLLM proxy credentials (from llmops_lite)

---

## Phase 1: Backend Setup & Testing

### Step 1: Set Up Python Virtual Environment

```bash
cd MY-HEALTH-CHATBOT/backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate

# Verify activation (should show venv path)
which python
```

### Step 2: Install Backend Dependencies

```bash
# Install all requirements
pip install -r requirements.txt

# Verify key packages installed
pip list | grep fastapi
pip list | grep chromadb
pip list | grep uvicorn
```

### Step 3: Configure Environment Variables

```bash
# Create .env file from example
cp .env.example .env

# Edit .env file with your credentials
nano .env  # or use any text editor
```

**Required in `.env`:**
```bash
# Copy from llmops_lite/.env
LITELLM_PROXY_BASE_URL=https://your-litellm-proxy.com
LITELLM_PROXY_SECRET_KEY=your-secret-key-here

# Optional (for caching)
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret

# Local settings
APP_ENV=development
DEBUG=True
LOG_LEVEL=INFO
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:3000
```

### Step 4: Test Data Pipeline (CRITICAL!)

#### 4.1: Scrape Sample UHC Policies

```bash
# Make sure you're in backend directory with venv activated
cd data_pipeline

# Run scraper (limited to 5 policies for testing)
python uhc_scraper.py
```

**Expected Output:**
```
================================================================================
UHC POLICY SCRAPER
================================================================================
Fetching policy links from: https://www.uhcprovider.com/...
Found X policy links

[1/5] Scraping: Policy Name 1
  Saved to: data/raw/POLICY-001.json
[2/5] Scraping: Policy Name 2
...
✅ SCRAPING COMPLETE - 5 policies scraped
```

**⚠️ If scraper fails:**
- Check internet connection
- UHC website might have changed structure
- Use fallback: Create sample policy files manually (see below)

#### 4.2: Load Policies into ChromaDB

```bash
# Still in data_pipeline directory
python load_chromadb.py
```

**Expected Output:**
```
================================================================================
CHROMADB LOADER - UHC INSURANCE POLICIES
================================================================================
Initializing ChromaDB at: ../chroma_data
  Created new collection: insurance_policies

Loading policies from: ../data/raw/uhc_policies.json
  Loaded 5 policies

Chunking policies...
  POLICY-001: 8 chunks
  POLICY-002: 6 chunks
  ...
  Total chunks: 40

Loading 40 chunks into ChromaDB...
  Loaded batch 1/1
✅ Successfully loaded 40 chunks
```

**Verify ChromaDB:**
```bash
# Check that chroma_data directory exists
ls -la ../../chroma_data

# Should see files like:
# - chroma.sqlite3
# - *.parquet files
```

### Step 5: Start Backend Server

```bash
# Go back to backend root
cd ..

# Start FastAPI server
uvicorn app.main:app --reload

# You should see:
# INFO:     Uvicorn running on http://0.0.0.0:8000
# INFO:     Application startup complete.
```

### Step 6: Test Backend API

**Test 1: Health Check**
```bash
# In a NEW terminal (keep server running)
curl http://localhost:8000/api/health

# Expected response:
{
  "status": "healthy",
  "version": "1.0.0",
  "llm_proxy": "https://your-proxy.com",
  "chroma_collections": 1,
  "timestamp": "2024-01-15T10:30:00"
}
```

**Test 2: Ask Question (Simple)**
```bash
curl -X POST http://localhost:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is bariatric surgery?", "provider": "UHC"}'

# Expected: JSON response with answer, sources, confidence
```

**Test 3: Interactive API Docs**
```
Open browser: http://localhost:8000/docs

1. Click on "POST /api/ask"
2. Click "Try it out"
3. Enter question: "What are the coverage criteria for MRI scans?"
4. Click "Execute"
5. Check response below
```

**✅ Backend Tests Passed If:**
- [ ] Health endpoint returns "healthy"
- [ ] API docs load at /docs
- [ ] Ask endpoint returns answer with sources
- [ ] ChromaDB collection count > 0
- [ ] No errors in terminal logs

---

## Phase 2: Frontend Setup & Testing

### Step 7: Set Up Frontend

```bash
# Open NEW terminal
cd MY-HEALTH-CHATBOT/frontend

# Install dependencies (takes 2-3 minutes)
npm install

# Expected output:
# added 300+ packages
```

### Step 8: Configure Frontend Environment

```bash
# Create .env.local
cp .env.local.example .env.local

# Edit .env.local
nano .env.local
```

**Set:**
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Step 9: Start Frontend Development Server

```bash
# Start Next.js dev server
npm run dev

# Expected output:
# - Local:        http://localhost:3000
# - Ready in 2.5s
```

### Step 10: Test Frontend in Browser

**Open browser:** http://localhost:3000

**Visual Checks:**
- [ ] Page loads without errors
- [ ] Header shows "UHC Insurance Policy Assistant"
- [ ] Three info cards visible
- [ ] Chat interface visible
- [ ] Input box at bottom
- [ ] Example questions shown

**Console Check:**
```
1. Open browser console (F12 or right-click → Inspect)
2. Check Console tab
3. Should be NO red errors
```

---

## Phase 3: End-to-End Integration Testing

### Test 11: Full Chat Flow

**Test Case 1: Normal Question**
```
1. In chat input, type: "Is bariatric surgery covered?"
2. Click send button
3. Wait 3-5 seconds

Expected:
✅ Loading animation appears
✅ Response appears with answer
✅ Sources section shows policy citations
✅ Confidence score displayed
✅ Source links are clickable
```

**Test Case 2: Repeated Question (Cache Test)**
```
1. Ask same question again: "Is bariatric surgery covered?"
2. Click send

Expected:
✅ Response comes back MUCH faster (<1 second)
✅ Same answer as before
✅ This proves llmops_lite caching works!
```

**Test Case 3: Invalid Input (Edge Case)**
```
1. Type: "What is the meaning of life?"
2. Send

Expected:
✅ Response: "I can only answer questions about UHC insurance..."
✅ No sources shown
✅ Confidence: 0.0
```

**Test Case 4: Empty Input (Edge Case)**
```
1. Leave input blank
2. Click send

Expected:
✅ Send button disabled OR
✅ Error message shown
```

**Test Case 5: Long Question**
```
1. Type a very long question (500+ characters)
2. Send

Expected:
✅ Error message: "Question too long"
```

### Test 12: Source Citations

```
1. Ask: "What are prior authorization requirements?"
2. Wait for response
3. Check Sources section

Expected:
✅ Multiple sources listed (1-5)
✅ Each source has:
   - Policy ID
   - Policy Title
   - "View" button
✅ Click "View" button → Opens UHC policy page in new tab
```

### Test 13: Confidence Scoring

```
1. Ask a very specific question: "What is the exact BMI requirement for bariatric surgery approval?"
2. Check confidence badge

Expected:
✅ High confidence (>70%): Green badge
✅ Medium confidence (50-70%): Yellow badge
✅ Low confidence (<50%): Red badge + warning message
```

### Test 14: Multiple Questions (Session Test)

```
Ask 3 different questions in sequence:
1. "What is covered for knee replacement?"
2. "Does UHC cover genetic testing?"
3. "What are the limitations for MRI scans?"

Expected:
✅ All questions answered
✅ Chat history preserved
✅ Each response has its own sources
✅ Timestamps shown
✅ Can scroll through chat history
```

### Test 15: Clear Chat

```
1. After asking several questions
2. Click "Clear Chat" button in header

Expected:
✅ All messages disappear
✅ Empty state shows: "Start a conversation"
✅ Input box still works
```

---

## Phase 4: Error Scenarios (Edge Cases)

### Test 16: Backend Down

```
1. Stop backend server (Ctrl+C in backend terminal)
2. Try asking a question in frontend

Expected:
✅ Error message appears
✅ User-friendly error (not technical gibberish)
✅ Red error box shown
```

### Test 17: Invalid Backend URL

```
1. Edit frontend/.env.local
2. Change API_URL to: http://localhost:9999 (wrong port)
3. Restart frontend: npm run dev
4. Try asking question

Expected:
✅ Connection error shown
✅ Frontend doesn't crash
```

### Test 18: ChromaDB Empty

```
1. Delete chroma_data folder: rm -rf ../chroma_data
2. Restart backend
3. Ask question

Expected:
✅ Error or warning: "ChromaDB collection is empty"
✅ Helpful message to run data pipeline
```

---

## Phase 5: Performance Testing

### Test 19: Response Time

```
Time these operations:

1. First question (cold start):
   Expected: 3-5 seconds

2. Same question (cached):
   Expected: <500ms (instant)

3. Different question:
   Expected: 3-5 seconds
```

### Test 20: Parallel Requests

```
1. Open 3 browser tabs
2. Ask different questions in each tab simultaneously

Expected:
✅ All tabs get responses
✅ No crashes
✅ Responses are correct
```

---

## Common Issues & Solutions

### Issue 1: "llmops_lite not found"
```bash
# Solution: Verify llmops_lite is in parent directory
ls ../../llmops_lite

# If not there, copy it:
cp -r ../../llmops_lite .
```

### Issue 2: "ChromaDB collection empty"
```bash
# Solution: Re-run data pipeline
cd backend/data_pipeline
python uhc_scraper.py
python load_chromadb.py
```

### Issue 3: "CORS error" in browser
```bash
# Solution: Check backend .env
# Ensure: CORS_ORIGINS=http://localhost:3000
```

### Issue 4: "Module not found" in backend
```bash
# Solution: Ensure venv is activated
source venv/bin/activate

# Reinstall requirements
pip install -r requirements.txt
```

### Issue 5: "npm install fails" in frontend
```bash
# Solution: Clear npm cache
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

---

## Success Criteria Checklist

Before proceeding to deployment, ensure ALL these pass:

### Backend ✅
- [ ] Health endpoint returns 200 OK
- [ ] API docs load at /docs
- [ ] ChromaDB has policies loaded (count > 0)
- [ ] Ask endpoint returns valid responses
- [ ] Source citations included in responses
- [ ] llmops_lite caching works (repeated queries fast)
- [ ] Input validation works (rejects invalid input)
- [ ] Low confidence answers show warnings

### Frontend ✅
- [ ] Page loads without errors
- [ ] Chat interface renders correctly
- [ ] Can send messages successfully
- [ ] Responses display with formatting
- [ ] Sources show as clickable links
- [ ] Confidence badges display
- [ ] Clear chat works
- [ ] No console errors

### Integration ✅
- [ ] Frontend → Backend communication works
- [ ] CORS configured correctly
- [ ] Error messages user-friendly
- [ ] Cache reduces response time significantly
- [ ] Multiple questions work in sequence
- [ ] Edge cases handled gracefully

---

## Next Steps After Local Testing

Once all tests pass:

1. **Create Sample Data (Optional)**
   - Screenshot successful queries
   - Save sample responses for documentation

2. **Prepare for Deployment**
   - Update README with actual screenshots
   - Document any environment-specific settings
   - Create deployment checklists

3. **Deploy Backend (Render)**
   - Follow deployment guide
   - Upload ChromaDB data
   - Test production API

4. **Deploy Frontend (Vercel)**
   - Update API_URL to production
   - Deploy
   - Test production frontend

---

## Quick Start Commands (Summary)

```bash
# Terminal 1 - Backend
cd MY-HEALTH-CHATBOT/backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python data_pipeline/uhc_scraper.py
python data_pipeline/load_chromadb.py
uvicorn app.main:app --reload

# Terminal 2 - Frontend
cd MY-HEALTH-CHATBOT/frontend
npm install
npm run dev

# Browser
# Backend: http://localhost:8000/docs
# Frontend: http://localhost:3000
```

---

**Ready to test? Let's go! 🚀**
