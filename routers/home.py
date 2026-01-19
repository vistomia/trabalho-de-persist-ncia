from fastapi import APIRouter
from models.users import User
from models.servers import Server
from models.java_links import Java
from models.softwares import Softwares
from models.minecraft_maps import MinecraftMap
from models.servers_properties import ServersProperties
from models.operators import Operator

router = APIRouter(
    prefix="",  # Prefixo para todas as rotas
    tags=["Home"],   # Tag para documentação automática
)

# Rota inicial
@router.get("/")
async def root():
    return {"message": "API ALTERNOS use /docs"}
