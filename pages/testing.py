import pandas as pd
import chardet
import io
from sklearn.preprocessing import LabelEncoder, StandardScaler
from pages import process
import joblib

pd.options.mode.copy_on_write = True

def detect_encoding(file):
    try:
        if isinstance(file, io.BytesIO):
            result = chardet.detect(file.read(100000))
            file.seek(0)  # Reset the file pointer after reading
        else:
            with open(file, "rb") as f:
                result = chardet.detect(f.read(100000))
        return result["encoding"]
    except Exception as e:
        print(f"Encoding detection error: {e}")
        return None

# Read CSV with encoding detection
def read_csv_with_encoding(file):
    detected_encoding = detect_encoding(file)
    if detected_encoding is None:
        return None, "Encoding detection failed."

    try:
        # Read the CSV file from BytesIO or file path
        df = pd.read_csv(file, encoding=detected_encoding)
        return df, None
    except Exception as e:
        return None, f"Error reading CSV: {e}"

def preprocess_data(df):
    # Initialize lists to store column names
    numeric_columns = []
    categorical_columns = []

    # Iterate over each column to check the number of unique values
    for column in df:
        unique_values = df[column].nunique()

        # If there are 5 or fewer unique values, treat it as categorical
        if unique_values <= 5:
            categorical_columns.append(column)
        elif df[column].dtype in ['int64', 'float64']:
            numeric_columns.append(column)
        else:
            df.drop(column, axis=1, inplace=True)

    # Encode categorical features with LabelEncoder
    label_encoders = {}
    for column in categorical_columns:
        le = LabelEncoder()
        df[column] = le.fit_transform(df[column])
        label_encoders[column] = le

    # Scale numerical features
    scaler = StandardScaler()
    df[numeric_columns] = scaler.fit_transform(df[numeric_columns])

    return df

def process_file(file, model):
    """Process CSV file from file path or uploaded file object."""
    df, error = read_csv_with_encoding(file)
    
    # Check if there was an error while reading the CSV
    if df is None:
        return None, error
    
    df = process.process_file(df)

    df = preprocess_data(df)

    model = joblib.load(model)
    predictions = model.predict(df)
    df = pd.DataFrame(predictions, columns=['Predictions'])
    
    # Write the processed DataFrame to a CSV in memory
    csv_output = io.StringIO()
    df.to_csv(csv_output, index=False)
    csv_output.seek(0)  # Move to the start of the StringIO buffer
    return csv_output, None
