import pandas as pd
import io  # To handle file-like objects from Streamlit

pd.options.mode.copy_on_write = True

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