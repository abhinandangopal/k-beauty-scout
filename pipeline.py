import os
import time
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import json

# Configure Gemini
# In app.py, we will set this up if the user provides an API key,
# otherwise we rely on the environment variable.
def get_gemini_model(api_key=None):
    if api_key:
        genai.configure(api_key=api_key)
    else:
        genai.configure(api_key=os.environ.get("GEMINI_API_KEY", ""))
    
    # We use gemini-1.5-pro or flash. Let's use gemini-1.5-flash for faster responses,
    # but the prompt works with gemini-1.5-pro as well.
    return genai.GenerativeModel('gemini-1.5-flash')

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

def search_query(query):
    """Fallback search using DuckDuckGo HTML or similar simple search to avoid CAPTCHAs, 
    or direct site searches."""
    # For a robust MVP without setting up Google Custom Search API, 
    # we can scrape DuckDuckGo Lite which doesn't use heavy JS.
    url = f"https://lite.duckduckgo.com/lite/"
    try:
        response = requests.post(url, headers=HEADERS, data={"q": query}, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        results = [a.text for a in soup.find_all('a', class_='result-snippet')]
        return " ".join(results)
    except Exception as e:
        return f"Error fetching search results: {e}"

def gather_brand_data(brand_name):
    """Gathers raw textual data from global and Indian retailers for the brand."""
    print(f"Gathering data for {brand_name}...")
    
    # Global Traction Search
    global_query = f"site:yesstyle.com OR site:sokoglam.com OR site:oliveyoung.com {brand_name} skincare"
    global_results = search_query(global_query)
    
    # India Saturation Search
    india_query = f"site:nykaa.com OR site:tira.com OR site:myntra.com OR site:maccaron.in {brand_name} skincare"
    india_results = search_query(india_query)
    
    return {
        "brand_name": brand_name,
        "global_presence_raw": global_results,
        "india_presence_raw": india_results
    }

def evaluate_brand_with_gemini(brand_data, model):
    """Uses Gemini API to evaluate the brand based on scraped data."""
    prompt = f"""
    You are an expert K-Beauty retail strategist for 'Glide', a platform launching international beauty brands in India.
    Your task is to evaluate the K-Beauty brand '{brand_data['brand_name']}' based on the provided raw search scrape data.
    
    Raw Global Search Data (YesStyle, SokoGlam, OliveYoung):
    {brand_data['global_presence_raw'][:2000]}
    
    Raw India Search Data (Nykaa, Tira, Myntra, Maccaron):
    {brand_data['india_presence_raw'][:2000]}
    
    Evaluate the brand based on these criteria:
    1. Market Saturation in India (0-10): 10 means ZERO presence in India (highly exclusive). 0 means already everywhere.
    2. Global Traction & Maturity (0-10): Based on global search data.
    3. Price Positioning: Categorize as 'Budget' (<$15), 'Mid-Premium' ($15-$35), or 'Luxury' (>$35). Estimate based on typical K-Beauty knowledge if not explicit in scrape.
    4. Formulation / USP: Core philosophy (e.g. Vegan, Snail Mucin, Centella, etc).
    5. Glide Launch Suitability (1-100): 
       - 40% Formulation Fit
       - 30% Price Point (Mid-Premium is best)
       - 30% Exclusivity (Low saturation in India)

    Return a STRICT JSON response exactly matching this structure (no markdown tags like ```json):
    {{
        "Brand Name": "{brand_data['brand_name']}",
        "Global Maturity Score": 8,
        "India Saturation Level": "Low",
        "India Exclusivity Score": 9,
        "Price Positioning": "Mid-Premium",
        "Formulation USP": "Brief description",
        "Suitability Score": 85,
        "Rationale": "1-2 sentence explanation"
    }}
    """
    
    # Exponential backoff for API limits
    max_retries = 5
    delays = [1, 2, 4, 8, 16]
    
    for attempt in range(max_retries):
        try:
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    response_mime_type="application/json"
                )
            )
            result = json.loads(response.text)
            return result
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(delays[attempt])
            else:
                return {
                    "Brand Name": brand_data['brand_name'],
                    "Global Maturity Score": 0,
                    "India Saturation Level": "Unknown",
                    "India Exclusivity Score": 0,
                    "Price Positioning": "Unknown",
                    "Formulation USP": "Error processing",
                    "Suitability Score": 0,
                    "Rationale": f"API Error: {str(e)}"
                }

def process_brand(brand_name, api_key=None):
    model = get_gemini_model(api_key)
    raw_data = gather_brand_data(brand_name)
    evaluation = evaluate_brand_with_gemini(raw_data, model)
    return evaluation
