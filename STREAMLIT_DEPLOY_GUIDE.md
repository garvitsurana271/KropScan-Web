# 🚀 KropScan Deployment Guide (Streamlit Community Cloud)

This guide will help you host **KropScan** for free on Streamlit Community Cloud. Your app has been refactored to run as a single-file application (`frontend.py`), eliminating the need for a separate backend server.

## 📋 Prerequisites
- A [GitHub Account](https://github.com/) (Free)
- A [Streamlit Cloud Account](https://share.streamlit.io/) (Free, sign in with GitHub)

---

## 🛠️ Step 1: Prepare Your Repository

1.  **Create a New Repository** on GitHub (e.g., `KropScan-Web`).
2.  **Upload Your Code**:
    *   Upload all files from your project folder to this new repository.
    *   **CRITICAL FILES:** Ensure these are present:
        *   `frontend.py` (This is your main app)
        *   `ai_engine.py`
        *   `chatbot.py`
        *   `auth_system.py`
        *   `community_chat.py`
        *   `requirements.txt`
        *   `kropscan_production_model.pth` (or your best model checkpoint)
        *   `model_info.json`
        *   `users.json` (Initial user database)
        *   `community_chat.json` (Initial chat history)

    > **Note on Large Files:** If your model (`.pth`) file is larger than 100MB, you cannot upload it directly to GitHub via the web interface. You must use [Git LFS](https://git-lfs.com/) or the command line.
    >
    > **Quick Command Line Upload:**
    > ```bash
    > git init
    > git add .
    > git commit -m "Initial commit"
    > git branch -M main
    > git remote add origin https://github.com/YOUR_USERNAME/KropScan-Web.git
    > git push -u origin main
    > ```

---

## ☁️ Step 2: Deploy on Streamlit Cloud

1.  Go to [share.streamlit.io](https://share.streamlit.io/).
2.  Click **"New app"**.
3.  Select **"Use existing repo"**.
4.  **Repository:** Select your `KropScan-Web` repo.
5.  **Branch:** `main`.
6.  **Main file path:** `frontend.py` (This is crucial!).
7.  Click **"Deploy!"**.

---

## ⚙️ Configuration (Optional but Recommended)

Your app uses local JSON files (`users.json`, `community_chat.json`) for data storage.
*   **On Streamlit Cloud, these files are "Ephemeral".** This means if the app restarts (which happens once a day or after inactivity), **new data will be wiped** and reset to what's in your GitHub repo.
*   **For a Class Project / Demo:** This is usually acceptable.
*   **For Permanent Storage:** You would need to connect a database like Google Sheets or Firestore, but that requires more setup.

---

## 🐛 Troubleshooting

*   **"Model not found":** Ensure `kropscan_production_model.pth` is in the root of your GitHub repo.
*   **"ModuleNotFoundError":** Check your `requirements.txt`. It should list all libraries like `torch`, `streamlit`, `opencv-python-headless` (preferred for cloud), etc.
*   **"Memory Limit Exceeded":** If the model is too big (>1GB), the free tier might crash. KropScan is optimized, so it should be fine.

## ✅ Verification
Once deployed, you will get a URL (e.g., `https://kropscan-web.streamlit.app`). You can share this link with anyone!
