from beanie import Document, Link
from beanie.odm.fields import PydanticObjectId
from pydantic import Field
from pydantic import BaseModel
from datetime import datetime

class MinecraftMap(Document):
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(default="", max_length=500)
    link: str = Field(..., min_length=1, max_length=200)
    size_mb: float = Field(0, ge=0, description="Tamanho do mapa em MB")
    world_type: str = Field(default="survival", description="Tipo do mundo (survival, creative, adventure)")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)
    
    class Settings:
        name = "maps"
        indexes = [
            "name",
            "world_type",
        ]

class MinecraftMapCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(default="", max_length=500)
    link: str = Field(..., min_length=1, max_length=200)
    size_mb: float = Field(0, ge=0)
    world_type: str = Field(default="survival")
