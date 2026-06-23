import streamlit as st
import pandas as pd
import plotly.express as px
import os
import time
from pipeline import process_brand
from discovery import fetch_potential_brands
from report_generator import generate_pdf_report

st.set_page_config(page_title="K-Beauty Scout | Glide", page_icon="✨", layout="wide")

st.markdown("""
<style>
    .reportview-container .main .block-container{ padding-top: 2rem; }
</style>
""", unsafe_allow_html=True)

st.title("✨ K-Beauty Scout for Glide")
st.markdown("Live Discovery & Evaluation Engine for International Beauty Brands")

with st.sidebar:
    st.header("⚙️ Configuration")
    st.warning("Live Evaluation requires a Gemini API Key.")
    api_key = st.text_input("Gemini API Key", type="password", help="Enter your Google Gemini API Key here. If deployed on Streamlit Cloud with Secrets, leave blank.")
    if not api_key:
        api_key = os.environ.get("GEMINI_API_KEY", "")
        
if 'results_df' not in st.session_state:
    st.session_state.results_df = pd.DataFrame(columns=[
        "Brand Name", "Global Maturity Score", "India Saturation Level", 
        "India Exclusivity Score", "Price Positioning", "Formulation USP", 
        "Suitability Score", "Formulation Complexity Score", "Brand Buzz Score",
        "Pricing Competitiveness", "Target Demographic", "Hero Product",
        "Market Gap Fit", "Pricing Strategy", "Detailed Logic", "Pros", "Cons",
        "Key Ingredients", "Rationale"
    ])

st.subheader("🚀 Live Evaluation Engine")
st.markdown("Enter a specific brand to evaluate, or run a batch from the discovery engine.")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Single Brand Lookup")
    brand_input = st.text_input("Brand Name", "Laneige")
    run_single = st.button("Evaluate Single Brand")

with col2:
    st.markdown("#### Automated Batch Discovery")
    num_to_evaluate = st.slider("Brands to auto-evaluate:", 1, 10, 3)
    run_batch = st.button("Run Batch Pipeline")

if run_single:
    if not api_key:
        st.error("Please provide a Gemini API Key in the sidebar.")
    else:
        with st.spinner(f"Scraping and Evaluating '{brand_input}'..."):
            try:
                eval_data = process_brand(brand_input, api_key=api_key)
                new_row = pd.DataFrame([eval_data])
                st.session_state.results_df = pd.concat([st.session_state.results_df, new_row], ignore_index=True).drop_duplicates(subset=["Brand Name"])
                st.success(f"Evaluated {brand_input}!")
            except Exception as e:
                st.error(f"Failed to process. Error: {str(e)}")

if run_batch:
    if not api_key:
        st.error("Please provide a Gemini API Key in the sidebar.")
    else:
        with st.spinner("Initializing Discovery Engine..."):
            all_brands = fetch_potential_brands()
            target_brands = all_brands[:num_to_evaluate]
        
        st.info(f"Evaluating top {num_to_evaluate} trending brands...")
        progress_bar = st.progress(0)
        
        for i, brand in enumerate(target_brands):
            with st.spinner(f"[{i+1}/{num_to_evaluate}] Scraping and Evaluating '{brand}'..."):
                try:
                    eval_data = process_brand(brand, api_key=api_key)
                    new_row = pd.DataFrame([eval_data])
                    st.session_state.results_df = pd.concat([st.session_state.results_df, new_row], ignore_index=True).drop_duplicates(subset=["Brand Name"])
                except Exception as e:
                    st.error(f"Failed to process {brand}. Error: {str(e)}")
            
            # Smart pause to respect free tier rate limits
            if i < len(target_brands) - 1:
                with st.spinner("Pausing 15 seconds to respect free API limits..."):
                    time.sleep(15)

            progress_bar.progress((i + 1) / num_to_evaluate)
        st.success("Batch Execution Complete!")

st.markdown("---")
st.header("📊 Evaluation Dashboard")

