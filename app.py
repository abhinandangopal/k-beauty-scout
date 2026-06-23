import streamlit as st
import pandas as pd
import plotly.express as px
import os
from pipeline import process_brand
from discovery import fetch_potential_brands

st.set_page_config(page_title="K-Beauty Scout | Glide", page_icon="✨", layout="wide")

# Custom CSS for premium feel
st.markdown("""
<style>
    .reportview-container .main .block-container{
        padding-top: 2rem;
    }
    .metric-card {
        background-color: #262730;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

st.title("✨ K-Beauty Scout for Glide")
st.markdown("Automated Discovery & Evaluation Engine for International Beauty Brands")

# --- Sidebar Configuration ---
with st.sidebar:
    st.header("⚙️ Configuration")
    mode = st.radio("Select Operation Mode", ["Demo Mode (Fast & Free)", "Live Pipeline Mode"])
    
    api_key = ""
    if mode == "Live Pipeline Mode":
        st.warning("Live Mode requires a Gemini API Key to run the evaluation engine.")
        api_key = st.text_input("Gemini API Key", type="password", help="Enter your Google Gemini API Key here.")
        if not api_key:
            st.info("Using system environment key if available.")
    
    st.markdown("---")
    st.markdown("Built for **Glide Launch Strategy**")

# --- In-Memory State for Results ---
if 'results_df' not in st.session_state:
    st.session_state.results_df = pd.DataFrame(columns=[
        "Brand Name", "Global Maturity Score", "India Saturation Level", 
        "India Exclusivity Score", "Price Positioning", "Formulation USP", 
        "Suitability Score", "Rationale"
    ])

# --- Demo Mode ---
if mode == "Demo Mode (Fast & Free)":
    st.subheader("🧪 Demo: Pre-Evaluated High-Impact Brands")
    st.markdown("Select a brand to view its pre-cached evaluation profile instantly.")
    
    demo_brands = {
        "Mixsoon": {
            "Brand Name": "Mixsoon", "Global Maturity Score": 8, "India Saturation Level": "Low",
            "India Exclusivity Score": 9, "Price Positioning": "Mid-Premium",
            "Formulation USP": "Minimalist, Fermented Ingredients (Bean Essence)",
            "Suitability Score": 88, "Rationale": "Highly viral globally, excellent formulation fit, virtually untapped in India."
        },
        "Tocobo": {
            "Brand Name": "Tocobo", "Global Maturity Score": 7, "India Saturation Level": "Very Low",
            "India Exclusivity Score": 9, "Price Positioning": "Mid-Premium",
            "Formulation USP": "Vegan, Sun Care focus (Cotton Soft Sun Stick)",
            "Suitability Score": 85, "Rationale": "Strong aesthetic appeal, suncare is a booming category in India."
        },
        "COSRX": {
            "Brand Name": "COSRX", "Global Maturity Score": 10, "India Saturation Level": "High",
            "India Exclusivity Score": 2, "Price Positioning": "Budget",
            "Formulation USP": "Clinical, Snail Mucin",
            "Suitability Score": 45, "Rationale": "Excellent global brand, but heavily saturated in the Indian market already (Maccaron, Nykaa)."
        }
    }
    
    selected_demo = st.selectbox("Select a Brand:", list(demo_brands.keys()))
    
    if st.button("Add to Shortlist Dashboard"):
        new_row = pd.DataFrame([demo_brands[selected_demo]])
        st.session_state.results_df = pd.concat([st.session_state.results_df, new_row], ignore_index=True).drop_duplicates(subset=["Brand Name"])
        st.success(f"Added {selected_demo} to Dashboard!")

# --- Live Pipeline Mode ---
else:
    st.subheader("🚀 Live Discovery & Evaluation Engine")
    st.markdown("Run the automated pipeline to fetch trending brands, scrape real-time market data, and score them using the Gemini AI Engine.")
    
    discovery_source = st.selectbox("Select Discovery Source", ["Seed List (Trending Brands)"])
    num_to_evaluate = st.slider("Number of brands to evaluate in this batch:", 1, 10, 3)
    
    if st.button("Run Pipeline"):
        if not api_key and not os.environ.get("GEMINI_API_KEY"):
            st.error("Please provide a Gemini API Key in the sidebar.")
        else:
            with st.spinner("Initializing Discovery Engine..."):
                all_brands = fetch_potential_brands()
                target_brands = all_brands[:num_to_evaluate]
            
            st.info(f"Discovered {len(all_brands)} total brands. Evaluating top {num_to_evaluate}: {', '.join(target_brands)}")
            
            progress_bar = st.progress(0)
            
            for i, brand in enumerate(target_brands):
                with st.spinner(f"[{i+1}/{num_to_evaluate}] Scraping and Evaluating '{brand}'..."):
                    try:
                        eval_data = process_brand(brand, api_key=api_key)
                        new_row = pd.DataFrame([eval_data])
                        st.session_state.results_df = pd.concat([st.session_state.results_df, new_row], ignore_index=True).drop_duplicates(subset=["Brand Name"])
                    except Exception as e:
                        st.error(f"Failed to process {brand}. Please check API Key or Rate Limits. Error: {str(e)}")
                progress_bar.progress((i + 1) / num_to_evaluate)
                
            st.success("Pipeline Execution Complete!")

# --- Dashboard & Visualizations ---
st.markdown("---")
st.header("📊 Evaluation Dashboard")

if not st.session_state.results_df.empty:
    df = st.session_state.results_df
    
    # KPIs
    col1, col2, col3 = st.columns(3)
    top_brand = df.loc[df['Suitability Score'].idxmax()]
    with col1:
        st.metric("Total Brands Evaluated", len(df))
    with col2:
        st.metric("Top Recommended Brand", top_brand['Brand Name'], f"Score: {top_brand['Suitability Score']}")
    with col3:
        avg_score = int(df['Suitability Score'].mean())
        st.metric("Average Suitability Score", avg_score)
        
    st.markdown("### Matrix: Global Maturity vs. India Exclusivity")
    st.markdown("Brands in the **Top Right** corner (High Global Maturity, High India Exclusivity) are prime targets for Glide.")
    
    fig = px.scatter(
        df, 
        x="Global Maturity Score", 
        y="India Exclusivity Score", 
        color="Price Positioning",
        size="Suitability Score",
        hover_name="Brand Name",
        hover_data=["Formulation USP"],
        text="Brand Name",
        range_x=[0, 11],
        range_y=[0, 11],
        template="plotly_dark",
        color_discrete_map={"Budget": "#3b82f6", "Mid-Premium": "#10b981", "Luxury": "#8b5cf6", "Unknown": "#64748b"}
    )
    fig.update_traces(textposition='top center')
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Detailed Scorecard")
    st.dataframe(df, use_container_width=True)
    
    # Export
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Scorecard (CSV)",
        data=csv,
        file_name='glide_kbeauty_shortlist.csv',
        mime='text/csv',
    )
else:
    st.info("No brands evaluated yet. Use the controls above to populate the dashboard.")
