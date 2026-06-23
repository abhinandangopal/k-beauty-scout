# ✨ K-Beauty Scout for Glide

An automated intelligence pipeline and Streamlit dashboard designed to discover, evaluate, and shortlist international K-Beauty brands for launch in the Indian market.

## Architecture

The system consists of three core modules:
1. **Discovery Engine (`discovery.py`)**: Automatically fetches a curated pool of high-potential K-Beauty brands.
2. **Scraping & AI Pipeline (`pipeline.py`)**:
    - **Scraping**: Queries global hubs (YesStyle, SokoGlam) to assess global maturity, and Indian platforms (Nykaa, Tira) to check market saturation.
    - **Evaluation**: Passes unstructured data to the Google Gemini AI to strictly score brands based on Formulation, Price Positioning, and Exclusivity.
3. **Interactive UI (`app.py`)**: A Streamlit dashboard with "Demo Mode" for instant recruiter demonstrations and "Live Mode" for real-time AI evaluation, complete with Plotly data visualizations.

## Quick Start (Local)

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Set up API Key (Optional but recommended for Live Mode):**
   ```bash
   # Windows
   set GEMINI_API_KEY=your_api_key_here
   # Mac/Linux
   export GEMINI_API_KEY=your_api_key_here
   ```
   *(Note: You can also enter the API key directly within the Streamlit UI).*
3. **Run the App:**
   ```bash
   streamlit run app.py
   ```

## Deployment (Streamlit Community Cloud)

To share this app online:
1. Push this repository to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io/) and connect your GitHub account.
3. Select this repository and `app.py` as the main file.
4. Add your `GEMINI_API_KEY` in the Streamlit Cloud "Advanced Settings > Secrets" if you want Live Mode to work seamlessly.
5. Click **Deploy**. You will receive a public URL to share!
