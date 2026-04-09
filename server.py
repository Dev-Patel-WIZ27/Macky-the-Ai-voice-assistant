from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import datetime
import random
from urllib.parse import urlparse
import openai
from duckduckgo_search import DDGS

app = FastAPI()

def optimize_query(query):
    query = query.lower().strip()
    # Handle specific stock market keywords for Reliance/India
    if "reliance" in query and ("stock" in query or "price" in query or "share" in query):
        return "reliance industries share price live nse moneycontrol"
    if any(k in query for k in ["stock", "price", "share", "market"]):
        # Add 'live' and 'nse' for Indian context if not present for better accuracy
        if "india" in query or "nse" in query or "bse" in query:
             return f"{query} live price"
        return f"{query} share price live nse"
    return query

def get_clean_site_name(url):
    try:
        domain = urlparse(url).netloc
        if domain.startswith("www."):
            domain = domain[4:]
        return domain.split('.')[0].capitalize()
    except:
        return "the web"

def perform_web_search(query):
    optimized = optimize_query(query)
    try:
        with DDGS() as ddgs:
            # Get up to 5 results to find the most accurate one
            results = list(ddgs.text(optimized, max_results=5))
            if results:
                # Prioritize snippets with currency symbols or high keyword density
                high_quality = []
                for res in results:
                    body = res['body'].lower()
                    if any(c in res['body'] for c in ["₹", "Rs", "INR", "$", "price", "traded"]):
                        high_quality.append(res)
                
                # Pick the best result found
                target = high_quality[0] if high_quality else results[0]
                site = get_clean_site_name(target['href'])
                
                return {
                    "site": site,
                    "body": target['body'],
                    "title": target['title']
                }
    except Exception as e:
        print(f"Search Error: {e}")
    return None

def wrap_with_friendly_personality(data, query):
    if not data:
        return "Hey buddy, I tried digging into the web for you but couldn't find anything solid right now. Want to try asking in a different way?"
    
    intros = [
        f"I've got some info on that for you, buddy! According to **{data['site']}**, ",
        f"I did a quick research for you. I see on **{data['site']}** that ",
        f"Check this out, buddy! **{data['site']}** is reporting that ",
        f"Found it! My research on **{data['site']}** shows that "
    ]
    
    closings = [
        ". Hope that helps you out!",
        ". Pretty interesting, right buddy?",
        ". I'm here if you need anything else!",
        ". Let me know if you want me to dig deeper for you!"
    ]
    
    return random.choice(intros) + data['body'] + random.choice(closings)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    query: str
    apikey: str = ""
    local_time: str = ""

MOCK_RESPONSES = [
    "I'm Macky, your Arctic assistant. How can I help you today, buddy?",
    "That's an interesting question! I'm here to help you out, buddy.",
    "System check complete. All protocols are green, buddy.",
    "I'm currently running in high-efficiency Friendly Mode, buddy."
]

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    query = request.query.lower()
    
    if "close macky" in query:
        return {"response": "Goodbye buddy", "type": "shutdown"}

    if "time" in query:
        t = request.local_time if request.local_time else datetime.datetime.now().strftime("%I:%M %p")
        return {"response": f"The current time is {t}, buddy.", "type": "system"}
    
    sites = {
        "youtube": "https://youtube.com", "google": "https://google.com",
        "wikipedia": "https://wikipedia.com", "github": "https://github.com"
    }
    
    for site, url in sites.items():
        if f"open {site}" in query:
            return {"response": f"Opening {site} for you, buddy.", "type": "browser", "url": url}

    # Research and Information Fallback
    search_data = perform_web_search(request.query)
    if search_data:
        friendly_response = wrap_with_friendly_personality(search_data, request.query)
        return {"response": friendly_response, "type": "web_search"}

    # Handle AI logic if no search results found
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
            return {"response": f"AI Error: {str(e)}. Reverting to buddy mode.", "type": "error"}

    return {"response": random.choice(MOCK_RESPONSES), "type": "simulation"}

@app.get("/status")
async def status():
    return {"status": "online", "mode": "Ultra Friendly Intelligence"}

app.mount("/", StaticFiles(directory="public", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
