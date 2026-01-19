from beanie import Document, Link
from beanie.odm.fields import PydanticObjectId
from pydantic import Field
from pydantic import BaseModel

class Java(Document):
    name: str = Field(..., min_length=1, max_length=100)
    version: str = Field(..., min_length=1, max_length=50)
    link: str = Field(..., min_length=1, max_length=200)
    
    class Settings:
        name = "java_versions"
        indexes = [
            "name",
            "version",
        ]

class JavaCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, description="Nome da Versão")
    version: str = Field(..., min_length=1, max_length=20, description="Número da Versão")
    link: str = Field(..., min_length=1, max_length=200, description="Link da instalação")
