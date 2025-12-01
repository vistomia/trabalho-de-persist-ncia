import fastapi
import database.database
from routers import user
from routers import java
from routers import map
from routers import operator
from routers import server
from routers import server_properties
from routers import software
import models
from database import database
from sqlmodel import SQLModel, Field, create_engine, Session, select, MetaData, insert
from models.user import User
from models.map import Map
from models.operator import Operator
from models.java import Java 
from models.server_properties import ServerProperties
from models.software import Software
from models.server import Server
from datetime import datetime
import os
from dotenv import load_dotenv

app = fastapi.FastAPI()
app.include_router(user.router)
app.include_router(java.router)
app.include_router(map.router)
app.include_router(operator.router)
app.include_router(server.router)
app.include_router(server_properties.router)
app.include_router(software.router)

load_dotenv()
db = database.Database(uri=os.getenv('DATABASE_URL', 'sqlite:///data.sqlite'))
engine = db.get_engine()
metadata = MetaData()

SQLModel.metadata.create_all(engine)

metadata.create_all(engine)

@app.get("/")
async def root():
    return {"message": "hello"}