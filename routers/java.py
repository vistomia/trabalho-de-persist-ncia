from fastapi import APIRouter, Depends, Query, HTTPException
from sqlmodel import Session, select, func, or_
from models.java import Java, JavaResponse
from database.database import Database
import os
from dotenv import load_dotenv

load_dotenv()

db = Database(uri=os.getenv('DATABASE_URL', 'sqlite:///data.sqlite'))

def get_session():
    with Session(db.get_engine()) as session:
        yield session

router = APIRouter()

@router.get("/java/", tags=["java"], response_model=list[JavaResponse])
async def read_java(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: str | None = Query(None),
    session: Session = Depends(get_session)
):
    query = select(Java)    
    
    if search:
        query = query.where(
            or_(
                Java.name.contains(search),
                Java.link.contains(search)
            )
        )
    
    query = query.offset(skip).limit(limit)
    java_entries = session.exec(query).all()
    return java_entries

@router.get("/java/{java_id}", tags=["java"], response_model=JavaResponse)
async def read_java_by_id(java_id: int, session: Session = Depends(get_session)):
    """Get Java entry by ID"""
    java_entry = session.get(Java, java_id)
    if not java_entry:
        raise HTTPException(status_code=404, detail="Java entry not found")
    return java_entry

@router.get("/java/search/", tags=["java"], response_model=list[JavaResponse])
async def search_java(
    name: str | None = Query(None),
    link: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    session: Session = Depends(get_session)
):
    query = select(Java)
    
    filters = []
    if name:
        filters.append(Java.name.contains(name))
    if link:
        filters.append(Java.link.contains(link))
    
    if filters:
        query = query.where(or_(*filters))
    
    query = query.offset(skip).limit(limit)
    java_entries = session.exec(query).all()
    return java_entries

@router.get("/java/count/", tags=["java"])
async def count_java(session: Session = Depends(get_session)):
    count = session.exec(select(func.count(Java.id))).one()
    return {"count": count}

@router.get("/java/ordered/", tags=["java"], response_model=list[JavaResponse])
async def read_java_ordered(
    order_by: str = Query("id", regex="^(id|name|link|created_at)$"),
    desc: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    session: Session = Depends(get_session)
):
    query = select(Java)
    
    if order_by == "name":
        order_field = Java.name.desc() if desc else Java.name
    elif order_by == "link":
        order_field = Java.link.desc() if desc else Java.link
    elif order_by == "created_at":
        order_field = Java.created_at.desc() if desc else Java.created_at
    else:
        order_field = Java.id.desc() if desc else Java.id
    
    query = query.order_by(order_field).offset(skip).limit(limit)
    java_entries = session.exec(query).all()
    return java_entries

@router.post("/java/", tags=["java"], response_model=JavaResponse)
async def create_java(java: Java, session: Session = Depends(get_session)):
    session.add(java)
    session.commit()
    session.refresh(java)
    return java

@router.patch("/java/{java_id}", tags=["java"], response_model=JavaResponse)
async def update_java(
    java_id: int,
    java_update: dict,
    session: Session = Depends(get_session)
):
    java_entry = session.get(Java, java_id)
    if not java_entry:
        raise HTTPException(status_code=404, detail="Java entry not found")
    
    for key, value in java_update.items():
        if hasattr(java_entry, key) and value is not None:
            field_info = Java.model_fields.get(key)
            if field_info:
                try:
                    field_type = field_info.annotation
                    if not isinstance(value, field_type):
                        if field_type in (int, float, str, bool):
                            value = field_type(value)
                        else:
                            raise ValueError(f"Invalid type for field {key}")
                    setattr(java_entry, key, value)
                except (ValueError, TypeError):
                    raise HTTPException(status_code=400, detail=f"Invalid value for field {key}")
    
    session.add(java_entry)
    session.commit()
    session.refresh(java_entry)
    return java_entry

@router.delete("/java/{java_id}", tags=["java"])
async def delete_java(java_id: int, session: Session = Depends(get_session)):
    java_entry = session.get(Java, java_id)
    if not java_entry:
        raise HTTPException(status_code=404, detail="Java entry not found")
    
    session.delete(java_entry)
    session.commit()
    return {"message": "Java entry deleted successfully"}