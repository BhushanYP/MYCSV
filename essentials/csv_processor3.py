import pandas as pd
import numpy as np
import chardet
import io
import pickle
from sklearn.model_selection import cross_val_score, GridSearchCV
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.svm import SVC, SVR
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
import warnings
from essentials import process

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

# Detect the encoding of a file
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
        # Read the CSV file from BytesIO
        df = pd.read_csv(file, encoding=detected_encoding)
        return df, None
    except Exception as e:
        return None, f"Error reading CSV: {e}"

# Select the last column as the target column
def get_target_column(df):
    return df.columns[-1]  # Return the last column as target

# Preprocess the data: handle missing values, categorical encoding, scaling
def preprocess_data(df, target_col):
    df = process.process_file(df)
    # Separate features and target
    X = df.drop(columns=[target_col])
    y = df[target_col]

    task_type= None

    # Initialize lists to store column names
    numeric_columns = []
    categorical_columns = []

    # Iterate over each column to check the number of unique values
    for column in X.columns:
        unique_values = X[column].nunique()

        # If there are 5 or fewer unique values, treat it as categorical
        if unique_values <= 5:
            categorical_columns.append(column)

        elif X[column].dtype in ['int64', 'float64']:
            numeric_columns.append(column)

        else:
            X.drop(column, axis=1, inplace=True)

    # Encode categorical features with LabelEncoder
    label_encoders = {}
    for column in categorical_columns:
        le = LabelEncoder()
        X[column] = le.fit_transform(X[column])
        label_encoders[column] = le

    # Scale numerical features
    scaler = StandardScaler()
    X[numeric_columns] = scaler.fit_transform(X[numeric_columns])

    # Handle target column if it is categorical (for classification)
    if not np.issubdtype(y.dtype, np.number):
        # If the target is categorical, use LabelEncoder to convert to numeric
        label_encoder = LabelEncoder()
        y = label_encoder.fit_transform(y)
        task_type='classification'

    elif y.nunique() <= 5:
        task_type='classification'

    else:
        task_type='Regression'

    return X, y, task_type

# Train and evaluate models, including hyperparameter tuning with GridSearchCV
def train_and_evaluate_models(X, y, task_type):
    models = {
        'Logistic Regression': LogisticRegression(),
        'Random Forest': RandomForestClassifier() if task_type == 'classification' else RandomForestRegressor(),
        'SVM': SVC() if task_type == 'classification' else SVR(),
        'Decision Tree': DecisionTreeClassifier() if task_type == 'classification' else DecisionTreeRegressor(),
        'K-Nearest Neighbors': KNeighborsClassifier() if task_type == 'classification' else KNeighborsRegressor(),
        'Linear Regression': LinearRegression(),
    }

    best_model = None
    best_score = -np.inf if task_type == 'classification' else np.inf
    best_model_name = None
    best_params = None

    for name, model in models.items():
        print(f"Training model: {name}")
        
        param_grid = {}
        if task_type == 'classification' and name == 'Random Forest':
            param_grid = {'n_estimators': [50, 100, 200], 'max_depth': [None, 10, 20]}
        elif task_type == 'regression' and name == 'Random Forest':
            param_grid = {'n_estimators': [50, 100, 200], 'max_depth': [None, 10, 20]}
        elif task_type == 'classification' and name == 'SVM':
            param_grid = {'C': [0.1, 1, 10], 'kernel': ['linear', 'rbf']}
        elif task_type == 'regression' and name == 'SVM':
            param_grid = {'C': [0.1, 1, 10], 'epsilon': [0.01, 0.1, 1]}

        if param_grid:
            grid_search = GridSearchCV(model, param_grid, cv=5, scoring='accuracy' if task_type == 'classification' else 'neg_mean_squared_error', n_jobs=-1)
            grid_search.fit(X, y)
            model = grid_search.best_estimator_
            best_params = grid_search.best_params_

        # Use the best model from GridSearchCV to evaluate
        score = cross_val_score(model, X, y, cv=5, scoring='accuracy' if task_type == 'classification' else 'neg_mean_squared_error').mean()
        if (task_type == 'classification' and score > best_score) or (task_type == 'regression' and score < best_score):
            best_score = score
            best_model = model
            best_model_name = name

    return best_model, best_model_name, best_score, best_params

# Process file, train model, and return the pickled model
def process_file(file, task_type = None):
    # Load and preprocess data
    df, error = read_csv_with_encoding(file)
    if error:
        return error

    # Select the last column as the target
    target_col = get_target_column(df)

    # Preprocess the data (handle missing values, scaling, encoding)
    X, y, task_type = preprocess_data(df, target_col)

    # Train and evaluate different models, including hyperparameter tuning
    best_model, best_model_name, best_score, best_params = train_and_evaluate_models(X, y, task_type)

    # Save the best model to a file
    model_filename = "best_model.pkl"
    with open(model_filename, 'wb') as f:
        pickle.dump(best_model, f)

    return model_filename, best_model_name, best_score, best_params  # Return the file path for download
