from sqlmodel import SQLModel, Field
from datetime import datetime

class Java(SQLModel, table=True):
    __tablename__ = "java"
    id: int = Field(default=None, primary_key=True)
    name: str
    link: str
    created_at: datetime = Field(default_factory=datetime.now)

class JavaResponse(SQLModel):
    id: int | None
    name: str
    link: str
    created_at: datetime