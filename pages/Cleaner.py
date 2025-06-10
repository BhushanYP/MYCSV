import streamlit as st
import base64
from Back_End import csv_processor  # Ensure this script exists in the same directory
import io

# ---- PAGE CONFIG ----
st.set_page_config(
    page_title="CSV Data Cleaner",
    page_icon="🧼",
    layout="wide"
)

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
    # Read CSV without processing to show column selection
        temp_df = csv_processor.read_csv_with_encoding(uploaded_file_cleaner)

        if isinstance(temp_df, str):
            st.error(f"❌ Error: {temp_df}")
        else:
            with st.form("column_selection_form"):
                st.write("### Select Columns to Include in Export and Apply Cleaning")
                selected_columns = st.multiselect(
                    "📤 Choose columns to export (they will also be cleaned):",
                    temp_df.columns.tolist(),
                    default=temp_df.columns.tolist()
                )
                submitted = st.form_submit_button("✅ Clean and Export")

            if submitted:
                with st.spinner("Processing... ⏳"):
                    processed_output = csv_processor.process_file(
                        uploaded_file_cleaner,
                        columns_to_include=selected_columns,
                        columns_to_clean=selected_columns
                    )

                if isinstance(processed_output, io.StringIO):
                    st.success(f"✅ Successfully processed!")
                    st.download_button(
                        label="⬇️ Download Cleaned CSV",
                        data=processed_output.getvalue(),
                        file_name="cleaned_data.csv",
                        mime="text/csv"
                    )
                else:
                    st.error(f"❌ Error: {processed_output}")
