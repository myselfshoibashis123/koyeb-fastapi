import os
import uuid
from fastapi import APIRouter, Depends, Form, UploadFile, File
from sqlalchemy.orm import Session
from .. import models, database

router = APIRouter()

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/add_asset/")
async def create_asset(
    title: str = Form(...),
    criticality: str = Form(...),
    description: str = Form(...),
    category: str = Form(...),
    type: str = Form(...),
    location: str = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    
    asset_id = str(uuid.uuid4())
    asset_folder = os.path.join("assetsInfo", asset_id)
    os.makedirs(asset_folder, exist_ok=True)

    
    image_path = os.path.join(asset_folder, image.filename)
    with open(image_path, "wb") as buffer:
        buffer.write(await image.read())

    # Save asset details in the database
    asset = models.AssetData(
        resource_id=asset_id,
        title=title,
        criticality=criticality,
        description=description,
        category=category,
        type=type,
        location=location,
        image_path=image_path  # Assuming you have an `image_path` column
    )

    db.add(asset)
    db.commit()
    db.refresh(asset)
    
    return {"message": "Asset added successfully", "asset_id": asset.resource_id, "image_path": image_path}
