import streamlit as st
import io
from Back_End import csv_processor2 # Ensure this script exists in the same directory
from Back_End import process

# ---- PAGE CONFIG ----
st.set_page_config(
    page_title="Visualize Data",
    page_icon="📊",
    layout="wide", initial_sidebar_state="collapsed"
)

# Set background image
process.set_bg_image("Background.png")

# ---- CUSTOM STYLES ----
custom_css = """
<style>
/* Center title with shadow */
.title {
    text-align: center;
    font-size: 3rem;
    font-weight: bold;
    margin-bottom: 10px;
    color: #FFFFFF;
}

/* Center tab title */
.tab_title {
    text-align: center;
    font-weight: bold;
}

/* Upload section styling */
.upload-box {
    background: rgba(255, 255, 255, 0.9);
    padding: 20px;
    border-radius: 12px;
    text-align: center;
    box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
}

/* Styled button */
[data-testid="stDownloadButton"] button {
    background: #4caf50 !important;
    color: white !important;
    font-size: 18px !important;
    border-radius: 12px !important;
    padding: 12px 24px !important;
    transition: 0.3s;
}
[data-testid="stDownloadButton"] button:hover {
    background: #388e3c !important;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ---- TITLE ----
st.markdown('<h1 class="title">📊 Visualize Data</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #FFFFFF;">Upload your CSV file, and we’ll Analyze and Visualized it for you!</p>', unsafe_allow_html=True)

st.markdown('<h2 class="tab_title">Visualize Data</h2>', unsafe_allow_html=True)
uploaded_file_analizer = st.file_uploader("Choose a CSV file", type=["csv"], key="cleaner")

st.markdown("⚠️ **Note:** For best performance, please upload CSV files smaller than **25MB**.")

if uploaded_file_analizer:
    with st.spinner("Processing... ⏳"):
        processed_output = csv_processor2.process_file(uploaded_file_analizer)

    if isinstance(processed_output, io.BytesIO):
            st.success("✅ Successfully processed!")
            st.download_button(
                label="⬇️ Download PDF",
                data=processed_output.getvalue(),
                file_name="simple_pdf.pdf",
                mime="application/pdf"
            )
    else:
        st.error(f"❌ Error: {processed_output}")