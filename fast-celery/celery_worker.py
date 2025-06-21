from celery import Celery

celery_app = Celery('tasks', broker='redis://redis/0', backend='redis://redis/0')

@celery_app.task()
def add(a, b):
    for i in range(a, b):
        print(i)
    return {"number": a + b}

@celery_app.task()
def compute_accuracy(csv_path: str):
    import numpy as np
    import pandas as pd
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score
    # Patch numpy for FLAML compatibility if needed
    np.NaN = np.nan
    np.Inf = np.inf

    # Import FLAML's AutoML
    
    from flaml import automl as flaml_automl

    model = flaml_automl.AutoML()


    # Load the CSV file. Adjust the CSV reading logic if needed.
    df = pd.read_csv(csv_path)
    
    # Assume that the last column is the target variable.
    X = df.iloc[:, :-1]
    y = df.iloc[:, -1]

    # Split the dataset into training and testing sets.
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Create an AutoML instance.
    # automl = automl.AutoML()

    # Define the settings for the AutoML run.
    settings = {
        "time_budget": 60,          # Run AutoML for 60 seconds.
        "metric": "accuracy",       # Optimize for accuracy.
        "task": "classification",   # Classification task.
        "estimator_list": [
            "lgbm", 
            "rf", 
            # "xgboost", 
            "extra_tree", 
            # "xgb_limitdepth", 
            "lrl1"
        ],
        "log_file_name": "flaml.log"  # Optional: specify a log file.
    }

    # Fit AutoML on the training data.
    model.fit(X_train=X_train, y_train=y_train, **settings)

    # Predict on the test set and compute accuracy.
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    # Retrieve the best hyperparameter configuration.
    best_config = model.best_config
    best_model = model.best_estimator

    return {"accuracy": accuracy, "best_config": best_config, "best_model": best_model}
