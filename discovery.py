import requests
from bs4 import BeautifulSoup
import random

def fetch_potential_brands():
    """
    Simulates a Discovery Engine. 
    In a fully scaled production environment, this would scrape aggregators like Olive Young, YesStyle,
    or use a database/API. For this demo pipeline, we use a robust seed list of trending and classic 
    K-Beauty brands to guarantee reliable pipeline execution without being blocked by anti-bot measures.
    """
    seed_brands = [
        "Mixsoon", "Tocobo", "Sioris", "Skin1004", "Round Lab", 
        "Purito", "I'm From", "Beauty of Joseon", "Torriden", "Anua",
        "Numbuzin", "Isntree", "Ma:nyo", "Axis-Y", "Haruharu Wonder",
        "Abib", "Celimax", "Rovectin", "Benton", "By Wishtrend",
        "Laneige", "COSRX", "Innisfree", "Etude House", "Missha", # Older/established brands to show contrast
        "Dr.G", "Jumiso", "Krave Beauty", "TirTir", "Illiyoon"
    ]
    
    # Shuffle to simulate a fresh discovery feed each time if we were pulling a subset
    random.shuffle(seed_brands)
    
    return seed_brands

if __name__ == "__main__":
    brands = fetch_potential_brands()
    print(f"Discovered {len(brands)} brands. Sample: {brands[:5]}")
