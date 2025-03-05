from sqlalchemy import Column, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class AssetData(Base):
    __tablename__ = "asset_data"

    # Unique Resource ID (Primary Key)
    resource_id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    
    # Required Fields
    title = Column(String, nullable=False)
    criticality = Column(String, nullable=False)
    description = Column(String, nullable=False)
    category = Column(String, nullable=False)
    type = Column(String, nullable=False)
    location = Column(String, nullable=False)
    image_path = Column(String)
    # Timestamp for record updates
    updated_on = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
