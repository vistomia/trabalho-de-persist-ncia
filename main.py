from fastapi import FastAPI
from contextlib import asynccontextmanager
from routers import home, java_links, minecraft_maps, server_operators, servers, servers_properties, softwares, users
from database import init_db, close_db
from fastapi_pagination import add_pagination
import time
import logging
import custom_logger

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db()

# FastAPI app instance
app = FastAPI(
    title="Alternos",
    description="API para gerenciamento de servidores de Minecraft usando FastAPI e MongoDB",
    version="2.0.0",
    lifespan=lifespan)

@app.middleware("http")
async def log_requests(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    logger.info(await custom_logger.middle_logger(request, response, process_time))
    return response

# Incluindo rotas
app.include_router(home.router)
app.include_router(users.router)
app.include_router(java_links.router)
app.include_router(minecraft_maps.router)
app.include_router(server_operators.router)
app.include_router(servers.router)
app.include_router(servers_properties.router)
app.include_router(softwares.router)
add_pagination(app)
