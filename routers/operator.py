from fastapi import APIRouter, Depends, Query, HTTPException
from sqlmodel import Session, select, func, and_
from models.operator import Operator
from database.database import Database
from models.server import Server
from models.user import User

import os
from dotenv import load_dotenv

load_dotenv()

db = Database(uri=os.getenv('DATABASE_URL', 'sqlite:///data.sqlite'))

def get_session():
    with Session(db.get_engine()) as session:
        yield session

router = APIRouter()

@router.get("/operators/", tags=["operators"], response_model=list[Operator])
async def read_operators(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    server_id: int | None = Query(None),
    user_id: int | None = Query(None),
    permission_level: str | None = Query(None),
    session: Session = Depends(get_session)
):
    query = select(Operator)
    
    filters = []
    if server_id:
        filters.append(Operator.server_id == server_id)
    if user_id:
        filters.append(Operator.user_id == user_id)
    if permission_level:
        filters.append(Operator.permission_level.contains(permission_level))
    
    if filters:
        query = query.where(and_(*filters))
    
    query = query.offset(skip).limit(limit)
    operators = session.exec(query).all()
    return operators

@router.get("/operators/{server_id}/{user_id}", tags=["operators"], response_model=Operator)
async def read_operator_by_ids(
    server_id: int, 
    user_id: int, 
    session: Session = Depends(get_session)
):
    operator = session.exec(
        select(Operator).where(
            and_(Operator.server_id == server_id, Operator.user_id == user_id)
        )
    ).first()
    
    if not operator:
        raise HTTPException(status_code=404, detail="Operator relationship not found")
    return operator

@router.get("/operators/count/", tags=["operators"])
async def count_operators(
    server_id: int | None = Query(None),
    user_id: int | None = Query(None),
    session: Session = Depends(get_session)
):
    """Get total count of operators with optional filters"""
    query = select(func.count()).select_from(Operator)
    
    filters = []
    if server_id:
        filters.append(Operator.server_id == server_id)
    if user_id:
        filters.append(Operator.user_id == user_id)
    
    if filters:
        query = query.where(and_(*filters))
    
    count = session.exec(query).one()
    return {"count": count}

@router.get("/operators/ordered/", tags=["operators"], response_model=list[Operator])
async def read_operators_ordered(
    order_by: str = Query("server_id", regex="^(server_id|user_id|permission_level|granted_at)$"),
    desc: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    session: Session = Depends(get_session)
):
    query = select(Operator)
    
    if order_by == "user_id":
        order_field = Operator.user_id.desc() if desc else Operator.user_id
    elif order_by == "permission_level":
        order_field = Operator.permission_level.desc() if desc else Operator.permission_level
    elif order_by == "granted_at":
        order_field = Operator.granted_at.desc() if desc else Operator.granted_at
    else:
        order_field = Operator.server_id.desc() if desc else Operator.server_id
    
    query = query.order_by(order_field).offset(skip).limit(limit)
    operators = session.exec(query).all()
    return operators

@router.post("/operators/", tags=["operators"], response_model=Operator)
async def create_operator(operator: Operator, session: Session = Depends(get_session)):
    if not session.get(Server, operator.server_id):
        raise HTTPException(status_code=400, detail="Server not found")
    if not session.get(User, operator.user_id):
        raise HTTPException(status_code=400, detail="User not found")
    
    # Check if operator relationship already exists
    existing = session.exec(
        select(Operator).where(
            and_(
                Operator.server_id == operator.server_id,
                Operator.user_id == operator.user_id
            )
        )
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400, 
            detail="Operator relationship already exists for this server and user"
        )
    
    session.add(operator)
    session.commit()
    session.refresh(operator)
    return operator

@router.patch("/operators/{server_id}/{user_id}", tags=["operators"], response_model=Operator)
async def update_operator(
    server_id: int,
    user_id: int,
    operator_update: dict,
    session: Session = Depends(get_session)
):
    """Update operator relationship (mainly permission level)"""
    operator = session.exec(
        select(Operator).where(
            and_(Operator.server_id == server_id, Operator.user_id == user_id)
        )
    ).first()
    
    if not operator:
        raise HTTPException(status_code=404, detail="Operator relationship not found")
    
    # Only allow updating permission_level (server_id and user_id are primary keys)
    allowed_fields = ["permission_level"]
    for key, value in operator_update.items():
        if hasattr(operator, key) and value is not None:
            field_info = Operator.model_fields.get(key)
            if field_info:
                try:
                    field_type = field_info.annotation
                    if not isinstance(value, field_type):
                        if field_type in (int, float, str, bool):
                            value = field_type(value)
                        else:
                            raise ValueError(f"Invalid type for field {key}")
                    setattr(operator, key, value)
                except (ValueError, TypeError):
                    raise HTTPException(status_code=400, detail=f"Invalid value for field {key}")
    
    session.add(operator)
    session.commit()
    session.refresh(operator)
    return operator

@router.delete("/operators/{server_id}/{user_id}", tags=["operators"])
async def delete_operator(
    server_id: int, 
    user_id: int, 
    session: Session = Depends(get_session)
):
    operator = session.exec(
        select(Operator).where(
            and_(Operator.server_id == server_id, Operator.user_id == user_id)
        )
    ).first()
    
    if not operator:
        raise HTTPException(status_code=404, detail="Operator relationship not found")
    
    session.delete(operator)
    session.commit()
    return {"message": "Operator relationship deleted successfully"}

@router.delete("/operators/by-server/{server_id}", tags=["operators"])
async def delete_operators_by_server(server_id: int, session: Session = Depends(get_session)):
    operators = session.exec(select(Operator).where(Operator.server_id == server_id)).all()
    
    if not operators:
        raise HTTPException(status_code=404, detail="No operators found for this server")
    
    for operator in operators:
        session.delete(operator)
    
    session.commit()
    return {"message": f"Deleted {len(operators)} operator relationships for server {server_id}"}