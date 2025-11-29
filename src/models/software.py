from sqlmodel import SQLModel, Field
from datetime import datetime

class Software(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str
    link: str
    version: str
    plugins_enabled: bool = Field(default=False)
    mods_enabled: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.now)