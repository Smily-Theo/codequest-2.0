# CodeQuest — Vercel Ready

A static, hackathon-ready CodeQuest prototype generated from the Stitch design.

## Deploy to Vercel

### Option 1 — GitHub + Vercel
1. Create a GitHub repository named `codequest`.
2. Upload the contents of this folder to the repository.
3. Import the repository into Vercel.
4. Framework preset: **Other** (or leave auto-detected).
5. Build command: `npm run build`.
6. Output directory: `.`.
7. Click **Deploy**.

### Option 2 — Vercel CLI
```bash
npm install -g vercel
cd codequest
vercel
```
Follow the prompts and run `vercel --prod` for production.

## Notes
- This Vercel version is intentionally static so it deploys without a Python server.
- Player progress is stored in browser `localStorage` for the demo.
- The coding challenge runner is a client-side **demo checker**, not a secure Python execution sandbox. Do not claim it executes arbitrary Python in production.
- The AI Tutor is a local progressive-hint demo. For a production AI tutor, add a server-side API route and keep provider API keys out of the browser.
