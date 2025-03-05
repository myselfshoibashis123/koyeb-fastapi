import os
from datetime import datetime
from fastapi import APIRouter, Depends, Form, File, UploadFile
from sqlalchemy.orm import Session

from .. import models, database

router = APIRouter()

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/add_datasource/")
async def add_datasource(
    asset_id: str = Form(...),
    data_source_type: str = Form(...),  # file" or "url"
    file: UploadFile = File(None),
    url: str = Form(None),
    db: Session = Depends(get_db)
):
    """
    Adds a datasource for an existing asset. 
    - If data_source_type = 'file', user uploads a file.
    - If data_source_type = 'url', user provides a URL.
    """

    # 1. Verify if asset exists
    asset = db.query(models.AssetData).filter_by(resource_id=asset_id).first()
    if not asset:
        return {"error": f"No asset found with asset_id '{asset_id}'"}

    # 2. Decide file vs. url
    file_path = None
    if data_source_type == "file":
        if not file:
            return {"error": "No file was uploaded, but data_source_type='file'."}

        # 2a. Ensure the asset folder exists
        asset_folder = os.path.join("assetsInfo", asset_id)
        os.makedirs(asset_folder, exist_ok=True)

        # 2b. Save the file
        saved_file_path = os.path.join(asset_folder, file.filename)
        with open(saved_file_path, "wb") as buffer:
            buffer.write(await file.read())

        # We store the file path, url remains None
        file_path = saved_file_path
        url = None

    elif data_source_type == "url":
        if not url:
            return {"error": "URL is required when data_source_type='url'."}
        # We store the URL, file_path remains None
        file_path = None

    else:
        return {"error": "Invalid data_source_type. Choose either 'file' or 'url'."}

    # 3. Create a new AssetDataSource record
    data_source = models.AssetDataSource(
        asset_id=asset_id,
        file_path=file_path,
        url=url,
        updated_on=datetime.utcnow()
    )
    db.add(data_source)
    db.commit()
    db.refresh(data_source)

    return {
        "message": "Data source added successfully",
        "data_source_id": data_source.id,
        "asset_id": data_source.asset_id,
        "file_path": data_source.file_path,
        "url": data_source.url,
        "updated_on": data_source.updated_on.isoformat()
    }
