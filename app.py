import streamlit as st
import pandas as pd
import plotly.express as px
import pipeline
import json

st.set_page_config(
    page_title="Glide | K-Beauty Scouting System",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom header styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.1rem;
        font-weight: 400;
        margin-bottom: 2rem;
        opacity: 0.85;
    }
    .fallback-box {
        background-color: rgba(255, 75, 75, 0.1);
        border: 1px solid rgba(255, 75, 75, 0.3);
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1.5rem;
    }
    </style>
""", unsafe_allow_type=True)

# App Sidebar
st.sidebar.image("https://img.icons8.com/ios-filled/100/ffffff/compass.png", width=60)
st.sidebar.title("Configuration")

# Toggle between Demo and Live
run_mode = st.sidebar.radio(
    "Choose Execution Mode",
    ["Demo Mode (Free, Instant)", "Live Pipeline (Scrape & Evaluate)"],
    help="Demo Mode uses pre-cached market analyses. Live Mode queries search indexes and runs Gemini dynamically."
)

api_key_input = ""
if run_mode == "Live Pipeline (Scrape & Evaluate)":
    st.sidebar.warning("Live run requires Gemini API validation credentials.")
    api_key_input = st.sidebar.text_input("Gemini API Key", type="password")

# Initialization of local session storage
if "scouted_brands" not in st.session_state:
    st.session_state.scouted_brands = list(pipeline.DEMO_DATA.values())

# Main View
st.markdown('<div class="main-header">✨ K-Beauty Scouting Suite</div>', unsafe_allow_type=True)
st.markdown('<div class="sub-header">Automated global research, enrichment, and LLM-driven market validation framework for Glide India</div>', unsafe_allow_type=True)

col1, col2 = st.columns([1, 1.3])

with col1:
    st.subheader("Brand Ingestion Dashboard")
    
    if run_mode == "Demo Mode (Free, Instant)":
        selected_demo = st.selectbox(
            "Select cached brand profile to evaluate:",
            list(pipeline.DEMO_DATA.keys())
        )
        if st.button("Simulate Pipeline Execution", use_container_width=True):
            with st.spinner("Executing pipeline phases... Scraped, Enriching, Running Gemini evaluation..."):
                st.toast("Phase 1: Emulating retail searches...")
                st.toast("Phase 2: Checking Indian saturation indexes...")
                st.toast("Phase 3: Formatting AI validation reports...")
                st.success("Analysis Complete!")
                st.session_state.active_report = pipeline.DEMO_DATA[selected_demo]
                
    else:
        brand_input = st.text_input("Enter New K-Beauty Brand Name (e.g., Laneige, Purito, Round Lab)", value="")
        if st.button("Trigger Live Discovery Pipeline", use_container_width=True):
            if not brand_input.strip():
                st.error("Please provide a valid brand name.")
            else:
                # 1. Quick Local Database Interception (Zero-Cost Cache Check)
                matched_key = next((k for k in pipeline.DEMO_DATA.keys() if k.lower() == brand_input.strip().lower()), None)
                
                if matched_key:
                    st.info(f"Loaded high-fidelity evaluation for '{brand_input}' instantly from secure local memory.")
                    st.session_state.active_report = pipeline.DEMO_DATA[matched_key]
                else:
                    with st.spinner(f"Scouting global networks for '{brand_input}'..."):
                        try:
                            # Step 1: Web Scraper & Saturation Checker
                            context, saturation = pipeline.fetch_search_context(brand_input)
                            
                            # Step 2: Call Gemini Engine (Self-Healing handles 429 Quota blocks automatically)
                            report = pipeline.run_gemini_evaluation(
                                brand_input, context, saturation, custom_key=api_key_input
                            )
                            st.session_state.active_report = report
                            
                            # Append dynamically to tracking session
                            if not any(b['brand_name'].lower() == report['brand_name'].lower() for b in st.session_state.scouted_brands):
                                st.session_state.scouted_brands.append(report)
                            
                        except Exception as e:
                            st.error(f"Unexpected Execution Error: {str(e)}")

    # Display Active Evaluation Report
    if "active_report" in st.session_state:
        r = st.session_state.active_report
        st.write("---")
        
        # Display Fallback Alert if API rate limits triggered the Zero-Cost Heuristics engine
        if r.get("is_fallback", False):
            st.markdown("""
                <div class="fallback-box">
                    <strong>⚠️ API Quota Alert Handled</strong><br>
                    Gemini Free Tier API quota exceeded or key missing. The pipeline gracefully self-healed, 
                    using <strong>Deterministic Market Heuristics</strong> to generate this scorecard.
                </div>
            """, unsafe_allow_type=True)
            
        st.subheader(f"Scorecard: {r['brand_name']}")
        
        # Display Core KPI Blocks
        m_col1, m_col2, m_col3 = st.columns(3)
        m_col1.metric("Glide Fit Score", f"{r['glide_fit_score']}/10")
        m_col2.metric("Maturity Score", f"{r['maturity_score']}/10")
        m_col3.metric("Social Traction", f"{r['social_traction_score']}/10")
        
        st.markdown(f"**🌿 Formulation Profile:** {r['formulation_profile']}")
        st.markdown(f"**💰 Estimated Pricing:** {r['average_price_usd']} ({r['price_tier']})")
        st.markdown(f"**📦 Saturation in India:** `{r['market_saturation_india']}`")
        
        st.info(f"**Strategic Alignment Justification:**\n{r['strategic_justification']}")

with col2:
    st.subheader("Interactive Market Mapping & Comparative Benchmarks")
    
    # Render Interactive Plotly Visualization for Recruiter Business Review
    df = pd.DataFrame(st.session_state.scouted_brands)
    
    # Format metrics securely
    df['glide_fit_score'] = df['glide_fit_score'].astype(float)
    df['social_traction_score'] = df['social_traction_score'].astype(float)
    
    fig = px.scatter(
        df,
        x="social_traction_score",
        y="glide_fit_score",
        size="glide_fit_score",
        color="market_saturation_india",
        hover_name="brand_name",
        labels={
            "social_traction_score": "Social Media Traction Score (1-10)",
            "glide_fit_score": "Glide Launch Alignment Score (1-10)",
            "market_saturation_india": "Saturation Level in India"
        },
        title="Glide Portfolio Fit Assessment Grid",
        template="plotly_dark",
        size_max=20
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Session Database Snapshot")
    st.dataframe(df[["brand_name", "price_tier", "market_saturation_india", "glide_fit_score"]], use_container_width=True)
    
    # Export options
    json_str = json.dumps(st.session_state.scouted_brands, indent=2)
    st.download_button(
        label="📥 Export Analysis Database as JSON",
        file_name="scouting_database_export.json",
        mime="application/json",
        data=json_str,
        use_container_width=True
    )
