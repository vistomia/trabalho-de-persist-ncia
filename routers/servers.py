from fastapi import APIRouter, HTTPException
from beanie import PydanticObjectId
from beanie.odm.fields import Link
from fastapi_pagination import Page
from fastapi_pagination.ext.beanie import apaginate
from models import java_links, minecraft_maps, operators, servers_properties, servers, softwares, users
from models.servers import Server
from datetime import datetime

router = APIRouter(
    prefix="/servers",
    tags=["Servers"],
)

@router.post("/", response_model=Server)
async def create_server(server_data: servers.ServerCreate):
    """Criar um novo servidor"""
    # Verificar se as referências existem
    owner = await users.User.get(server_data.owner_id)
    if not owner:
        raise HTTPException(status_code=400, detail="Usuário proprietário não encontrado")
    
    software = await softwares.Software.get(server_data.software_id)
    if not software:
        raise HTTPException(status_code=400, detail="Software não encontrado")
    
    java = await java_links.Java.get(server_data.java_id)
    if not java:
        raise HTTPException(status_code=400, detail="Versão Java não encontrada")
    
    server_props = await servers_properties.ServerProperties.get(server_data.server_properties_id)
    if not server_props:
        raise HTTPException(status_code=400, detail="Propriedades do servidor não encontradas")
    
    if server_data.map_id:
        map_obj = await minecraft_maps.Map.get(server_data.map_id)
        if not map_obj:
            raise HTTPException(status_code=400, detail="Mapa não encontrado")
    
    server = Server(**server_data.dict())
    await server.insert()
    return Server(**server.dict())

@router.get("/", response_model=Page[Server])
async def list_servers():
    """Listar servidores com paginação"""
    return await apaginate(Server.find())

@router.get("/{server_id}", response_model=Server)
async def get_server(server_id: PydanticObjectId):
    """Obter servidor por ID"""
    server = await Server.get(server_id)
    if not server:
        raise HTTPException(status_code=404, detail="Servidor não encontrado")
    
    return Server(**server.dict())

@router.get("/{server_id}/details", response_model=Server)
async def get_server_details(server_id: PydanticObjectId):
    """Obter servidor com detalhes completos (com dados relacionados)"""
    server = await Server.get(server_id, fetch_links=True)
    if not server:
        raise HTTPException(status_code=404, detail="Servidor não encontrado")
    
    return Server(**server.dict())

@router.put("/{server_id}", response_model=Server)
async def update_server(server_id: PydanticObjectId, server_data: servers.ServerCreate):
    """Atualizar servidor"""
    server = await Server.get(server_id)
    if not server:
        raise HTTPException(status_code=404, detail="Servidor não encontrado")
    
    # Verificar referências se estiverem sendo alteradas
    if server_data.software_id:
        software = await softwares.Software.get(server_data.software_id)
        if not software:
            raise HTTPException(status_code=400, detail="Software não encontrado")
    
    if server_data.java_id:
        java = await java_links.Java.get(server_data.java_id)
        if not java:
            raise HTTPException(status_code=400, detail="Versão Java não encontrada")
    
    if server_data.map_id:
        map_obj = await minecraft_maps.Map.get(server_data.map_id)
        if not map_obj:
            raise HTTPException(status_code=400, detail="Mapa não encontrado")
    
    # Atualizar campos
    update_data = server_data.dict(exclude_unset=True)
    await server.update({"$set": update_data})
    
    return Server(**server.dict())

@router.delete("/{server_id}")
async def delete_server(server_id: PydanticObjectId):
    """Excluir servidor"""
    server = await Server.get(server_id)
    if not server:
        raise HTTPException(status_code=404, detail="Servidor não encontrado")
    
    await server.delete()
    return {"message": "Servidor excluído com sucesso"}

@router.get("/search/by-name/{name}", response_model=Page[Server])
async def search_servers_by_name(name: str):
    """Busca case-insensitive por nome do servidor"""
    query = Server.find({"name": {"$regex": name, "$options": "i"}})
    return await apaginate(query)

@router.get("/owner/{owner_id}/servers", response_model=Page[Server])
async def get_servers_by_owner(owner_id: PydanticObjectId):
    """Listar todos os servidores de um proprietário"""
    # Verificar se o usuário existe
    owner = await users.User.get(owner_id)
    if not owner:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    query = Server.find(Server.owner_id == owner_id)
    return await apaginate(query)

@router.get("/by-year/{year}", response_model=Page[Server])
async def get_servers_by_year(year: int):
    """Listar servidores criados em um ano específico"""
    start_date = datetime(year, 1, 1)
    end_date = datetime(year + 1, 1, 1)
    
    query = Server.find({
        "created_at": {
            "$gte": start_date,
            "$lt": end_date
        }
    })
    return await apaginate(query)

@router.get("/by-date-range", response_model=Page[Server])
async def get_servers_by_date_range(
    start_date: datetime = None,
    end_date: datetime = None,
    year: int = None,
    month: int = None
):
    """Listar servidores por período - suporte a range customizado, ano específico ou mês específico"""
    query_filter = {}
    
    if year and month:
        # Filtro por ano e mês específicos
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
    elif year:
        # Filtro apenas por ano
        start_date = datetime(year, 1, 1)
        end_date = datetime(year + 1, 1, 1)
    
    if start_date and end_date:
        if start_date >= end_date:
            raise HTTPException(status_code=400, detail="Data inicial deve ser menor que a data final")
        query_filter["created_at"] = {"$gte": start_date, "$lt": end_date}
    elif start_date:
        query_filter["created_at"] = {"$gte": start_date}
    elif end_date:
        query_filter["created_at"] = {"$lt": end_date}
    
    query = Server.find(query_filter)
    return await apaginate(query)


@router.get("/status/{status}/count")
async def count_servers_by_status(status: str):
    """Contar servidores por status"""
    count = await Server.find(Server.status == status).count()
    return {"status": status, "count": count}

@router.get("/stats/summary")
async def get_servers_summary():
    """Resumo estatístico dos servidores"""
    pipeline = [
        {
            "$group": {
                "_id": "$status",
                "count": {"$sum": 1}
            }
        }
    ]
    
    status_counts = await Server.aggregate(pipeline).to_list()
    total_servers = await Server.count()
    
    return {
        "total_servers": total_servers,
        "by_status": {item["_id"]: item["count"] for item in status_counts}
    }

@router.get("/with-operators/count")
async def count_servers_with_operators():
    """Contar servidores que têm operadores"""
    pipeline = [
        {
            "$lookup": {
                "from": "operators",
                "localField": "_id",
                "foreignField": "server_id",
                "as": "operators"
            }
        },
        {
            "$match": {
                "operators": {"$ne": []}
            }
        },
        {
            "$count": "servers_with_operators"
        }
    ]
    
    result = await Server.aggregate(pipeline).to_list(1)
    count = result[0]["servers_with_operators"] if result else 0
    
    return {"servers_with_operators": count}
