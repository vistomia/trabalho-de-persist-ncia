from sqlmodel import SQLModel, Field
from datetime import datetime

class Software(SQLModel, table=True):
    __tablename__ = "softwares"
    id: int | None = Field(default=None, primary_key=True)
    name: str
    link: str
    version: str
    plugins_enabled: bool = Field(default=False)
    mods_enabled: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.now)