if not st.session_state.results_df.empty:
    df = st.session_state.results_df
    
    df['Suitability Score'] = pd.to_numeric(df['Suitability Score'], errors='coerce').fillna(0)
    df['Global Maturity Score'] = pd.to_numeric(df['Global Maturity Score'], errors='coerce').fillna(0)
    df['India Exclusivity Score'] = pd.to_numeric(df['India Exclusivity Score'], errors='coerce').fillna(0)
    
    c1, c2, c3 = st.columns(3)
    top_brand = df.loc[df['Suitability Score'].idxmax()] if not df.empty and df['Suitability Score'].max() > 0 else None
    
    with c1: st.metric("Brands Evaluated", len(df))
    if top_brand is not None:
        with c2: st.metric("Top Recommended", top_brand['Brand Name'], f"Score: {int(top_brand['Suitability Score'])}")
    with c3: st.metric("Average Score", int(df['Suitability Score'].mean()))
        
    plot_df = df[df['Suitability Score'] > 0]
    if not plot_df.empty:
        try:
            fig = px.scatter(
                plot_df, x="Global Maturity Score", y="India Exclusivity Score", color="Price Positioning",
                size="Suitability Score", hover_name="Brand Name", hover_data=["Formulation USP"], text="Brand Name",
                range_x=[0, 11], range_y=[0, 11], template="plotly_dark",
                color_discrete_map={"Budget": "#3b82f6", "Mid-Premium": "#10b981", "Luxury": "#8b5cf6", "Unknown": "#64748b"}
            )
            fig.update_traces(textposition='top center')
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Could not render chart due to data formatting: {e}")
    else:
        st.warning("No valid scores to plot. (Check API Key if you see only 0 scores).")

    st.markdown("---")
    st.subheader("Deep Dive Intelligence")
    
    for idx, row in plot_df.iterrows():
        with st.expander(f"🔎 {row['Brand Name']} - Advanced Analysis (Score: {int(row['Suitability Score'])})"):
            colA, colB = st.columns([1, 2])
            with colA:
                # Radar Chart
                radar_data = pd.DataFrame(dict(
                    r=[row['Global Maturity Score'], row['India Exclusivity Score'], row.get('Formulation Complexity Score', 0), row.get('Brand Buzz Score', 0), row.get('Pricing Competitiveness', 0)],
                    theta=['Global Maturity', 'India Exclusivity', 'Formulation', 'Brand Buzz', 'Pricing Strategy']
                ))
                fig_radar = px.line_polar(radar_data, r='r', theta='theta', line_close=True, template="plotly_dark", range_r=[0, 10])
                fig_radar.update_traces(fill='toself')
                st.plotly_chart(fig_radar, use_container_width=True)
            with colB:
                st.markdown(f"**Hero Product:** {row.get('Hero Product', 'N/A')}")
                st.markdown(f"**Target Demographic:** {row.get('Target Demographic', 'N/A')}")
                st.markdown(f"**Market Gap Fit:** {row.get('Market Gap Fit', 'N/A')}")
                st.markdown(f"**Detailed Strategy:** {row.get('Detailed Logic', row.get('Rationale', ''))}")
                
                c_pro, c_con = st.columns(2)
                with c_pro:
                    st.success("**Pros**")
                    for p in row.get('Pros', []): st.write(f"- {p}")
                with c_con:
                    st.error("**Risks/Cons**")
                    for c in row.get('Cons', []): st.write(f"- {c}")

    st.markdown("---")
    st.subheader("Raw Data & Export")
    st.dataframe(df, use_container_width=True)
    
    # PDF Generator
    pdf_bytes = generate_pdf_report(df)
    st.download_button(
        label="📄 Download Full Intelligence Report (PDF)",
        data=pdf_bytes,
        file_name="glide_kbeauty_scout_report.pdf",
        mime="application/pdf",
        type="primary"
    )
else:
    st.info("No brands evaluated yet. Run an evaluation above.")
