from beanie import Document, Link
from beanie.odm.fields import PydanticObjectId
from pydantic import Field
from pydantic import BaseModel
from datetime import datetime

class Operator(Document):
    server_id: PydanticObjectId = Field(..., description="ID do servidor")
    user_id: PydanticObjectId = Field(..., description="ID do usuário")
    permission_level: str = Field(..., max_length=50, description="Nível de permissão (admin, moderator, helper)")
    granted_at: datetime = Field(default_factory=datetime.utcnow)
    granted_by: PydanticObjectId = Field(None, description="ID do usuário que concedeu a permissão")
    
    class Settings:
        name = "operators"
        indexes = [
            "server_id",
            "user_id",
        ]
    
    model_config = {
        "arbitrary_types_allowed": True
    }

class OperatorCreate(BaseModel):
    server_id: str = Field(..., description="ID do servidor")
    user_id: str = Field(..., description="ID do usuário")
    permission_level: str = Field(..., max_length=50)
    granted_by: str = Field(None, description="ID do usuário que concedeu")
