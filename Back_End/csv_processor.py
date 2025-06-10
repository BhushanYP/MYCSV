import pandas as pd
import chardet  # For encoding detection
import io  # To handle file-like objects from Streamlit

pd.options.mode.copy_on_write = True

def detect_encoding(file):
    """Detects encoding of a file-like object or file path."""
    if isinstance(file, str):  # If it's a file path
        with open(file, "rb") as f:
            result = chardet.detect(f.read(100000))
    else:  # If it's an uploaded file from Streamlit
        result = chardet.detect(file.read(100000))
        file.seek(0)  # Reset file pointer after reading
    return result["encoding"]

def read_csv_with_encoding(file):
    """Reads a CSV file from a file path or an uploaded file object with auto encoding detection."""
    detected_encoding = detect_encoding(file)
    
    try:
        if isinstance(file, str):  # If it's a file path
            df = pd.read_csv(file, encoding=detected_encoding)
        else:  # If it's a file-like object from Streamlit
            df = pd.read_csv(file, encoding=detected_encoding)
    except UnicodeDecodeError:
        try:
            df = pd.read_csv(file, encoding="ISO-8859-1")
        except Exception as e:
            return f"Encoding Error: {e}"

    if df.empty or len(df.columns) == 1:
        try:
            df = pd.read_csv(file, encoding=detected_encoding, header=None)
        except Exception as e:
            return f"Final Read Error: {e}"

    return df

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

def process_file(file, columns_to_include=None, columns_to_clean=None):
    df = read_csv_with_encoding(file)
    if isinstance(df, str):  # error string
        return df

    df = df.drop_duplicates()

    # Limit DataFrame to only selected columns before cleaning
    if columns_to_include:
        df = df[[col for col in columns_to_include if col in df.columns]]

    # Determine which of the selected columns are date-like
    date_columns = detect_date_columns(df)
    clean_targets = columns_to_clean if columns_to_clean else df.columns

    for column in clean_targets:
        if column not in df.columns:
            continue

        # Normalize date columns
        if column in date_columns:
            df = normalize_dates(df, column)

        # Fill missing values
        if df[column].dtype == 'object' and not df[column].dropna().empty:
            mode_value = df[column].mode()[0]
            df.loc[1:, column] = df.loc[1:, column].fillna(mode_value)
        elif pd.api.types.is_numeric_dtype(df[column]) and not df[column].dropna().empty:
            median_value = df[column].median()
            df.loc[1:, column] = df.loc[1:, column].fillna(median_value)

    # Drop columns with >40% missing data
    missing_pct = df.isnull().mean()
    df = df.drop(columns=missing_pct[missing_pct > 0.4].index)

    # Drop rows if <10% have missing data
    if (df.isnull().any(axis=1).sum() / len(df)) * 100 < 10:
        df = df.dropna()

    # Final CSV output
    csv_output = io.StringIO()
    df.to_csv(csv_output, index=False)
    csv_output.seek(0)

    return csv_output
