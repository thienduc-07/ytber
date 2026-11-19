# PRODUCTION CLOUD DEPLOYMENT GUIDE (ZERO-BUDGET ARCHITECTURE)
**Project:** Zero-Budget AI Video Studio (Vietnamese Shorts)  
**Document ID:** `docs/DEPLOYMENT_GUIDE.md`  
**Target Cost:** $0.00 / Month  
**Last Updated:** 2026-11-19  

---

## 1. Cloud Architecture Overview

The platform uses a decoupled serverless/cloud architecture ensuring high availability and zero operational costs:

```
[ FRONTEND ]   --> Cloudflare Pages (Free, Unlimited Bandwidth, Global CDN, SSL)
[ AUTH & DB ]  --> Supabase (Free Tier: 50k MAU Auth, 500 MB PostgreSQL, RLS)
[ STORAGE ]    --> Supabase Storage (1 GB Free Tier with 2-hour audio auto-purge)
[ API GATEWAY]--> Render.com / Fly.io Free Web Service (FastAPI stateless coordination)
[ RENDERING ]  --> Client-Side In-Browser Engine (User's browser GPU via WebCodecs)
```

---

## 2. Step 1: Supabase Configuration (Database & Auth)

1. **Create Supabase Project:**
   * Go to [supabase.com](https://supabase.com) and create a free project (Region: `Singapore (ap-southeast-1)` or `Tokyo` for lowest Vietnam latency).
2. **Apply Database Migration:**
   * Open the **SQL Editor** in the Supabase Dashboard.
   * Copy and run the entire SQL migration script from `supabase/migrations/20261119_initial_schema.sql`.
   * Verify that all 7 tables (`profiles`, `projects`, `episodes`, `scenes`, `scene_assets`, `render_jobs`, `user_quotas`) are created with Row Level Security (RLS) active.
3. **Configure Storage Bucket:**
   * Go to **Storage** -> Create a new bucket named `audio-stems`.
   * Set bucket to **Public** for streaming audio previews.
   * Add RLS storage policy: authenticated users can upload and read.
4. **Retrieve API Keys:**
   * Go to **Project Settings** -> **API**.
   * Note `Project URL`, `anon public` key, and `service_role secret` key.

---

## 3. Step 2: Backend API Deployment (FastAPI)

1. **Deploy to Render.com (or Fly.io / Railway Free Tier):**
   * Connect your GitHub repository to [render.com](https://render.com).
   * Create a **Web Service**:
     * Environment: `Python 3`
     * Root Directory: `backend`
     * Build Command: `pip install -r requirements.txt`
     * Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
2. **Configure Environment Variables in Render:**
   * `ENVIRONMENT`: `production`
   * `SUPABASE_URL`: `https://your-project.supabase.co`
   * `SUPABASE_ANON_KEY`: `eyJhbGciOi...`
   * `SUPABASE_SERVICE_ROLE_KEY`: `eyJhbGciOi...`
   * `GROQ_API_KEY`: `gsk_...` (Obtain free at [console.groq.com](https://console.groq.com))
   * `CORS_ORIGINS`: `["https://your-app.pages.dev", "https://yourdomain.com"]`
3. **Verify Deployment:**
   * Visit `https://your-api.onrender.com/api/v1/health` and verify `status: "healthy"`.

---

## 4. Step 3: Frontend Deployment (Cloudflare Pages)

1. **Connect to Cloudflare Pages:**
   * Go to [dash.cloudflare.com](https://dash.cloudflare.com) -> **Workers & Pages** -> **Create application** -> **Pages** -> **Connect to Git**.
2. **Build Settings:**
   * Framework preset: `Vite`
   * Root directory: `frontend`
   * Build command: `npm run build`
   * Build output directory: `dist`
3. **Configure Environment Variables:**
   * `VITE_SUPABASE_URL`: `https://your-project.supabase.co`
   * `VITE_SUPABASE_ANON_KEY`: `eyJhbGciOi...`
   * `VITE_API_BASE_URL`: `https://your-api.onrender.com`
4. **Deploy & Custom Domain:**
   * Click **Save and Deploy**. Cloudflare automatically builds and deploys to `*.pages.dev`.
   * (Optional): Add your custom domain under **Custom domains** in Cloudflare Pages with free SSL.

---

## 5. Verification Checklist

- [ ] Visit frontend URL on Google Chrome.
- [ ] Sign up a new user account (confirm email if enabled, or disable email confirmation for testing in Supabase Auth settings).
- [ ] Verify profile record is automatically created in `public.profiles`.
- [ ] Submit a Vietnamese script to test Groq/Gemini structuring.
- [ ] Verify WebCodecs hardware rendering exports a clean 1080×1920 MP4 file in under 10 seconds.
