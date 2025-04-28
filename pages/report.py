import streamlit as st
import base64
import io
from pages import csv_processor3  # Assuming the modified backend logic is in this script

# ---- PAGE CONFIG ----
st.set_page_config(
    page_title="Generate Models",
    page_icon="📜",
    layout="wide"
)

# Sidebar for navigation with emojis and boxed selection
st.sidebar.title('🚀 Navigation')
if st.sidebar.button("🏠 Home"):
    st.switch_page("MYCSV.py")
if st.sidebar.button("🧼 CSV Cleaner"):
    st.switch_page("pages/Cleaner.py")  # Link to CSV Cleaner
if st.sidebar.button("📊 Visualize Data"):
    st.switch_page("pages/visualize.py")  # Link to Visualize Data
if st.sidebar.button("🧪 Model Testing"):
    st.switch_page("pages/testing_ground.py")
if st.sidebar.button("ℹ️ About"):
    st.switch_page("pages/about.py")  # Assuming the "main" page is your About page

# ---- FUNCTION TO SET BACKGROUND IMAGE ----
def set_bg_image(image_file):
    try:
        with open(image_file, "rb") as img_file:
            base64_str = base64.b64encode(img_file.read()).decode()
        bg_style = f'''
        <style>
        [data-testid="stAppViewContainer"] {{
            background-image: url("data:image/jpg;base64,{base64_str}");
            background-size: cover;
        }}
        </style>
        '''
        st.markdown(bg_style, unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("Background image not found. Make sure 'Background.jpg' exists.")

# Set background image
set_bg_image("Background.jpg")

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
st.markdown('<h1 class="title">📜 Generate Reports</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #FFFFFF;">Upload your CSV file, and we’ll Analyze and create a model for you!</p>', unsafe_allow_html=True)

st.markdown('<h2 class="tab_title">Generate Reports</h2>', unsafe_allow_html=True)
uploaded_file_report = st.file_uploader("Choose a CSV file", type=["csv"], key="report")
    
if uploaded_file_report:
    # Inform the user that the file is being processed
    with st.spinner("Processing... ⏳"):
        # Process the file using the backend function
        processed_output = csv_processor3.process_file(uploaded_file_report)

    # Check if the output is valid and provide a downloadable model file
    if isinstance(processed_output, tuple) and len(processed_output) == 4:
        model_filename, best_model_name, best_score, best_params = processed_output
        st.success(f"✅ Successfully processed! Best model: {best_model_name} with performance score: {best_score:.4f}")

        # Offer the pickled model file for download
        with open(model_filename, 'rb') as model_file:
            st.download_button(
                label="⬇️ Download Model",
                data=model_file,
                file_name="best_model.pkl",
                mime="application/pkl"
            )
    else:
        st.error(f"❌ Error: {processed_output}")
