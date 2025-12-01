from fastapi import APIRouter, Depends, Query, HTTPException
from sqlmodel import Session, select, func, or_
from models.map import Map
from database.database import Database

import os
from dotenv import load_dotenv

load_dotenv()

db = Database(uri=os.getenv('DATABASE_URL', 'sqlite:///data.sqlite'))

def get_session():
    with Session(db.get_engine()) as session:
        yield session

router = APIRouter()

@router.get("/maps/", tags=["maps"], response_model=list[Map])
async def read_maps(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: str | None = Query(None),
    session: Session = Depends(get_session)
):
    query = select(Map)    
    
    if search:
        query = query.where(
            or_(
                Map.name.contains(search),
                Map.description.contains(search),
                Map.link.contains(search)
            )
        )
    
    query = query.offset(skip).limit(limit)
    maps = session.exec(query).all()
    return maps

@router.get("/maps/{map_id}", tags=["maps"], response_model=Map)
async def read_map_by_id(map_id: int, session: Session = Depends(get_session)):
    map_entry = session.get(Map, map_id)
    if not map_entry:
        raise HTTPException(status_code=404, detail="Map not found")
    return map_entry

@router.get("/maps/search/", tags=["maps"], response_model=list[Map])
async def search_maps(
    name: str | None = Query(None),
    description: str | None = Query(None),
    link: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    session: Session = Depends(get_session)
):
    query = select(Map)
    
    filters = []
    if name:
        filters.append(Map.name.contains(name))
    if description:
        filters.append(Map.description.contains(description))
    if link:
        filters.append(Map.link.contains(link))
    
    if filters:
        query = query.where(or_(*filters))
    
    query = query.offset(skip).limit(limit)
    maps = session.exec(query).all()
    return maps

@router.get("/maps/count/", tags=["maps"])
async def count_maps(session: Session = Depends(get_session)):
    count = session.exec(select(func.count(Map.id))).one()
    return {"count": count}

@router.get("/maps/ordered/", tags=["maps"], response_model=list[Map])
async def read_maps_ordered(
    order_by: str = Query("id", regex="^(id|name|description|link|created_at)$"),
    desc: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    session: Session = Depends(get_session)
):
    query = select(Map)
    
    if order_by == "name":
        order_field = Map.name.desc() if desc else Map.name
    elif order_by == "description":
        order_field = Map.description.desc() if desc else Map.description
    elif order_by == "link":
        order_field = Map.link.desc() if desc else Map.link
    elif order_by == "created_at":
        order_field = Map.created_at.desc() if desc else Map.created_at
    else:
        order_field = Map.id.desc() if desc else Map.id
    
    query = query.order_by(order_field).offset(skip).limit(limit)
    maps = session.exec(query).all()
    return maps

@router.post("/maps/", tags=["maps"], response_model=Map)
async def create_map(map_data: Map, session: Session = Depends(get_session)):
    session.add(map_data)
    session.commit()
    session.refresh(map_data)
    return map_data

@router.patch("/maps/{map_id}", tags=["maps"], response_model=Map)
async def update_map(
    map_id: int,
    map_update: dict,
    session: Session = Depends(get_session)
):
    map_entry = session.get(Map, map_id)
    if not map_entry:
        raise HTTPException(status_code=404, detail="Map not found")
    
    for key, value in map_update.items():
        if hasattr(map_entry, key) and value is not None:
            field_info = Map.model_fields.get(key)
            if field_info:
                try:
                    field_type = field_info.annotation
                    if not isinstance(value, field_type):
                        if field_type in (int, float, str, bool):
                            value = field_type(value)
                        else:
                            raise ValueError(f"Invalid type for field {key}")
                    setattr(map_entry, key, value)
                except (ValueError, TypeError):
                    raise HTTPException(status_code=400, detail=f"Invalid value for field {key}")
    
    session.add(map_entry)
    session.commit()
    session.refresh(map_entry)
    return map_entry

@router.delete("/maps/{map_id}", tags=["maps"])
async def delete_map(map_id: int, session: Session = Depends(get_session)):
    map_entry = session.get(Map, map_id)
    if not map_entry:
        raise HTTPException(status_code=404, detail="Map not found")
    
    session.delete(map_entry)
    session.commit()
    return {"message": "Map deleted successfully"}