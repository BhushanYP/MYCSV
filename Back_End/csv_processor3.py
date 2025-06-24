import numpy as np
from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import LabelEncoder, StandardScaler, OneHotEncoder
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.svm import SVC, SVR
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error
import warnings
import sys
import os
import joblib

sys.path.append(os.path.dirname(__file__))
from Back_End import process

warnings.filterwarnings('ignore')

def get_target_column(df):
    return df.columns[-1]

def preprocess_data(df, target_col):
    df = process.process_file(df)

    X = df.drop(columns=[target_col])
    y = df[target_col]

    task_type = None
    y_scaler = None
    y_original = y.copy()

    # Auto-infer task type
    if not np.issubdtype(y.dtype, np.number):
        task_type = 'classification'
        y = LabelEncoder().fit_transform(y)
    elif y.nunique() <= 5:
        task_type = 'classification'
    else:
        task_type = 'regression'
        y_scaler = StandardScaler()
        y = y_scaler.fit_transform(y.values.reshape(-1, 1)).ravel()

    # Identify column types
    numeric_cols = X.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = X.select_dtypes(include=['object', 'bool']).columns.tolist()

    # Build transformer
    transformers = []
    if numeric_cols:
        transformers.append(('num', StandardScaler(), numeric_cols))
    if categorical_cols:
        transformers.append(('cat', OneHotEncoder(handle_unknown='ignore'), categorical_cols))

    preprocessor = ColumnTransformer(transformers)
    X_processed = preprocessor.fit_transform(X)

    return X_processed, y, task_type, y_scaler, preprocessor, y_original

def train_and_evaluate_models(X, y, task_type, y_original=None, y_scaler=None):
    models = {
        'Logistic Regression': LogisticRegression() if task_type == 'classification' else None,
        'Random Forest': RandomForestClassifier() if task_type == 'classification' else RandomForestRegressor(),
        'SVM': SVC() if task_type == 'classification' else SVR(),
        'Decision Tree': DecisionTreeClassifier() if task_type == 'classification' else DecisionTreeRegressor(),
        'K-Nearest Neighbors': KNeighborsClassifier() if task_type == 'classification' else KNeighborsRegressor(),
        'Linear Regression': LinearRegression() if task_type == 'regression' else None
    }

    param_grids = {
        'Random Forest': {'n_estimators': [50, 100], 'max_depth': [None, 10]},
        'SVM': {'C': [0.1, 1, 10], 'kernel': ['linear', 'rbf']} if task_type == 'classification' else {'C': [0.1, 1, 10], 'epsilon': [0.01, 0.1, 1]},
        'Decision Tree': {'max_depth': [None, 5, 10]},
        'K-Nearest Neighbors': {'n_neighbors': [3, 5, 7]}
    }

    best_model = None
    best_score = -np.inf
    best_model_name = None
    best_params = None

    for name, model in models.items():
        if model is None:
            continue

        print(f"Training model: {name}")

        grid = GridSearchCV(model, param_grids.get(name, {}), cv=5, scoring='neg_root_mean_squared_error' if task_type == 'regression' else 'accuracy', n_jobs=-1)
        grid.fit(X, y)
        model = grid.best_estimator_

        if task_type == 'classification':
            score = grid.best_score_
        else:
            predictions = model.predict(X)
            if y_scaler is not None:
                y_real = y_scaler.inverse_transform(y.reshape(-1, 1))
                pred_real = y_scaler.inverse_transform(predictions.reshape(-1, 1))
                rmse = mean_squared_error(y_real, pred_real, squared=False)
                std_real = np.std(y_real)
                score = max(0, 1 - (rmse / std_real))  # Regression accuracy
            else:
                score = 0

        if score > best_score:
            best_score = score
            best_model = model
            best_model_name = name
            best_params = grid.best_params_ if param_grids.get(name) else None

    return best_model, best_model_name, best_score, best_params

def process_file(file, task_type=None):
    df, error = process.read_csv_with_encoding(file)
    if error:
        return error

    target_col = get_target_column(df)
    X, y, task_type, y_scaler, preprocessor, y_original = preprocess_data(df, target_col)
    best_model, best_model_name, best_score, best_params = train_and_evaluate_models(X, y, task_type, y_original, y_scaler)

    pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('model', best_model)
    ])

    model_filename = "best_model.pkl"
    model_package = {
        'pipeline': pipeline,
        'y_scaler': y_scaler,
        'task_type': task_type
    }

    joblib.dump(model_package, model_filename)

    return model_filename, best_model_name, best_score, best_params