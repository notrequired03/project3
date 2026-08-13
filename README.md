# ChatHere.online - Ryanair-Style Twitter Meme AI Bot & Control Dashboard 🔥

An automated Twitter/X bot and management dashboard designed for **chathere.online**. The bot adopts an unhinged, hilarious corporate banter persona (inspired by Ryanair's official Twitter)—posting funny memes, trolling legacy video/chat sites, and auto-replying to trending keywords using Google's **Gemini AI API** (`google-genai` SDK with `gemini-3.6-flash`).

---

## 🌟 Key Features

1. **Ryanair Brand Personality**: Sarcastic, funny, self-aware posts promoting `chathere.online`, roasting slow Discord calls, dead Omegle clones, and relatable internet moments.
2. **Web Dashboard UI**:
   - **Credentials Tab**: Enter your Twitter username, email, password, and Google Gemini API key securely.
   - **Schedule & Controls**: Set your posting interval (e.g., every 30 minutes for ~48 posts/day), enable/disable auto-replying, and manage target keywords.
   - **AI Persona Studio**: Customize instructions and target sites to roast.
   - **Meme Studio**: Preview Gemini-generated tweets live or post custom tweets instantly.
   - **Live Activity Console**: Stream live logs of Twitter actions and AI responses.
3. **No Official Twitter API Costs**: Powered by `twikit` (web-emulation API) with cookie persistence to avoid paying $0.015/tweet on official API tiers.
4. **Render Ready**: Includes `render.yaml`, `Procfile`, and `.gitignore` for 1-click cloud deployment.

---

## 🚀 How to Run Locally

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Web Server
```bash
python app.py
```
Open your browser and navigate to: `http://localhost:5000`

### 3. Setup via Web Dashboard
1. Go to the **Credentials** tab and enter:
   - Your Twitter Username
   - Your Twitter Account Email
   - Your Twitter Password
   - Your Gemini API Key (Get a free key at [Google AI Studio](https://aistudio.google.com/))
2. Click **Save Credentials**.
3. Toggle the **Bot Status** switch at the top right to **ACTIVE**.

---

## 📦 How to Push to GitHub & Deploy to Render

### Step 1: Initialize Git and Push to Your GitHub Repository
Run the following commands in your project directory:

```bash
git add .
git commit -m "Initial commit - ChatHere Ryanair Twitter AI Bot"
git branch -M main
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/YOUR_REPO_NAME.git
git push -u origin main
```

### Step 2: Deploy to Render (Free Cloud Hosting)
1. Sign up or log into [Render.com](https://render.com/).
2. Click **New +** -> **Web Service**.
3. Select **Build and deploy from a Git repository** and connect your GitHub account.
4. Choose your new repository (`YOUR_REPO_NAME`).
5. Render will automatically detect `render.yaml` / Python configuration:
   - **Name**: `chathere-twitter-bot`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
6. Click **Create Web Service**.

Once deployed, Render will provide a live URL (e.g., `https://chathere-twitter-bot.onrender.com`). Open the link, input your credentials in the dashboard, and your bot will run automatically in the cloud 24/7!

---

## 🛡️ Safety & Anti-Ban Guidelines
- The bot includes built-in randomized safety delays (30–90 seconds) between replies and uses cookie caching (`cookies.json`) to prevent frequent log-in challenges.
- Posting every **30 minutes** yields ~48 posts/day, which is well within standard account activity thresholds.
