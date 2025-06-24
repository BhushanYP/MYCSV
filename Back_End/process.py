import streamlit as st
import base64
import pandas as pd
import chardet

pd.options.mode.copy_on_write = True

def set_bg_image(image_file):
    try:
        with open(image_file, "rb") as img_file:
            base64_str = base64.b64encode(img_file.read()).decode()
        bg_style = f'''
        <style>
        [data-testid="stAppViewContainer"] {{
            background-image: url("data:image/png;base64,{base64_str}");
            background-size: cover;
        }}
        </style>
        '''
        st.markdown(bg_style, unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("Background image not found. Make sure 'Background.png' exists.")

def detect_date_columns(df):
    """Detect columns that are likely to contain dates."""
    date_columns = []
    for column in df.columns:
        if pd.api.types.is_numeric_dtype(df[column]) or pd.api.types.is_bool_dtype(df[column]):
            continue
        try:
            temp = pd.to_datetime(df[column], errors='coerce')
            if temp.notna().mean() >= 0.8:
                date_columns.append(column)
        except Exception:
            continue
    return date_columns

def normalize_dates(df, column_name):
    """Normalize dates to YYYY-MM-DD format."""
    try:
        df[column_name] = pd.to_datetime(df[column_name], errors='coerce')
        df = df.dropna(subset=[column_name])
        df[column_name] = df[column_name].dt.strftime('%Y-%m-%d')
        return df
    except Exception:
        return df

def process_file(df):

    if isinstance(df, str):  # If df is a string, it means an error occurred
        return df

    # Drop duplicate rows
    df = df.drop_duplicates()

    # Detect and normalize date columns
    date_columns = detect_date_columns(df)
    for date_column in date_columns:
        df = normalize_dates(df, date_column)

    # Drop columns with more than 40% missing data
    missing_percentage = df.isnull().mean()
    df = df.drop(columns=missing_percentage[missing_percentage > 0.4].index)

    # Drop rows with excessive missing values
    if (df.isnull().any(axis=1).sum() / len(df)) * 100 < 10:
        df = df.dropna()

    # Fill missing values: mode for text, median for numbers
    for column in df.columns:
        if df[column].dtype == 'object' and not df[column].dropna().empty:
            mode_value = df[column].mode()[0]
            df.loc[1:, column] = df.loc[1:, column].fillna(mode_value)
        elif pd.api.types.is_numeric_dtype(df[column]) and not df[column].dropna().empty:
            median_value = df[column].median()
            df.loc[1:, column] = df.loc[1:, column].fillna(median_value)

    return df

def detect_encoding(file):
    """Detects encoding of a file-like object or file path."""
    try:
        if isinstance(file, str):  # File path
            with open(file, "rb") as f:
                raw_data = f.read(100000)
        else:  # File-like object
            raw_data = file.read(100000)
            file.seek(0)  # Reset stream for later use

        result = chardet.detect(raw_data)
        encoding = result.get("encoding")

        if encoding is None or result.get("confidence", 0) < 0.5:
            encoding = "utf-8"  # Fallback

        return encoding, None
    except Exception as e:
        return None, f"Encoding detection failed: {e}"


def read_csv_with_encoding(file):
    """Reads a CSV with encoding detection and error handling."""
    encoding, error = detect_encoding(file)
    if error:
        return None, error

    try:
        if not isinstance(file, str):
            file.seek(0)  # Reset stream before reading again

        df = pd.read_csv(file, encoding=encoding)
        return df, None
    except Exception as e:
        return None, f"Error reading CSV: {e}"