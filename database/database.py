from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from core.config import settings
from models.users import User
from models.servers import Server
from models.java_links import Java
from models.softwares import Software
from models.servers_properties import ServerProperties
from models.operators import Operator
from models.minecraft_maps import Map

class Database:
    client: AsyncIOMotorClient = None

db = Database()

async def connect_to_mongo():
    """Conecta ao MongoDB e inicializa o Beanie"""
    db.client = AsyncIOMotorClient(settings.mongodb_url)
    await init_beanie(
        database=db.client[settings.database_name],
        document_models=[
            User,
            Server, 
            Java,
            Software,
            ServerProperties,
            Operator,
            Map
        ]
    )

async def close_mongo_connection():
    """Fecha a conexão com o MongoDB"""
    db.client.close()
