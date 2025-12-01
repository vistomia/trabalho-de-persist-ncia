from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from .operator import Operator

class Server(SQLModel, table=True):
    __tablename__ = "servers"
    
    id: int = Field(default=None, primary_key=True)
    name: str
    owner_id: int = Field(foreign_key="users.id")
    server_properties_id: int = Field(foreign_key="server_properties.id")
    software_id: int = Field(foreign_key="softwares.id")
    java_id: int = Field(foreign_key="java.id")
    created_at: datetime = Field(default_factory=datetime.now)
    #status: str
    
    # Relationship with operators - use module path to avoid circular import issues
    operators: List["Operator"] = Relationship(back_populates="server")
