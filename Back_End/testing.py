import pandas as pd
import io
import process
import joblib

pd.options.mode.copy_on_write = True

def process_file(file, model_path):
    """Process CSV file and make predictions using saved pipeline."""
    # Read and clean CSV
    df, error = process.read_csv_with_encoding(file)
    df = process.process_file(df)
    if error:
        return None, error

    df_clean = process.process_file(df)
    if df_clean is None:
        return None, "Error processing data"

    # Load trained model, scaler, and task type
    model_package = joblib.load(model_path)
    pipeline = model_package['pipeline']
    y_scaler = model_package.get('y_scaler', None)
    task_type = model_package.get('task_type', 'regression')  # Default to regression

    # Make predictions
    predictions = pipeline.predict(df_clean)

    # Reverse standardization if regression
    if task_type == 'regression' and y_scaler is not None:
        predictions = y_scaler.inverse_transform(predictions.reshape(-1, 1)).ravel()

    # Attach predictions to original DataFrame
    df_result = df.copy()
    df_result['Predictions'] = predictions

    # Save to CSV in memory
    csv_output = io.StringIO()
    df_result.to_csv(csv_output, index=False)
    csv_output.seek(0)

    return csv_output, None