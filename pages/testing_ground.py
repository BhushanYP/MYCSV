import streamlit as st
from Back_End import testing # Ensure this script exists in the same directory
from Back_End import process

# ---- PAGE CONFIG ----
st.set_page_config(
    page_title="Model Testing",
    page_icon="🧪",
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
st.markdown('<h1 class="title">🧪 Model Testing</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #FFFFFF;">Upload your CSV and PKL file, and we’ll test it for you!</p>', unsafe_allow_html=True)

st.markdown('<h2 class="tab_title">Model Testing</h2>', unsafe_allow_html=True)
uploaded_csv = st.file_uploader("Choose a CSV file", type=["csv"], key="csv_uploader")
uploaded_pkl = st.file_uploader("Choose a PKL file", type=["pkl"], key="pkl_uploader")

st.markdown("⚠️ **Note:** For best performance, please upload CSV files smaller than **25MB**.")

from io import StringIO
if uploaded_csv and uploaded_pkl:
    with st.spinner("Processing... ⏳"):
        processed_output = testing.process_file(uploaded_csv, uploaded_pkl)

    if isinstance(processed_output, tuple) and len(processed_output) == 2:
        csv_output, _ = processed_output  # Extract the CSV content

        # If csv_output is a string, wrap it in StringIO to create a file-like object
        if isinstance(csv_output, str):
            csv_output = StringIO(csv_output)
        
        st.success(f"✅ Successfully processed!")
        st.download_button(
            label="⬇️ Download Cleaned CSV",
            data=csv_output.getvalue(),
            file_name="Test_data.csv",
            mime="text/csv"
        )
              
    else:
        st.error(f"❌ Error: {processed_output}")
