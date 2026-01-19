from dotenv import load_dotenv
from pymongo import AsyncMongoClient
from beanie import init_beanie
import os
import logging

from models import java_links, minecraft_maps, operators, servers_properties, servers, softwares, users

load_dotenv()
DATABASE_URL = os.getenv("MONGODB_URL")
DBNAME = os.getenv("DATABASE_NAME")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

_client: AsyncMongoClient | None = None

async def init_db():
    global _client
    _client = AsyncMongoClient(DATABASE_URL)
    logger.info(f"Using DATABASE_URL: {DATABASE_URL}")
    db = _client[DBNAME]

    await init_beanie(
        database=db,
        document_models=[
            java_links.Java, 
            minecraft_maps.MinecraftMap,
            operators.Operator,
            servers_properties.ServersProperties,
            servers.Server,
            softwares.Softwares,
            users.User
        ],
    )

async def close_db():
    global _client
    if _client is not None:
        _client.close()
        logger.info(f"Closed DATABASE_URL: {DATABASE_URL}")
        _client = None
