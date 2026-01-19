from beanie import Document, Link
from beanie.odm.fields import PydanticObjectId
from pydantic import Field
from pydantic import BaseModel
from datetime import datetime

class Server(Document):
    name: str = Field(..., min_length=1, max_length=100)
    owner_id: PydanticObjectId = Field(..., description="ID do proprietário (usuário)")
    server_properties_id: PydanticObjectId = Field(..., description="ID das propriedades do servidor")
    software_id: PydanticObjectId = Field(..., description="ID do software")
    java_id: PydanticObjectId = Field(..., description="ID da versão Java")
    map_id: PydanticObjectId | None = Field(None, description="ID do mapa (opcional)")
    status: str = Field(default="offline", description="Status do servidor (online, offline, maintenance)")
    ip_address: str | None = Field(None, description="Endereço IP do servidor")
    port: int = Field(default=25565, ge=1, le=65535, description="Porta do servidor")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)
    
    class Settings:
        name = "servers"
        indexes = [
            "name",
            "owner_id",
            "status",
            "created_at",
        ]
    
    model_config = {
        "arbitrary_types_allowed": True
    }

class ServerCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    owner_id: str
    server_properties_id: str
    software_id: str
    java_id: str
    map_id: str | None = None
    ip_address: str | None = None
    port: int = Field(default=25565, ge=1, le=65535)
