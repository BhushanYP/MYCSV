import streamlit as st
import base64
from essentials import csv_processor  # Ensure this script exists in the same directory
import io

# ---- PAGE CONFIG ----
st.set_page_config(
    page_title="CSV Data Cleaner",
    page_icon="🧼",
    layout="wide"
)

st.sidebar.title('🚀 Navigation')
if st.sidebar.button("🏠 Home"):
    st.switch_page("MYCSV.py")
if st.sidebar.button("📊 Visualize Data"):
    st.switch_page("essentials/visualize.py")  # Link to Visualize Data
if st.sidebar.button("📜 Generate Models"):
    st.switch_page("essentials/report.py")  # Link to Generate Reports
if st.sidebar.button("🧪 Model Testing"):
    st.switch_page("essentials/testing_ground.py")
if st.sidebar.button("ℹ️ About"):
    st.switch_page("essentials/about.py")  # Assuming the "main" page is your About page


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
st.markdown('<h1 class="title">🧼 CSV Data Cleaner</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #FFFFFF;">Upload your CSV file, and we’ll clean it for you!</p>', unsafe_allow_html=True)

st.markdown('<h2 class="tab_title">CSV Cleaner</h2>', unsafe_allow_html=True)
uploaded_file_cleaner = st.file_uploader("Choose a CSV file", type=["csv"], key="cleaner")

if uploaded_file_cleaner:
    if uploaded_file_cleaner.name.endswith('.csv'):
        with st.spinner("Processing... ⏳"):
            processed_output = csv_processor.process_file(uploaded_file_cleaner)

        # Check if the processed output is a StringIO object (the cleaned data)
        if isinstance(processed_output, io.StringIO):
            st.success(f"✅ Successfully processed!")
            st.download_button(
                label="⬇️ Download Cleaned CSV",
                data=processed_output.getvalue(),  # Use .getvalue() to extract CSV data
                file_name="cleaned_data.csv",
                mime="text/csv"
            )
        else:
            st.error(f"❌ Error: {processed_output}")
    else:
        st.error("❌ Please upload a valid CSV file.")
