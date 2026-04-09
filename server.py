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
    query = query.lower()
    # Optimize for Indian stocks if Reliance or other major companies mentioned
    if "reliance" in query and "stock" in query:
        return "reliance industries share price live nse moneycontrol"
    if "stock" in query or "price" in query or "share" in query:
        if "india" in query or "nse" in query or "bse" in query:
            return f"{query} live price nse"
        return f"{query} real-time stock price"
    return query

def get_clean_site_name(url):
    try:
        domain = urlparse(url).netloc
        if domain.startswith("www."):
            domain = domain[4:]
        # Get the first part of the domain and capitalize it
        return domain.split('.')[0].capitalize()
    except:
        return "the web"

def perform_web_search(query):
    # Optimize the search query for better accuracy
    search_query = optimize_query(query)
    try:
        with DDGS() as ddgs:
            # Retrieve up to 5 results for better factual density
            results = list(ddgs.text(search_query, max_results=5))
            if results:
                # We prioritize results that look like they have price data
                best_results = []
                for res in results:
                    # Look for currency symbols or "₹" specifically for high-relevance info
                    if any(c in res['body'] for c in ["₹", "$", "Rs", "price", "trading"]):
                        best_results.append(res)
                
                # If we found high-quality price data, use that
                final_res = best_results[0] if best_results else results[0]
                
                site = get_clean_site_name(final_res['href'])
                return {
                    "site": site,
                    "body": final_res['body'],
                    "title": final_res['title']
                }
    except Exception as e:
        print(f"Search Error: {e}")
    return None

def wrap_with_friendly_personality(data, query):
    if not data:
        return "Hey buddy, I tried digging into the web for you but couldn't find anything solid. Want to try asking in a different way?"
    
    # Friendly, helpful intro phrases
    intro_phrases = [
        f"I've got some info on that for you! According to **{data['site']}**, ",
        f"I did a quick search buddy. I see on **{data['site']}** that ",
        f"Check this out! **{data['site']}** is reporting that ",
        f"Found it! My research on **{data['site']}** shows that "
    ]
    
    # Closing phrases to feel like a friend
    closing_phrases = [
        ". Hope that helps you out!",
        ". Pretty interesting, right?",
        ". I'm here if you need anything else!",
        ". Let me know if you want me to dig deeper, buddy!"
    ]
    
    response = random.choice(intro_phrases) + data['body'] + random.choice(closing_phrases)
    return response

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
    local_time: str = ""

# Mock responses for absolute fallback
MOCK_RESPONSES = [
    "I'm Macky, your Arctic assistant. How can I help you today, buddy?",
    "That's an interesting question! I'm here to help, buddy.",
    "System check complete. All protocols are green, buddy.",
    "I'm currently running in high-efficiency Friendly Mode, buddy."
]

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    query = request.query.lower()
    
    # 1. Check for specific commands (System tasks)
    if "close macky" in query:
        return {"response": "Goodbye buddy", "type": "shutdown"}

    if "time" in query:
        t = request.local_time if request.local_time else datetime.datetime.now().strftime("%I:%M %p")
        return {"response": f"The current time is {t}, buddy.", "type": "system"}
    
    sites = {
        "youtube": "https://youtube.com",
        "google": "https://google.com",
        "wikipedia": "https://wikipedia.com",
        "github": "https://github.com"
    }
    
    for site, url in sites.items():
        if f"open {site}" in query:
            return {"response": f"Opening {site} for you, buddy.", "type": "browser", "url": url}

    # 2. Check for real-time information requests (Web Search as Primary Intelligence)
    real_time_keywords = [
        "news", "latest", "weather", "price", "who is", "what is", "current", 
        "today", "stock", "share", "crypto", "bitcoin", "market", "how is", "where is", "report"
    ]
    
    # If it matches keywords OR if no API key is provided, we use the WEB
    if any(k in query for k in real_time_keywords) or not request.apikey:
        search_data = perform_web_search(request.query)
        if search_data:
            friendly_response = wrap_with_friendly_personality(search_data, request.query)
            return {"response": friendly_response, "type": "web_search"}

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

    # 4. Final Fallback (Random Macky phrase)
    response = random.choice(MOCK_RESPONSES)
    return {"response": response, "type": "simulation"}

@app.get("/status")
async def status():
    return {"status": "online", "mode": "Friendly Intelligence"}

# Serve Frontend from 'public' folder
app.mount("/", StaticFiles(directory="public", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
