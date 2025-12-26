# Deployment Guide

This guide walks through deploying the UHC Insurance Chatbot to production.

## Prerequisites

- GitHub account
- Render account (for backend) - [render.com](https://render.com)
- Vercel account (for frontend) - [vercel.com](https://vercel.com)
- llmops_lite configured with LiteLLM proxy credentials

---

## Backend Deployment (Render)

### Step 1: Prepare Backend

```bash
# 1. Load data into ChromaDB locally
cd backend
python data_pipeline/uhc_scraper.py    # Scrape policies
python data_pipeline/load_chromadb.py  # Load into ChromaDB

# 2. Test backend locally
uvicorn app.main:app --reload
# Visit http://localhost:8000/docs to test API
```

### Step 2: Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit: UHC Insurance Chatbot"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/uhc-chatbot.git
git push -u origin main
```

### Step 3: Deploy to Render

1. **Create New Web Service**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository

2. **Configure Service**
   - Name: `uhc-chatbot-api`
   - Region: Oregon (US West)
   - Branch: `main`
   - Build Command: `cd backend && pip install -r requirements.txt`
   - Start Command: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`

3. **Set Environment Variables**
   ```
   LITELLM_PROXY_BASE_URL=<your_litellm_proxy_url>
   LITELLM_PROXY_SECRET_KEY=<your_secret_key>
   AWS_ACCESS_KEY_ID=<optional>
   AWS_SECRET_ACCESS_KEY=<optional>
   CORS_ORIGINS=https://your-frontend.vercel.app
   APP_ENV=production
   DEBUG=False
   ```

4. **Deploy**
   - Click "Create Web Service"
   - Wait for build to complete (~5 minutes)
   - Note your backend URL: `https://uhc-chatbot-api.onrender.com`

5. **Upload ChromaDB Data**

   **Option A: Include in Git (Small datasets)**
   ```bash
   # Remove chroma_data from .gitignore
   git add backend/chroma_data
   git commit -m "Add ChromaDB data"
   git push
   ```

   **Option B: Upload via Render Shell (Recommended)**
   - In Render dashboard, go to your service
   - Click "Shell" tab
   - Run scraper and loader in production:
   ```bash
   cd backend
   python data_pipeline/uhc_scraper.py
   python data_pipeline/load_chromadb.py
   ```

### Step 4: Test Backend

```bash
# Test health endpoint
curl https://uhc-chatbot-api.onrender.com/api/health

# Test query endpoint
curl -X POST https://uhc-chatbot-api.onrender.com/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is bariatric surgery coverage?", "provider": "UHC"}'
```

---

## Frontend Deployment (Vercel)

### Step 1: Configure Environment

```bash
cd frontend

# Create .env.local for production
cat > .env.local << EOF
NEXT_PUBLIC_API_URL=https://uhc-chatbot-api.onrender.com
EOF
```

### Step 2: Deploy to Vercel

**Option A: Vercel CLI**
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
cd frontend
vercel

# Follow prompts:
# - Link to existing project or create new
# - Set framework: Next.js
# - Set build command: npm run build
# - Set output directory: .next
```

**Option B: Vercel Dashboard**
1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click "Add New" → "Project"
3. Import your GitHub repository
4. Configure:
   - Framework: Next.js
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `.next`
5. Add Environment Variable:
   - Key: `NEXT_PUBLIC_API_URL`
   - Value: `https://uhc-chatbot-api.onrender.com`
6. Click "Deploy"

### Step 3: Update Backend CORS

After deployment, update backend CORS settings in Render:

1. Go to Render dashboard → Your service → Environment
2. Update `CORS_ORIGINS`:
   ```
   https://your-frontend.vercel.app,http://localhost:3000
   ```
3. Save and redeploy

### Step 4: Test Frontend

Visit your Vercel URL: `https://your-frontend.vercel.app`

---

## Post-Deployment Checklist

- [ ] Backend health endpoint returns 200: `/api/health`
- [ ] Frontend loads without errors
- [ ] Chat interface sends/receives messages
- [ ] Source citations display correctly
- [ ] Confidence scores show for answers
- [ ] Edge cases handled (empty input, invalid questions)
- [ ] Low-confidence answers show warning
- [ ] llmops_lite caching works (repeated queries are instant)

---

## Monitoring & Maintenance

### Render Monitoring
- Dashboard shows logs, metrics, and health
- Free tier sleeps after 15min inactivity (30s cold start)
- Upgrade to paid tier for 24/7 uptime

### Vercel Monitoring
- Analytics available in dashboard
- Free tier: 100GB bandwidth/month
- Logs available for debugging

### llmops_lite Monitoring
- Check DynamoDB cache hit rate
- Monitor token usage via Langfuse (if configured)
- Review Slack alerts for critical errors

---

## Troubleshooting

### Backend Issues

**Issue: "ChromaDB collection not found"**
- Solution: Run data pipeline in Render shell
```bash
cd backend
python data_pipeline/load_chromadb.py
```

**Issue: "llmops_lite import error"**
- Solution: Ensure llmops_lite is in parent directory or installed as package
- Check environment variables are set correctly

**Issue: "504 Gateway Timeout"**
- Solution: Free tier on Render has 30s timeout - optimize queries or upgrade

### Frontend Issues

**Issue: "CORS error when calling API"**
- Solution: Update `CORS_ORIGINS` in backend environment variables

**Issue: "API_URL undefined"**
- Solution: Set `NEXT_PUBLIC_API_URL` in Vercel environment variables

---

## Updating After Changes

### Backend Updates
```bash
git add backend/
git commit -m "Update backend"
git push
# Render auto-deploys on push to main
```

### Frontend Updates
```bash
git add frontend/
git commit -m "Update frontend"
git push
# Vercel auto-deploys on push to main
```

### Data Updates
```bash
# Re-scrape policies and reload ChromaDB
cd backend
python data_pipeline/uhc_scraper.py
python data_pipeline/load_chromadb.py
# Commit and push if using Git storage
```

---

## Cost Estimation

### Free Tier (Recommended for Assignment)
- **Render:** Free tier
- **Vercel:** Free tier
- **llmops_lite/LLM API:** ~$0.01 per 100 queries (with caching)
- **Total:** $0-5/month for light usage

### Production Tier
- **Render:** $7/month (always-on, faster)
- **Vercel:** $20/month (analytics, more bandwidth)
- **LLM API:** ~$50/month (moderate usage with caching)
- **DynamoDB:** ~$5/month (caching storage)
- **Total:** ~$82/month

---

## Security Best Practices

1. **Never commit secrets**
   - Use `.env` files (gitignored)
   - Set secrets in dashboard

2. **Use environment variables**
   - API keys in Render/Vercel dashboards
   - Never hardcode credentials

3. **Enable CORS properly**
   - Whitelist specific domains
   - Don't use `allow_origins=["*"]` in production

4. **Rate limiting** (Optional)
   - Add rate limiting middleware
   - Prevent abuse

---

## Next Steps

- [ ] Set up custom domain
- [ ] Configure SSL certificates (automatic on Vercel/Render)
- [ ] Add analytics (Google Analytics, PostHog)
- [ ] Set up error tracking (Sentry)
- [ ] Add user authentication (optional)
- [ ] Implement feedback collection

---

**Need Help?**
- Render Docs: https://render.com/docs
- Vercel Docs: https://vercel.com/docs
- Next.js Docs: https://nextjs.org/docs
