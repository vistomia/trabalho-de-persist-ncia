from fastapi import APIRouter, HTTPException
from beanie import PydanticObjectId
from beanie.odm.fields import Link
from fastapi_pagination import Page
from fastapi_pagination.ext.beanie import apaginate
from models import java_links, minecraft_maps, operators, servers_properties, servers, softwares, users

router = APIRouter(
    prefix="/operators",
    tags=["Operators"],
)
@router.get("/", response_model=Page[operators.Operator])
async def read_operators(
    server_id: PydanticObjectId | None = None,
    user_id: PydanticObjectId | None = None,
    permission_level: str | None = None,
):
    query = {}
    
    if server_id:
        query["server_id"] = server_id
    if user_id:
        query["user_id"] = user_id
    if permission_level:
        query["permission_level"] = {"$regex": permission_level, "$options": "i"}
    
    operators_page = await apaginate(operators.Operator, query_filter=query)
    
    # Fetch related documents for each operator
    for operator in operators_page.items:
        await operator.fetch_all_links()
    
    return operators_page

@router.get("/{server_id}/{user_id}", response_model=operators.Operator)
async def read_operator_by_ids(
    server_id: PydanticObjectId, 
    user_id: PydanticObjectId
):
    operator = await operators.Operator.find_one({
        "server_id": server_id,
        "user_id": user_id
    }).fetch_links()
    
    if not operator:
        raise HTTPException(status_code=404, detail="Operator relationship not found")
    return operator

@router.get("/count/")
async def count_operators(
    server_id: PydanticObjectId | None = None,
    user_id: PydanticObjectId | None = None,
):
    """Get total count of operators with optional filters"""
    query = {}
    
    if server_id:
        query["server_id"] = server_id
    if user_id:
        query["user_id"] = user_id
    
    count = await operators.Operator.find(query).count()
    return {"count": count}

@router.post("/", response_model=operators.Operator)
async def create_operator(operator: operators.Operator):
    # Check if server exists
    server = await servers.Server.get(operator.server_id)
    if not server:
        raise HTTPException(status_code=400, detail="Server not found")
    
    # Check if user exists
    user = await users.User.get(operator.user_id)
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    
    # Check if operator relationship already exists
    existing = await operators.Operator.find_one({
        "server_id": operator.server_id,
        "user_id": operator.user_id
    })
    
    if existing:
        raise HTTPException(
            status_code=400, 
            detail="Operator relationship already exists for this server and user"
        )
    
    created_operator = await operator.insert()
    await created_operator.fetch_all_links()
    return created_operator

@router.patch("/{server_id}/{user_id}", response_model=operators.Operator)
async def update_operator(
    server_id: PydanticObjectId,
    user_id: PydanticObjectId,
    operator_update: dict,
):
    """Update operator relationship (mainly permission level)"""
    operator = await operators.Operator.find_one({
        "server_id": server_id,
        "user_id": user_id
    })
    
    if not operator:
        raise HTTPException(status_code=404, detail="Operator relationship not found")
    
    # Only allow updating permission_level (server_id and user_id are primary keys)
    allowed_fields = ["permission_level"]
    for key, value in operator_update.items():
        if key in allowed_fields and value is not None:
            setattr(operator, key, value)
    
    await operator.save()
    await operator.fetch_all_links()
    return operator

@router.delete("/{server_id}/{user_id}")
async def delete_operator(
    server_id: PydanticObjectId, 
    user_id: PydanticObjectId
):
    operator = await operators.Operator.find_one({
        "server_id": server_id,
        "user_id": user_id
    })
    
    if not operator:
        raise HTTPException(status_code=404, detail="Operator relationship not found")
    
    await operator.delete()
    return {"message": "Operator relationship deleted successfully"}

@router.delete("/by-server/{server_id}")
async def delete_operators_by_server(server_id: PydanticObjectId):
    operators_list = await operators.Operator.find({"server_id": server_id}).to_list()
    
    if not operators_list:
        raise HTTPException(status_code=404, detail="No operators found for this server")
    
    await operators.Operator.find({"server_id": server_id}).delete()
    
    return {"message": f"Deleted {len(operators_list)} operator relationships for server {server_id}"}

