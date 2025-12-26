# Testing Checklist - Complete Before Deployment

Use this checklist to ensure everything works before deploying.

---

## Pre-Testing Setup

- [ ] Python 3.11+ installed (`python3 --version`)
- [ ] Node.js 18+ installed (`node --version`)
- [ ] llmops_lite exists in parent directory
- [ ] llmops_lite credentials configured (LITELLM_PROXY_BASE_URL, LITELLM_PROXY_SECRET_KEY)

---

## Backend Testing

### Setup
- [ ] Virtual environment created (`python3 -m venv venv`)
- [ ] Virtual environment activated (`source venv/bin/activate`)
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file created and configured

### Data Pipeline
- [ ] Scraper runs successfully (`python data_pipeline/uhc_scraper.py`)
- [ ] Policies scraped (at least 3-5 for testing)
- [ ] ChromaDB loader runs (`python data_pipeline/load_chromadb.py`)
- [ ] `chroma_data/` directory created with files
- [ ] ChromaDB has documents (check logs for count > 0)

### API Server
- [ ] Server starts without errors (`uvicorn app.main:app --reload`)
- [ ] llmops_lite imported successfully (check startup logs)
- [ ] ChromaDB initialized (check startup logs)
- [ ] Health endpoint works: `curl http://localhost:8000/api/health`
- [ ] API docs load: http://localhost:8000/docs
- [ ] Ask endpoint works (test via /docs or curl)

---

## Frontend Testing

### Setup
- [ ] Dependencies installed (`npm install`)
- [ ] `.env.local` created with API_URL
- [ ] Server starts (`npm run dev`)
- [ ] No errors in terminal
- [ ] Page loads: http://localhost:3000

### Visual Checks
- [ ] Header shows "UHC Insurance Policy Assistant"
- [ ] Three info cards visible
- [ ] Chat interface renders
- [ ] Input box present
- [ ] Send button present
- [ ] Example questions shown
- [ ] No errors in browser console (F12)

---

## Integration Testing

### Basic Flow
- [ ] Can type in input box
- [ ] Send button clickable
- [ ] Question sends successfully
- [ ] Loading indicator appears
- [ ] Response appears (within 5 seconds)
- [ ] Answer text formatted properly
- [ ] Sources section displays
- [ ] Confidence badge shows
- [ ] Timestamp displays

### Edge Cases
- [ ] Empty input rejected or button disabled
- [ ] Very long question (>500 chars) rejected with error
- [ ] Non-medical question returns polite refusal
- [ ] Low confidence answers show warning message
- [ ] Clear chat button works
- [ ] Multiple questions work in sequence

### Caching Test
- [ ] Ask same question twice
- [ ] Second response much faster (<1 second)
- [ ] Responses identical

### Sources Test
- [ ] Sources section shows for answers
- [ ] Each source has title and policy ID
- [ ] "View" buttons present
- [ ] Clicking "View" opens UHC policy page

### Error Handling
- [ ] Stop backend → Frontend shows connection error
- [ ] Invalid API URL → Graceful error message
- [ ] Backend responds even when ChromaDB empty

---

## Performance Testing

- [ ] First question: 3-5 seconds ✓
- [ ] Cached question: <500ms ✓
- [ ] Page load: <2 seconds ✓
- [ ] No memory leaks after 10+ questions
- [ ] Chat history scrolls smoothly

---

## Code Quality

### Backend
- [ ] No hardcoded credentials
- [ ] Environment variables used
- [ ] Proper error messages (not raw exceptions)
- [ ] Input validation works
- [ ] Type hints present (Pydantic models)

### Frontend
- [ ] No console errors
- [ ] No console warnings
- [ ] Responsive design (test on mobile)
- [ ] Proper TypeScript types
- [ ] Clean code formatting

---

## Documentation

- [ ] README.md has all required sections
- [ ] QUICKSTART.md provides simple setup
- [ ] LOCAL_TESTING_GUIDE.md is comprehensive
- [ ] DEPLOYMENT.md ready for production
- [ ] Code comments where needed
- [ ] Environment variables documented

---

## Git & GitHub

- [ ] Git repository initialized
- [ ] All code committed
- [ ] `.gitignore` properly configured
- [ ] No secrets in commits
- [ ] README includes:
  - [ ] Project description
  - [ ] Setup instructions
  - [ ] Architecture diagrams
  - [ ] Tech stack
  - [ ] Usage guide

---

## Pre-Deployment Final Checks

### Backend Ready?
- [ ] All tests pass locally
- [ ] ChromaDB populated with real data
- [ ] Environment variables documented
- [ ] No errors in logs
- [ ] Health endpoint returns 200

### Frontend Ready?
- [ ] Builds successfully (`npm run build`)
- [ ] No build errors
- [ ] No TypeScript errors
- [ ] Environment variables documented
- [ ] API URL configurable

### Documentation Ready?
- [ ] README has HLD diagram
- [ ] README has LLD explanation
- [ ] README has step-by-step usage guide
- [ ] All links work
- [ ] Screenshots included (optional but recommended)

---

## Deployment Checklist

### Backend (Render)
- [ ] GitHub repo created and pushed
- [ ] Render service created
- [ ] Environment variables set in Render
- [ ] ChromaDB data uploaded
- [ ] Build succeeds
- [ ] Health endpoint accessible
- [ ] Backend URL noted for frontend

### Frontend (Vercel)
- [ ] Vercel project created
- [ ] GitHub repo connected
- [ ] Environment variable set (NEXT_PUBLIC_API_URL)
- [ ] Build succeeds
- [ ] Frontend loads
- [ ] Can send messages
- [ ] CORS configured in backend

### Final Production Test
- [ ] End-to-end flow works in production
- [ ] Sources clickable
- [ ] Responses correct
- [ ] Caching works
- [ ] Error handling works

---

## Submission Checklist

- [ ] GitHub repo URL ready
- [ ] README includes live demo URLs
- [ ] README includes architecture (HLD/LLD)
- [ ] All code committed and pushed
- [ ] No TODOs left in code
- [ ] Professional commit messages
- [ ] Clean code (no commented-out blocks)

---

## Score Yourself

### Must Have (Assignment Requirements)
- [ ] Good interfaces ✓
- [ ] Deployed and ready to use ✓
- [ ] Gracefully handles edge cases ✓
- [ ] Easy to extend for other providers ✓
- [ ] GitHub repo with code ✓
- [ ] README with demo URL ✓
- [ ] README with HLD/LLD ✓

### Bonus Points
- [ ] Source citations
- [ ] Confidence scoring
- [ ] Smart caching (llmops_lite)
- [ ] Professional UI/UX
- [ ] Comprehensive documentation
- [ ] CI/CD pipeline
- [ ] Type safety (Pydantic + TypeScript)

---

## When Everything is ✓

You're ready to deploy! 🚀

**Next Step:** Follow `DEPLOYMENT.md`

---

**Total Checkboxes:** 100+
**Passing Score:** All "Must Have" items checked
**Excellent Score:** 90%+ checked
