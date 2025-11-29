import fastapi
import database.database
from routers import user
import models
from database import database
from sqlmodel import SQLModel, Field, create_engine, Session, select, MetaData, insert
from models.user import User

app = fastapi.FastAPI()
app.include_router(user.router)

db = database.Database(uri='sqlite:///data.sqlite')
engine = db.get_engine()
metadata = MetaData()

# Create tables
SQLModel.metadata.create_all(engine)

# Use User model instead of users_table
metadata.create_all(engine)

with Session(engine) as session:
    # Check if the table has any data
    statement = select(User).limit(1)
    result = session.exec(statement).first()
    
    if result is None:
        print("Table is empty. Inserting sample data...")
        # Create User instances
        users_to_add = [
            User(username="alice", email="alice@example.com", password="password123"),
            User(username="bob", email="bob@example.com", password="password123"),
            User(username="carol", email="carol@example.com", password="password123")
        ]
        
        # Add users to session and commit
        for user in users_to_add:
            session.add(user)
        session.commit()
    
    # Print all data
    statement = select(User)
    results = session.exec(statement)
    for user in results:
        print(f"ID: {user.id}, Username: {user.username}, Email: {user.email}")

@app.get("/")
async def root():
    return {"message": "hello"}