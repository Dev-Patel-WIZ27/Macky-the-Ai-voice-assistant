from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import datetime
import random
import openai
from duckduckgo_search import DDGS

app = FastAPI()

def perform_web_search(query):
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
            if results:
                # Format the top results into a string
                search_data = "\n".join([f"- {r['title']}: {r['body']}" for r in results])
                return f"I found some information from the web:\n\n{search_data}"
    except Exception as e:
        print(f"Search Error: {e}")
    return None

# Enable CORS for frontend interaction
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    query: str
    apikey: str = ""

# Mock responses for Simulation Mode
MOCK_RESPONSES = [
    "I'm Macky, your Arctic assistant. How can I help you today?",
    "That's an interesting question! In simulation mode, I can tell you that the future looks bright.",
    "I'm processing your request... Wait, I'm just a simulation for now! But I'm still learning.",
    "Arctic temperatures are stable. My circuits are running efficiently.",
    "System check complete. All protocols are green.",
    "I can open websites like YouTube or Google if you ask me to!",
    "I'm currently running in high-efficiency Mock Mode."
]

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    query = request.query.lower()
    
    # 1. Check for specific commands (System tasks)
    if "close macky" in query:
        return {"response": "Goodbye boss", "type": "shutdown"}

    if "time" in query:
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        return {"response": f"The current time is {current_time}.", "type": "system"}
    
    sites = {
        "youtube": "https://youtube.com",
        "google": "https://google.com",
        "wikipedia": "https://wikipedia.com",
        "github": "https://github.com"
    }
    
    for site, url in sites.items():
        if f"open {site}" in query:
            return {"response": f"Opening {site} for you.", "type": "browser", "url": url}

    # 2. Check for real-time information requests (Web Search)
    real_time_keywords = ["news", "latest", "weather", "price", "who is", "what is", "current", "today"]
    if any(k in query for k in real_time_keywords) and not request.apikey:
        search_result = perform_web_search(request.query)
        if search_result:
            return {"response": search_result, "type": "web_search"}

    # 3. Real ChatGPT Logic (if API key provided)
    if request.apikey and len(request.apikey) > 20:
        try:
            openai.api_key = request.apikey
            response = openai.Completion.create(
                model="text-davinci-003",
                prompt=f"User: {request.query}\nAssistant:",
                max_tokens=150
            )
            return {"response": response.choices[0].text.strip(), "type": "ai"}
        except Exception as e:
            return {"response": f"AI Error: {str(e)}. Reverting to simulation.", "type": "error"}

    # 3. Simulation Logic (Default)
    response = random.choice(MOCK_RESPONSES)
    return {"response": response, "type": "simulation"}

@app.get("/status")
async def status():
    return {"status": "online", "mode": "Smart Simulation"}

# Serve Frontend from 'public' folder
app.mount("/", StaticFiles(directory="public", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
