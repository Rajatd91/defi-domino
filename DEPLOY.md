# 🚀 Deploy in 5 minutes

Run these commands top-to-bottom. Don't skip steps.

---

## Step 1 — Authenticate GitHub CLI (one-time, ~30 sec)

```bash
gh auth login
# Choose: GitHub.com → HTTPS → Login with a web browser
# Paste the one-time code into the browser, hit Authorize
```

---

## Step 2 — Push the repo (1 command, ~10 sec)

From the project root (`/Users/rajat/Desktop/DeFi project`):

```bash
cd "/Users/rajat/Desktop/DeFi project"
gh repo create defi-domino --public --source=. --remote=origin --push --description "DeFi Domino — Protocol Contagion Risk Mapper. Stress-test the DeFi ecosystem against any single-protocol failure."
```

**Your code link is now:**
```
https://github.com/<your-username>/defi-domino
```

---

## Step 3 — Deploy live to Streamlit Cloud (free, ~3 min)

1. Open: **https://share.streamlit.io/deploy**
2. Sign in with GitHub (same account you just pushed to)
3. Fill in:
   - Repository: `<your-username>/defi-domino`
   - Branch: `main`
   - Main file path: `app.py`
   - App URL: `defi-domino` (or any available subdomain)
4. Click **Deploy**

Streamlit Cloud will install requirements.txt and boot the app in 1–3 minutes.

**Your live demo link will be:**
```
https://defi-domino-<your-username>.streamlit.app
```

If Streamlit Cloud is slow, fallback: paste the GitHub repo link with a note in the submission saying *"Run locally with `streamlit run app.py` — full instructions in README.md"*. Most judges will appreciate that the project boots in one command.

---

## Step 4 — Upload the deck

1. Open https://slides.google.com → blank presentation → File → Import slides
2. Upload `presentation/DeFi_Domino_Pitch.pptx`
3. Top right → Share → "Anyone with the link" → "Viewer" → Copy link
4. Paste that link into the **Link to Presentation** field

---

## Step 5 — Record + upload the demo video

1. Open localhost:8501 in your browser
2. Use macOS screen recording (Cmd+Shift+5 → Record selected portion)
3. Follow the script in `DEMO_VIDEO.md` exactly — under 90 seconds
4. Upload to YouTube as **Unlisted**, copy the link

---

## Step 6 — Fill the form (paste from `SUBMISSION.md`)

Submit. You're done.
