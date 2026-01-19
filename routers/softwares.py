from fastapi import APIRouter, HTTPException
from beanie import PydanticObjectId
from beanie.odm.fields import Link
from fastapi_pagination import Page
from fastapi_pagination.ext.beanie import apaginate
from models.softwares import Softwares

router = APIRouter(
    prefix="/softwares",
    tags=["Softwares"],
)

@router.get("/", response_model=Page[Softwares])
async def read_software():
    return await apaginate(Softwares)

@router.get("/{software_id}", response_model=Softwares)
async def read_software_by_id(software_id: PydanticObjectId):
    software = await Softwares.get(software_id)
    if not software:
        raise HTTPException(status_code=404, detail="Software not found")
    return software

@router.post("/", response_model=Softwares)
async def create_software(software_data: Softwares):
    software = Softwares(**software_data.dict(exclude_unset=True))
    await software.insert()
    return software

@router.patch("/{software_id}", response_model=Softwares)
async def update_software(
    software_id: PydanticObjectId,
    software_update: dict
):
    software = await Softwares.get(software_id)
    if not software:
        raise HTTPException(status_code=404, detail="Software not found")
    
    await software.update({"$set": software_update})
    return await Softwares.get(software_id)

@router.delete("/{software_id}")
async def delete_software(software_id: PydanticObjectId):
    software = await Softwares.get(software_id)
    if not software:
        raise HTTPException(status_code=404, detail="Software not found")
    
    await software.delete()
    return {"message": "Software deleted successfully"}

@router.get("/search/by-name/{name}", response_model=Page[Softwares])
async def search_softwares_by_name(name: str):
    """Busca case-insensitive por nome do software"""
    query = Softwares.find({"name": {"$regex": name, "$options": "i"}})
    return await apaginate(query)

@router.get("/search/by-version/{version}", response_model=Page[Softwares])
async def search_softwares_by_version(version: str):
    """Busca case-insensitive por versão"""
    query = Softwares.find({"version": {"$regex": version, "$options": "i"}})
    return await apaginate(query)

@router.get("/filter/with-plugins", response_model=Page[Softwares])
async def get_softwares_with_plugins():
    """Softwares que suportam plugins"""
    query = Softwares.find({"plugins_enabled": True})
    return await apaginate(query)

@router.get("/filter/with-mods", response_model=Page[Softwares])
async def get_softwares_with_mods():
    """Softwares que suportam mods"""
    query = Softwares.find({"mods_enabled": True})
    return await apaginate(query)

@router.get("/aggregations/usage-by-servers")
async def softwares_usage_by_servers():
    """Quantidade de servidores por software"""
    from models.servers import Server
    
    pipeline = [
        {
            "$lookup": {
                "from": "servers",
                "localField": "_id",
                "foreignField": "software_id",
                "as": "servers_using"
            }
        },
        {
            "$project": {
                "name": 1,
                "version": 1,
                "plugins_enabled": 1,
                "mods_enabled": 1,
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
    
    result = await Softwares.aggregate(pipeline).to_list()
    return {"softwares_usage": result}

@router.get("/aggregations/by-capabilities")
async def softwares_by_capabilities():
    """Estatísticas por capacidades (plugins/mods)"""
    pipeline = [
        {
            "$group": {
                "_id": {
                    "plugins_enabled": "$plugins_enabled",
                    "mods_enabled": "$mods_enabled"
                },
                "count": {"$sum": 1},
                "softwares": {
                    "$push": {
                        "name": "$name",
                        "version": "$version"
                    }
                }
            }
        },
        {
            "$sort": {"count": -1}
        }
    ]
    
    result = await Softwares.aggregate(pipeline).to_list()
    return {"softwares_by_capabilities": result}

@router.get("/stats/summary")
async def get_softwares_summary():
    """Resumo estatístico dos softwares"""
    total = await Softwares.count()
    with_plugins = await Softwares.find({"plugins_enabled": True}).count()
    with_mods = await Softwares.find({"mods_enabled": True}).count()
    both_capabilities = await Softwares.find({
        "plugins_enabled": True,
        "mods_enabled": True
    }).count()
    
    return {
        "total_softwares": total,
        "with_plugins": with_plugins,
        "with_mods": with_mods,
        "with_both_capabilities": both_capabilities,
        "vanilla_only": total - with_plugins - with_mods + both_capabilities
    }
