from fastapi import APIRouter, HTTPException, Depends
import requests
from sqlalchemy.orm import Session

# Import your DB-related utilities and models
from .. import models, database

router = APIRouter()

# Change this URL if your Celery server is exposed on a different host or port.
CELERY_SERVER_URL = "http://localhost:8000"


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/submit_csv")
def submit_csv(asset_id: str, db: Session = Depends(get_db)):
    """
    Accepts an asset_id, queries the asset_data_source table for the file path,
    converts the path to the correct format, and sends it to the Celery server.
    Returns the task ID.
    """
    # 1. Query the DB for the record with this asset_id
    data_source = db.query(models.AssetDataSource).filter(models.AssetDataSource.id == asset_id).first()
    if not data_source:
        raise HTTPException(status_code=404, detail=f"No data source found for asset_id {asset_id}")
    
    # 2. Extract the file_path from the DB record
    csv_path = data_source.file_path
    print(csv_path)
    if not csv_path:
        raise HTTPException(status_code=404, detail=f"No file path set for asset_id {asset_id}")
    
    # 3. Convert backslashes to forward slashes and prepend "../" (if your Docker setup requires it)
    converted_path = csv_path.replace("\\", "/")
    adjusted_csv_path = "../" + converted_path
    
    # 4. Build the target URL for the Celery server endpoint
    celery_endpoint = f"{CELERY_SERVER_URL}/compute_accuracy"
    
    # 5. Send a POST request with the JSON payload containing the CSV path
    try:
        response = requests.post(celery_endpoint, json={"csv_path": adjusted_csv_path})
        response.raise_for_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Request to Celery server failed: {e}")
    
    # If the request is successful, Celery server should return {"task_id": "<id>"}
    return response.json()

@router.get("/result/{task_id}")
def get_result(task_id: str):
    """
    Given a task ID, polls the Celery server for the task result
    by calling /task_result/{task_id}.
    """
    celery_result_endpoint = f"{CELERY_SERVER_URL}/task_result/{task_id}"
    try:
        response = requests.get(celery_result_endpoint)
        response.raise_for_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Request to Celery server failed: {e}")
    
    return response.json()
