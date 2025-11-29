from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .server import Server
    from .user import User

class Operator(SQLModel, table=True):
    __tablename__ = "operators"
    
    server_id: int = Field(foreign_key='servers.id', primary_key=True)
    user_id: int = Field(foreign_key='users.id', primary_key=True)
    permission_level: str = Field(max_length=50)
    granted_at: datetime = Field(default_factory=datetime.now)
    
    server: "Server" = Relationship(back_populates="operators")
    user: "User" = Relationship(back_populates="operators")
