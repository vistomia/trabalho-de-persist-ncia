from fastapi import APIRouter, HTTPException
from beanie import PydanticObjectId
from beanie.odm.fields import Link
from fastapi_pagination import Page
from fastapi_pagination.ext.beanie import apaginate
from models import java_links, minecraft_maps, operators, servers_properties, servers, softwares, users

router = APIRouter(
    prefix="/servers_properties",
    tags=["ServersProperties"],
)

@router.get("/", response_model=Page[servers_properties.ServersProperties])
async def read_server_properties(
    skip: int = 0,
    limit: int = 10,
    search: str | None = None
):
    if search:
        query = servers_properties.ServersProperties.find({
            "$or": [
                {"motd": {"$regex": search, "$options": "i"}},
                {"level_name": {"$regex": search, "$options": "i"}},
                {"gamemode": {"$regex": search, "$options": "i"}},
                {"difficulty": {"$regex": search, "$options": "i"}}
            ]
        })
    else:
        query = servers_properties.ServersProperties.find_all()
    
    return await apaginate(query)

@router.get("/{properties_id}", response_model=servers_properties.ServersProperties)
async def read_server_properties_by_id(properties_id: PydanticObjectId):
    properties = await servers_properties.ServersProperties.get(properties_id)
    if not properties:
        raise HTTPException(status_code=404, detail="Server properties not found")
    return properties

@router.get("/search/", response_model=Page[servers_properties.ServersProperties])
async def search_server_properties(
    gamemode: str | None = None,
    difficulty: str | None = None,
    motd: str | None = None,
    level_name: str | None = None,
    online_mode: bool | None = None,
    hardcore: bool | None = None,
    max_players: int | None = None
):
    filters = {}
    if gamemode:
        filters["gamemode"] = {"$regex": gamemode, "$options": "i"}
    if difficulty:
        filters["difficulty"] = {"$regex": difficulty, "$options": "i"}
    if motd:
        filters["motd"] = {"$regex": motd, "$options": "i"}
    if level_name:
        filters["level_name"] = {"$regex": level_name, "$options": "i"}
    if online_mode is not None:
        filters["online_mode"] = online_mode
    if hardcore is not None:
        filters["hardcore"] = hardcore
    if max_players is not None:
        filters["max_players"] = max_players
    
    query = servers_properties.ServersProperties.find(filters)
    return await apaginate(query)

@router.get("/count/")
async def count_server_properties():
    count = await servers_properties.ServersProperties.count()
    return {"count": count}

@router.get("/ordered/", response_model=Page[servers_properties.ServersProperties])
async def read_server_properties_ordered(
    order_by: str = "id",
    desc: bool = False
):
    sort_order = -1 if desc else 1
    query = servers_properties.ServersProperties.find_all().sort([(order_by, sort_order)])
    return await apaginate(query)

@router.post("/", response_model=servers_properties.ServersProperties)
async def create_server_properties(properties: servers_properties.ServersProperties):
    await properties.insert()
    return properties

@router.patch("/{properties_id}", response_model=servers_properties.ServersProperties)
async def update_server_properties(
    properties_id: PydanticObjectId,
    properties_update: dict
):
    properties = await servers_properties.ServersProperties.get(properties_id)
    if not properties:
        raise HTTPException(status_code=404, detail="Server properties not found")
    
    await properties.update({"$set": properties_update})
    await properties.save()
    return properties

@router.delete("/{properties_id}")
async def delete_server_properties(properties_id: PydanticObjectId):
    properties = await servers_properties.ServersProperties.get(properties_id)
    if not properties:
        raise HTTPException(status_code=404, detail="Server properties not found")
    
    await properties.delete()
    return {"message": "Server properties deleted successfully"}

@router.get("/aggregations/by-gamemode")
async def properties_by_gamemode():
    """Distribuição de propriedades por modo de jogo"""
    pipeline = [
        {
            "$group": {
                "_id": "$gamemode",
                "count": {"$sum": 1},
                "avg_max_players": {"$avg": "$max_players"},
                "properties": {
                    "$push": {
                        "level_name": "$level_name",
                        "difficulty": "$difficulty",
                        "max_players": "$max_players"
                    }
                }
            }
        },
        {
            "$sort": {"count": -1}
        }
    ]
    
    result = await servers_properties.ServersProperties.aggregate(pipeline).to_list()
    return {"properties_by_gamemode": result}

