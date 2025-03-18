from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship
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
    type = Column(String, nullable=False) # to avoid keyword change to atype
    location = Column(String, nullable=False)
    image_path = Column(String)
    # Timestamp for record updates
    updated_on = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AssetDataSource(Base):
    __tablename__ = "asset_data_source"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    asset_id = Column(String, ForeignKey("asset_data.resource_id"))
    file_path = Column(String, nullable=True)
    url = Column(String, nullable=True)
    updated_on = Column(DateTime, default=datetime.utcnow)

    # Relationship back to AssetData if you want to navigate from datasource -> asset
    asset = relationship("AssetData", backref="data_sources")