@router.get("/aggregations/by-permission-level")
async def operators_by_permission_level():
    """Distribuição de operadores por nível de permissão"""
    pipeline = [
        {
            "$group": {
                "_id": "$permission_level",
                "count": {"$sum": 1},
                "operators": {
                    "$push": {
                        "server_id": "$server_id",
                        "user_id": "$user_id",
                        "granted_at": "$granted_at"
                    }
                }
            }
        },
        {
            "$sort": {"count": -1}
        }
    ]
    
    result = await operators.Operator.aggregate(pipeline).to_list()
    return {"operators_by_permission": result}

@router.get("/aggregations/most-active-operators")
async def most_active_operators():
    """Usuários que são operadores em mais servidores"""
    pipeline = [
        {
            "$group": {
                "_id": "$user_id",
                "servers_count": {"$sum": 1},
                "permissions": {
                    "$push": {
                        "server_id": "$server_id",
                        "permission_level": "$permission_level",
                        "granted_at": "$granted_at"
                    }
                }
            }
        },
        {
            "$lookup": {
                "from": "users",
                "localField": "_id",
                "foreignField": "_id",
                "as": "user_info"
            }
        },
        {
            "$project": {
                "user_id": "$_id",
                "username": {"$arrayElemAt": ["$user_info.username", 0]},
                "email": {"$arrayElemAt": ["$user_info.email", 0]},
                "servers_count": 1,
                "permissions": 1
            }
        },
        {
            "$sort": {"servers_count": -1}
        }
    ]
    
    result = await operators.Operator.aggregate(pipeline).to_list()
    return {"most_active_operators": result}

@router.get("/aggregations/by-granted-month")
async def operators_by_granted_month():
    """Operadores concedidos por mês"""
    pipeline = [
        {
            "$group": {
                "_id": {
                    "year": {"$year": "$granted_at"},
                    "month": {"$month": "$granted_at"}
                },
                "count": {"$sum": 1},
                "permissions": {
                    "$push": {
                        "server_id": "$server_id",
                        "user_id": "$user_id",
                        "permission_level": "$permission_level"
                    }
                }
            }
        },
        {
            "$sort": {"_id.year": -1, "_id.month": -1}
        }
    ]
    
    result = await operators.Operator.aggregate(pipeline).to_list()
    return {"operators_by_month": result}

@router.get("/complex/server-operators-details/{server_id}")
async def get_server_operators_details(server_id: PydanticObjectId):
    """Detalhes completos dos operadores de um servidor específico"""
    pipeline = [
        {
            "$match": {"server_id": server_id}
        },
        {
            "$lookup": {
                "from": "users",
                "localField": "user_id",
                "foreignField": "_id",
                "as": "user_info"
            }
        },
        {
            "$lookup": {
                "from": "servers",
                "localField": "server_id",
                "foreignField": "_id",
                "as": "server_info"
            }
        },
        {
            "$lookup": {
                "from": "users",
                "localField": "granted_by",
                "foreignField": "_id",
                "as": "granted_by_info"
            }
        },
        {
            "$project": {
                "permission_level": 1,
                "granted_at": 1,
                "user": {"$arrayElemAt": ["$user_info", 0]},
                "server": {"$arrayElemAt": ["$server_info", 0]},
                "granted_by_user": {"$arrayElemAt": ["$granted_by_info", 0]}
            }
        },
        {
            "$sort": {"granted_at": -1}
        }
    ]
    
    result = await operators.Operator.aggregate(pipeline).to_list()
    if not result:
        raise HTTPException(status_code=404, detail="Nenhum operador encontrado para este servidor")
    
    return {"server_operators_details": result}

@router.get("/stats/summary")
async def get_operators_summary():
    """Resumo estatístico dos operadores"""
    total = await operators.Operator.count()
    
    # Por nível de permissão
    by_permission = await operators.Operator.aggregate([
        {"$group": {"_id": "$permission_level", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]).to_list()
    
    # Servidores únicos com operadores
    unique_servers = await operators.Operator.aggregate([
        {"$group": {"_id": "$server_id"}},
        {"$count": "unique_servers"}
    ]).to_list(1)
    
    # Usuários únicos que são operadores
    unique_users = await operators.Operator.aggregate([
        {"$group": {"_id": "$user_id"}},
        {"$count": "unique_users"}
    ]).to_list(1)
    
    return {
        "total_operators": total,
        "by_permission_level": {item["_id"]: item["count"] for item in by_permission},
        "servers_with_operators": unique_servers[0]["unique_servers"] if unique_servers else 0,
        "users_as_operators": unique_users[0]["unique_users"] if unique_users else 0
    }
