from fastapi import FastAPI
from .routers import createAsset
from .database import engine
from . import models

app = FastAPI()

models.Base.metadata.create_all(engine)

app.include_router(createAsset.router)