from fastapi import FastAPI
from .routers import createAsset, AssetDataSource, addTask
from .database import engine
from . import models

app = FastAPI()

models.Base.metadata.create_all(engine)

app.include_router(createAsset.router, prefix="/asset", tags=["Asset"])
app.include_router(AssetDataSource.router, prefix="/datasource", tags=["DataSource"])
app.include_router(addTask.router, prefix="/addtask", tags=["TaskAddition"])