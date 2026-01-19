from beanie import Document, Link
from beanie.odm.fields import PydanticObjectId
from pydantic import Field
from pydantic import BaseModel
from datetime import datetime

class Softwares(Document):
    name: str = Field(..., min_length=1, max_length=100)
    version: str = Field(..., description="Versão do software (ex: 1.20.4, 1.19.2)")
    link: str = Field(..., description="Link para download")
    plugins_enabled: bool = Field(default=False, description="Suporte a plugins")
    mods_enabled: bool = Field(default=False, description="Suporte a mods")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)
    
    class Settings:
        name = "softwares"
        indexes = [
            "name",
            "version",
            "plugins_enabled",
            "mods_enabled"
        ]
