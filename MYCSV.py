import streamlit as st
import os
import base64

def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

def main():
    st.set_page_config(page_title='MYCSV', layout='wide')

    # Sidebar for navigation with emojis and boxed selection
    st.sidebar.title('🚀 Navigation')
    if st.sidebar.button("🧼 CSV Cleaner"):
        st.switch_page("essentials/Cleaner.py")  # Link to CSV Cleaner
    if st.sidebar.button("📊 Visualize Data"):
        st.switch_page("essentials/visualize.py")  # Link to Visualize Data
    if st.sidebar.button("📜 Generate Models"):
        st.switch_page("essentials/report.py")  # Link to Generate Reports
    if st.sidebar.button("🧪 Model Testing"):
        st.switch_page("essentials/testing_ground.py")
    if st.sidebar.button("ℹ️ About"):
        st.switch_page("essentials/about.py")  # Assuming the "main" page is your About page

    # About Page
    st.markdown("<h1 style='text-align: center;'>📊 MYCSV - Your Data Processing Hub 🚀</h1>", unsafe_allow_html=True)

    st.markdown("""
    <div class='center-text'>
        <p>Welcome to MYCSV, an advanced tool for CSV data processing, visualization, and reporting!</p>
    </div>
    """, unsafe_allow_html=True)

    # Layout for Data Cleaning, Data Visualization, and Prediction Models
    col1, col2 = st.columns([2, 1])
    with col2:
        st.markdown("### CSV Cleaner")
        img_base64 = get_base64_image(os.path.join("images", "upload.png"))
        if st.button("Go to CSV Cleaner", key="csv_cleaner"):
            st.switch_page("essentials/Cleaner.py")
        st.markdown(f"""
            <div class='image-container'>
                <img src='data:image/png;base64,{img_base64}' style='width:100%;' />
            </div>
        """, unsafe_allow_html=True)

    with col1:
        st.markdown("""
            <div class="section-description" style="text-align: left; padding-right: 15px; margin-top: 30px;">
                <br><br><strong>Data Cleaning</strong><br><br>
                Data cleaning is an essential step in any data analysis process. It involves handling missing values, correcting inconsistencies, and transforming raw data into a structured format. 
                This process ensures that your data is accurate, complete, and ready for analysis or further processing. In this section, you can upload your CSV files and clean them using various tools.
            </div>
        """, unsafe_allow_html=True)

    col3, col4 = st.columns([1, 2])
    with col3:
        st.markdown("### Visualize Data")
        img_base64 = get_base64_image(os.path.join("images", "visualize.png"))
        if st.button("Go to Visualize Data", key="visualize_data"):
            st.switch_page("essentials/visualize.py")
        st.markdown(f"""
            <div class='image-container'>
                <img src='data:image/png;base64,{img_base64}' style='width:100%;' />
            </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
            <div class="section-description" style="text-align: left; padding-left: 15px; margin-top: 30px;">
                <br><br><strong>Data Visualization</strong><br><br>
                Data visualization is key to understanding trends and patterns within your data. By using charts, graphs, and other visual elements, you can communicate your findings in a way that is easily understood. 
                This section provides tools to create various visualizations to help you analyze the relationships, distributions, and trends within your data.
            </div>
        """, unsafe_allow_html=True)

    col5, col6 = st.columns([2, 1])
    with col6:
        st.markdown("### Generate Models")
        img_base64 = get_base64_image(os.path.join("images", "report.png"))
        if st.button("Go to Generate Reports", key="generate_reports"):
            st.switch_page("essentials/reports.py")
        st.markdown(f"""
            <div class='image-container'>
                <img src='data:image/png;base64,{img_base64}' style='width:100%;' />
            </div>
        """, unsafe_allow_html=True)

    with col5:
        st.markdown("""
            <div class="section-description" style="text-align: left; padding-right: 15px; margin-top: 30px;">
                <br><br><strong>Prediction Models</strong><br><br>
                In this section, you can apply machine learning models to predict trends or outcomes based on historical data. By utilizing algorithms like regression, classification, and clustering, 
                you can generate predictions that help inform future decisions. The system also allows you to evaluate model performance and make improvements to your predictions over time.
            </div>
        """, unsafe_allow_html=True)

    col7, col8 = st.columns([1, 2])
    with col7:
        st.markdown("### Testing Models")
        img_base64 = get_base64_image(os.path.join("images", "test.png"))
        if st.button("Go to Model Testing", key="Model_Testing"):
            st.switch_page("essentials/testing_ground.py")
        st.markdown(f"""
            <div class='image-container'>
                <img src='data:image/png;base64,{img_base64}' style='width:80%;' />
            </div>
        """, unsafe_allow_html=True)

    with col8:
        st.markdown("""
            <div class="section-description" style="text-align: left; padding-right: 15px; margin-top: 30px;">
                <br><br><strong>Testing Models</strong><br><br>
                Testing Models involves evaluating how well a machine learning or statistical model performs on unseen data. It helps determine the model’s accuracy, reliability, and generalization ability. This process typically includes using a separate test dataset, applying performance metrics (like accuracy, precision, recall, or RMSE), and identifying potential issues like overfitting or underfitting. Testing is a crucial step to ensure the model can make accurate predictions in real-world scenarios.
            </div>
        """, unsafe_allow_html=True)

if __name__ == '__main__':
    main()
