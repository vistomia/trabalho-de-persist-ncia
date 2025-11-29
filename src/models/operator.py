from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
class Operator(SQLModel, table=True):
    server_id: int = Field(foreign_key='servers.id', primary_key=True)
    user_id: int = Field(foreign_key='users.id', primary_key=True)
    permission_level: str = Field(max_length=50)
    granted_at: datetime = Field(default_factory=datetime.now)
    
    server: "Server" | None = Relationship(back_populates="operators")
    user: "User" | None = Relationship(back_populates="operators")
