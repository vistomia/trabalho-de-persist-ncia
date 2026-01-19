from fastapi import APIRouter, HTTPException
from beanie import PydanticObjectId
from beanie.odm.fields import Link
from fastapi_pagination import Page
from fastapi_pagination.ext.beanie import apaginate
from models.minecraft_maps import MinecraftMap

router = APIRouter(
    prefix="/minecraft_maps",
    tags=["Maps"],
)

@router.get("/", response_model=Page[MinecraftMap])
async def read_maps():
    return await apaginate(MinecraftMap)

@router.get("/{map_id}", response_model=MinecraftMap)
async def read_map_by_id(map_id: PydanticObjectId):
    map_entry = await MinecraftMap.get(map_id)
    if not map_entry:
        raise HTTPException(status_code=404, detail="Map not found")
    return map_entry

@router.post("/", response_model=MinecraftMap)
async def create_map(map_data: MinecraftMap):
    await map_data.insert()
    return map_data

@router.put("/{map_id}", response_model=MinecraftMap)
async def update_map(map_id: PydanticObjectId, map_update: dict):
    map_entry = await MinecraftMap.get(map_id)
    if not map_entry:
        raise HTTPException(status_code=404, detail="Map not found")
    
    await map_entry.update({"$set": map_update})
    return map_entry

@router.delete("/{map_id}")
async def delete_map(map_id: PydanticObjectId):
    map_entry = await MinecraftMap.get(map_id)
    if not map_entry:
        raise HTTPException(status_code=404, detail="Map not found")
    
    await map_entry.delete()
    return {"message": "Map deleted successfully"}

@router.get("/search/{query}", response_model=Page[MinecraftMap])
async def search_maps(query: str):
    """Busca case-insensitive por nome ou descrição do mapa"""
    search_query = MinecraftMap.find({
        "$or": [
            {"name": {"$regex": query, "$options": "i"}},
            {"description": {"$regex": query, "$options": "i"}}
        ]
    })
    return await apaginate(search_query)

@router.get("/filter/by-world-type/{world_type}", response_model=Page[MinecraftMap])
async def filter_maps_by_world_type(world_type: str):
    """Filtrar mapas por tipo de mundo"""
    query = MinecraftMap.find({"world_type": {"$regex": world_type, "$options": "i"}})
    return await apaginate(query)

@router.get("/filter/by-size-range")
async def filter_maps_by_size_range(min_size: float = 0, max_size: float = 1000):
    """Filtrar mapas por tamanho em MB"""
    query = MinecraftMap.find({
        "size_mb": {"$gte": min_size, "$lte": max_size}
    })
    return await apaginate(query)

@router.get("/aggregations/by-world-type")
async def maps_by_world_type():
    """Quantidade de mapas por tipo de mundo"""
    pipeline = [
        {
            "$group": {
                "_id": "$world_type",
                "count": {"$sum": 1},
                "avg_size": {"$avg": "$size_mb"},
                "total_size": {"$sum": "$size_mb"},
                "maps": {
                    "$push": {
                        "name": "$name",
                        "size_mb": "$size_mb"
                    }
                }
            }
        },
        {
            "$sort": {"count": -1}
        }
    ]
    
    result = await MinecraftMap.aggregate(pipeline).to_list()
    return {"maps_by_world_type": result}

@router.get("/aggregations/usage-by-servers")
async def maps_usage_by_servers():
    """Mapas utilizados por servidores"""
    from models.servers import Server
    
    pipeline = [
        {
            "$lookup": {
                "from": "servers",
                "localField": "_id",
                "foreignField": "map_id",
                "as": "servers_using"
            }
        },
        {
            "$project": {
                "name": 1,
                "description": 1,
                "world_type": 1,
                "size_mb": 1,
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
    
    result = await MinecraftMap.aggregate(pipeline).to_list()
    return {"maps_usage": result}

@router.get("/stats/summary")
async def get_maps_summary():
    """Resumo estatístico dos mapas"""
    pipeline = [
        {
            "$group": {
                "_id": None,
                "total_maps": {"$sum": 1},
                "avg_size": {"$avg": "$size_mb"},
                "total_size": {"$sum": "$size_mb"},
                "min_size": {"$min": "$size_mb"},
                "max_size": {"$max": "$size_mb"}
            }
        }
    ]
    
    result = await MinecraftMap.aggregate(pipeline).to_list(1)
    stats = result[0] if result else {
        "total_maps": 0, "avg_size": 0, "total_size": 0,
        "min_size": 0, "max_size": 0
    }
    
    # Contagem por tipo de mundo
    by_type_pipeline = [
        {
            "$group": {
                "_id": "$world_type",
                "count": {"$sum": 1}
            }
        }
    ]
    
    by_type = await MinecraftMap.aggregate(by_type_pipeline).to_list()
    
    return {
        "summary": stats,
        "by_world_type": {item["_id"]: item["count"] for item in by_type}
    }

@router.get("/ordered/by-size", response_model=Page[MinecraftMap])
async def get_maps_ordered_by_size(desc: bool = True):
    """Mapas ordenados por tamanho"""
    sort_order = -1 if desc else 1
    query = MinecraftMap.find_all().sort([("size_mb", sort_order)])
    return await apaginate(query)

@router.get("/ordered/by-name", response_model=Page[MinecraftMap])
async def get_maps_ordered_by_name(desc: bool = False):
    """Mapas ordenados por nome"""
    sort_order = -1 if desc else 1
    query = MinecraftMap.find_all().sort([("name", sort_order)])
    return await apaginate(query)
