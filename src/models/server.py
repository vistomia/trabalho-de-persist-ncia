from sqlmodel import SQLModel, Field
from datetime import datetime

class Server(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str
    ip: str
    owner_id: int = Field(foreign_key="user.id")
    server_properties_id: int = Field(foreign_key="server_properties.id")
    software_id: int = Field(foreign_key="software.id")
    java_id: int = Field(foreign_key="java.id")
    created_at: datetime = Field(default_factory=datetime.now)
    # status: str
