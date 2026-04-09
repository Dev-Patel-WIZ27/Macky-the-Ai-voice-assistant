# Macky AI – Futuristic Virtual Assistant 🤖❄️

> A modern, web-based AI assistant portal featuring an "Arctic Blue" aura and smart simulation intelligence.

---

## ✨ Features

- **🌐 Browser-Based Portal** — Accessible anywhere via `localhost:8001`.
- **🗣️ Voice & Text Support** — Talk to Macky using your mic or type manually.
- **🌀 Pulse Feedback** — Futuristic AI Orb pulses visually while Macky is listening or speaking.
- **🌩️ Smart Simulation** — Intelligent local brain for core commands (Time, Apps) and mock conversations.
- **⚙️ OpenAI Integration** — Built-in settings panel to add your own API key for full GPT-4 power.
- **⚡ Fast Response** — Built with FastAPI and native Web Speech APIs for near-instant interaction.

---

## 🗂️ Project Structure

```
macky-ai/
├── server.py       # FastAPI backend logic
├── index.html      # UI structure & templates
├── style.css       # Arctic Blue "Aura" design system
├── app.js          # Logic, Voice Recognition & Synthesis
└── README.md
```

---

## 🚀 Getting Started

### 1. Launch the Backend
```bash
# Navigate to the project folder
cd macky-virtual-assistant

# Start the FastAPI server
python server.py
```

### 2. Launch the UI
```bash
# In a new terminal, serve the frontend
python -m http.server 8001
```

### 3. Open in Browser
Visit 👉 **[http://localhost:8001](http://localhost:8001)**

---

## 🧭 Commands to Try

- *"What is the time?"*
- *"Open YouTube"* (or Google, GitHub, Wikipedia)
- *"Tell me a joke"*
- *"How are you today?"*

---

## 🎨 Design System

| Token | Value |
|-------|-------|
| Accent | `#38bdf8` (Arctic Blue) |
| Background | `#050a0f` |
| Style | "Aura" (Glassmorphism + Neon) |
| Fonts | Syncopate, Outfit |

---

## ☁️ Deployment (Render)

Macky is ready to be hosted on **Render** as a single Web Service.

1. **Connect GitHub:** Link your `Macky-the-Ai-voice-assistant` repo to Render.
2. **Select Web Service:** Create a new "Web Service".
3. **Configuration:**
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn server:app --host 0.0.0.0 --port $PORT`
4. **Environment Variables:** (Optional) Add `OPENAI_API_KEY` in the Render dashboard if you want it pre-configured.

---

## 🖋️ Author

**Dev Patel** — [@Dev-Patel-WIZ27](https://github.com/Dev-Patel-WIZ27)

---

## 📄 License

MIT License. Feel free to use and expand!