@router.get("/aggregations/by-difficulty")
async def properties_by_difficulty():
    """Distribuição por dificuldade"""
    pipeline = [
        {
            "$group": {
                "_id": "$difficulty",
                "count": {"$sum": 1},
                "avg_max_players": {"$avg": "$max_players"},
                "hardcore_count": {
                    "$sum": {"$cond": [{"$eq": ["$hardcore", True]}, 1, 0]}
                }
            }
        },
        {
            "$sort": {"count": -1}
        }
    ]
    
    result = await servers_properties.ServersProperties.aggregate(pipeline).to_list()
    return {"properties_by_difficulty": result}

@router.get("/aggregations/player-capacity-stats")
async def player_capacity_stats():
    """Estatísticas de capacidade de jogadores"""
    pipeline = [
        {
            "$group": {
                "_id": None,
                "avg_capacity": {"$avg": "$max_players"},
                "min_capacity": {"$min": "$max_players"},
                "max_capacity": {"$max": "$max_players"},
                "total_capacity": {"$sum": "$max_players"},
                "properties_count": {"$sum": 1}
            }
        }
    ]
    
    result = await servers_properties.ServersProperties.aggregate(pipeline).to_list(1)
    stats = result[0] if result else {}
    
    # Distribuição por ranges de capacidade
    capacity_ranges = await servers_properties.ServersProperties.aggregate([
        {
            "$bucket": {
                "groupBy": "$max_players",
                "boundaries": [0, 10, 20, 50, 100, 500, 1000],
                "default": "1000+",
                "output": {
                    "count": {"$sum": 1},
                    "avg_capacity": {"$avg": "$max_players"}
                }
            }
        }
    ]).to_list()
    
    return {
        "overall_stats": stats,
        "capacity_distribution": capacity_ranges
    }

@router.get("/aggregations/usage-by-servers")
async def properties_usage_by_servers():
    """Propriedades utilizadas por servidores"""
    from models.servers import Server
    
    pipeline = [
        {
            "$lookup": {
                "from": "servers",
                "localField": "_id",
                "foreignField": "server_properties_id",
                "as": "servers_using"
            }
        },
        {
            "$project": {
                "level_name": 1,
                "gamemode": 1,
                "difficulty": 1,
                "max_players": 1,
                "motd": 1,
                "servers_count": {"$size": "$servers_using"},
                "servers": {
                    "$map": {
                        "input": "$servers_using",
                        "as": "server",
                        "in": {
                            "name": "$$server.name",
                            "status": "$$server.status"
                        }
                    }
                }
            }
        },
        {
            "$sort": {"servers_count": -1}
        }
    ]
    
    result = await servers_properties.ServersProperties.aggregate(pipeline).to_list()
    return {"properties_usage": result}

@router.get("/filter/by-max-players")
async def filter_by_max_players(min_players: int = 0, max_players: int = 1000):
    """Filtrar propriedades por capacidade de jogadores"""
    query = servers_properties.ServersProperties.find({
        "max_players": {"$gte": min_players, "$lte": max_players}
    })
    return await apaginate(query)

@router.get("/filter/hardcore-servers", response_model=Page[servers_properties.ServersProperties])
async def get_hardcore_properties():
    """Propriedades de servidores hardcore"""
    query = servers_properties.ServersProperties.find({"hardcore": True})
    return await apaginate(query)

@router.get("/stats/advanced-summary")
async def get_advanced_properties_summary():
    """Resumo avançado das propriedades de servidor"""
    total = await servers_properties.ServersProperties.count()
    
    # Estatísticas por modo de jogo
    by_gamemode = await servers_properties.ServersProperties.aggregate([
        {"$group": {"_id": "$gamemode", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]).to_list()
    
    # Estatísticas por dificuldade
    by_difficulty = await servers_properties.ServersProperties.aggregate([
        {"$group": {"_id": "$difficulty", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]).to_list()
    
    # Contadores booleanos
    hardcore_count = await servers_properties.ServersProperties.find({"hardcore": True}).count()
    online_mode_count = await servers_properties.ServersProperties.find({"online_mode": True}).count()
    flight_enabled = await servers_properties.ServersProperties.find({"allow_flight": True}).count()
    
    return {
        "total_properties": total,
        "by_gamemode": {item["_id"]: item["count"] for item in by_gamemode},
        "by_difficulty": {item["_id"]: item["count"] for item in by_difficulty},
        "hardcore_servers": hardcore_count,
        "online_mode_enabled": online_mode_count,
        "flight_enabled": flight_enabled,
        "offline_mode_enabled": total - online_mode_count
    }
