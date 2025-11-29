from sqlmodel import SQLModel, Field
from datetime import datetime

class Map(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    description: str = Field(default="")
    link: str
    created_at: datetime = Field(default_factory=datetime.now)