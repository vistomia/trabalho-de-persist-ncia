from fastapi import APIRouter, HTTPException
from beanie import PydanticObjectId
from beanie.odm.fields import Link
from fastapi_pagination import Page
from fastapi_pagination.ext.beanie import apaginate
from models.java_links import Java, JavaCreate

router = APIRouter(
    prefix="/java",
    tags=["JavaLinks"],
)

@router.get("/", response_model=Page[Java])
async def read_java() -> Page[Java]:
    return await apaginate(Java.find_all(fetch_links=True))


@router.get("/{java_id}", response_model=Java)
async def read_java_by_id(java_id: PydanticObjectId): 
    # O .get() busca pelo _id do Mongo
    java_entry = await Java.get(java_id)
    
    if not java_entry:
        raise HTTPException(status_code=404, detail="Java entry not found")
    return java_entry


@router.get("/search/", response_model=Page[Java])
async def search_java(
    name: str | None = None, 
    link: str | None = None
):
    # ^ para pegar os que iniciam com a string e i para case-insensitive
    filters = []
    if name:
        filters.append({"name": {"$regex": f"^{name}", "$options": "i"}})
    if link:
        filters.append({"link": {"$regex": f"^{link}", "$options": "i"}})
    
    if not filters:
        return []

    query = Java.find({"$or": filters})
    
    return await apaginate(query)


@router.get("/count/")
async def count_java():
    count = await Java.count()
    return {"count": count}


@router.post("/", response_model=Java)
async def create_java(java: JavaCreate):
    java_data = Java(**java.dict())
    await java_data.create()
    return java_data


@router.patch("/{java_id}", response_model=Java)
async def update_java(java_id: PydanticObjectId, java_update: JavaCreate):
    # 1. Busca o documento
    java_db = await Java.get(java_id)
    if not java_db:
        raise HTTPException(status_code=404, detail="Java entry not found")

    # 2. Atualiza os campos. O exclude_unset garante que só atualiza o que foi enviado
    update_data = java_update.dict(exclude_unset=True)
    
    # Maneira manual de atualizar os campos no objeto
    for key, value in update_data.items():
        setattr(java_db, key, value)
    
    await java_db.save()
    return java_db


@router.delete("/{java_id}")
async def delete_java(java_id: PydanticObjectId):
    java_db = await Java.get(java_id)
    if not java_db:
        raise HTTPException(status_code=404, detail="Java entry not found")
    
    await java_db.delete()
    return {"message": "Deleted successfully"}


@router.get("/search/by-version/{version}", response_model=Page[Java])
async def search_java_by_version(version: str):
    """Busca case-insensitive por versão do Java"""
    query = Java.find({"version": {"$regex": version, "$options": "i"}})
    return await apaginate(query)

@router.get("/aggregations/usage-by-servers")
async def java_usage_by_servers():
    """Versões Java utilizadas por servidores"""
    from models.servers import Server
    
    pipeline = [
        {
            "$lookup": {
                "from": "servers",
                "localField": "_id",
                "foreignField": "java_id",
                "as": "servers_using"
            }
        },
        {
            "$project": {
                "name": 1,
                "version": 1,
                "link": 1,
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
    
    result = await Java.aggregate(pipeline).to_list()
    return {"java_usage": result}

@router.get("/aggregations/by-version-family")
async def java_by_version_family():
    """Distribuição por família de versão (8, 11, 17, 21, etc.)"""
    pipeline = [
        {
            "$addFields": {
                "major_version": {
                    "$toInt": {
                        "$arrayElemAt": [
                            {"$split": ["$version", "."]},
                            0
                        ]
                    }
                }
            }
        },
        {
            "$group": {
                "_id": "$major_version",
                "count": {"$sum": 1},
                "versions": {
                    "$push": {
                        "name": "$name",
                        "version": "$version"
                    }
                }
            }
        },
        {
            "$sort": {"_id": 1}
        }
    ]
    
    result = await Java.aggregate(pipeline).to_list()
    return {"java_by_version_family": result}

@router.get("/stats/summary")
async def get_java_summary():
    """Resumo estatístico das versões Java"""
    total = await Java.count()
    
    # Buscar versões mais utilizadas
    usage_pipeline = [
        {
            "$lookup": {
                "from": "servers",
                "localField": "_id",
                "foreignField": "java_id",
                "as": "servers"
            }
        },
        {
            "$project": {
                "name": 1,
                "version": 1,
                "usage_count": {"$size": "$servers"}
            }
        },
        {
            "$sort": {"usage_count": -1}
        },
        {
            "$limit": 5
        }
    ]
    
    most_used = await Java.aggregate(usage_pipeline).to_list()
    
    return {
        "total_java_versions": total,
        "most_used_versions": most_used
    }

@router.get("/ordered/by-name", response_model=Page[Java])
async def get_java_ordered_by_name(desc: bool = False):
    """Versões Java ordenadas por nome"""
    sort_order = -1 if desc else 1
    query = Java.find_all().sort([("name", sort_order)])
    return await apaginate(query)

@router.get("/ordered/by-version", response_model=Page[Java])
async def get_java_ordered_by_version(desc: bool = False):
    """Versões Java ordenadas por versão"""
    sort_order = -1 if desc else 1
    query = Java.find_all().sort([("version", sort_order)])
    return await apaginate(query)
