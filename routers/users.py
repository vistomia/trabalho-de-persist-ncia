from fastapi import APIRouter, HTTPException
from beanie import PydanticObjectId
from beanie.odm.fields import Link
from fastapi_pagination import Page
from fastapi_pagination.ext.beanie import apaginate
from models.users import User
from datetime import datetime

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.get("/", response_model=Page[User])
async def get_users():
    return await apaginate(User.find())

@router.get("/{user_id}", response_model=User)
async def get_user(user_id: PydanticObjectId) -> User:
    user = await User.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    return user

@router.post("/", response_model=User)
async def create_user(user: User):
    existing_user = await User.find_one({
        "$or": [
            {"email": user.email},
            {"username": user.username}
        ]
    })
    
    if (existing_user):
        raise HTTPException(status_code=400, detail="Conta já cadastrada")
    
    await user.insert()
    return user

@router.put("/{user_id}", response_model=User)
async def update_user(user_id: PydanticObjectId, user_data: dict):
    user = await User.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    for key, value in user_data.items():
        setattr(user, key, value)

    await user.save()
    return user

@router.delete("/{user_id}")
async def delete_user(user_id: PydanticObjectId):
    user = await User.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    await user.delete()
    return {"message": "Usuário excluído com sucesso"}

@router.get("/search/by-username/{username}", response_model=Page[User])
async def search_users_by_username(username: str):
    query = User.find({"username": {"$regex": f"^{username}", "$options": "i"}})
    return await apaginate(query)

@router.get("/count")
async def get_users_stats():
    total = await User.count()
    
    return { "total_users": total }

@router.get("/by-year/{year}", response_model=Page[User])
async def get_users_by_year(year: int):
    """Listar usuários criados em um ano específico"""
    start_date = datetime(year, 1, 1)
    end_date = datetime(year + 1, 1, 1)
    
    query = User.find({
        "created_at": {
            "$gte": start_date,
            "$lt": end_date
        }
    })
    return await apaginate(query)

@router.get("/search/by-email/{email}", response_model=Page[User])
async def search_users_by_email(email: str):
    """Busca case-insensitive por email"""
    query = User.find({"email": {"$regex": email, "$options": "i"}})
    return await apaginate(query)

@router.get("/aggregations/users-with-servers")
async def users_with_servers():
    """Usuários que possuem servidores (proprietários)"""
    from models.servers import Server
    
    pipeline = [
        {
            "$lookup": {
                "from": "servers",
                "localField": "_id",
                "foreignField": "owner_id",
                "as": "owned_servers"
            }
        },
        {
            "$match": {
                "owned_servers": {"$ne": []}
            }
        },
        {
            "$project": {
                "username": 1,
                "email": 1,
                "created_at": 1,
                "servers_count": {"$size": "$owned_servers"},
                "servers": {
                    "$map": {
                        "input": "$owned_servers",
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
    
    result = await User.aggregate(pipeline).to_list()
    return {"users_with_servers": result}

@router.get("/aggregations/users-as-operators")
async def users_as_operators():
    """Usuários que são operadores em servidores"""
    from models.operators import Operator
    
    pipeline = [
        {
            "$lookup": {
                "from": "operators",
                "localField": "_id",
                "foreignField": "user_id",
                "as": "operator_roles"
            }
        },
        {
            "$match": {
                "operator_roles": {"$ne": []}
            }
        },
        {
            "$project": {
                "username": 1,
                "email": 1,
                "created_at": 1,
                "operator_count": {"$size": "$operator_roles"},
                "roles": {
                    "$map": {
                        "input": "$operator_roles",
                        "as": "role",
                        "in": {
                            "server_id": "$$role.server_id",
                            "permission_level": "$$role.permission_level"
                        }
                    }
                }
            }
        },
        {
            "$sort": {"operator_count": -1}
        }
    ]
    
    result = await User.aggregate(pipeline).to_list()
    return {"users_as_operators": result}

@router.get("/aggregations/registration-by-month")
async def users_registration_by_month():
    """Usuários registrados por mês"""
    pipeline = [
        {
            "$group": {
                "_id": {
                    "year": {"$year": "$created_at"},
                    "month": {"$month": "$created_at"}
                },
                "count": {"$sum": 1},
                "users": {"$push": {"username": "$username", "created_at": "$created_at"}}
            }
        },
        {
            "$sort": {"_id.year": -1, "_id.month": -1}
        }
    ]
    
    result = await User.aggregate(pipeline).to_list()
    return {"users_by_month": result}

@router.get("/complex/complete-user-profile/{user_id}")
async def get_complete_user_profile(user_id: PydanticObjectId):
    """Perfil completo do usuário com servidores próprios e onde é operador"""
    pipeline = [
        {
            "$match": {"_id": user_id}
        },
        {
            "$lookup": {
                "from": "servers",
                "localField": "_id",
                "foreignField": "owner_id",
                "as": "owned_servers"
            }
        },
        {
            "$lookup": {
                "from": "operators",
                "localField": "_id", 
                "foreignField": "user_id",
                "as": "operator_roles"
            }
        },
        {
            "$lookup": {
                "from": "servers",
                "localField": "operator_roles.server_id",
                "foreignField": "_id",
                "as": "operator_servers"
            }
        },
        {
            "$project": {
                "username": 1,
                "email": 1,
                "created_at": 1,
                "owned_servers_count": {"$size": "$owned_servers"},
                "operator_roles_count": {"$size": "$operator_roles"},
                "owned_servers": "$owned_servers",
                "operator_roles": "$operator_roles",
                "operator_servers": "$operator_servers"
            }
        }
    ]
    
    result = await User.aggregate(pipeline).to_list(1)
    if not result:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    return {"complete_profile": result[0]}

