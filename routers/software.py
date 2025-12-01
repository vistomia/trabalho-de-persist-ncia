from fastapi import APIRouter, Depends, Query, HTTPException
from sqlmodel import Session, select, func, or_
from models.software import Software
from database.database import Database

import os
from dotenv import load_dotenv

load_dotenv()

db = Database(uri=os.getenv('DATABASE_URL', 'sqlite:///data.sqlite'))

def get_session():
    with Session(db.get_engine()) as session:
        yield session

router = APIRouter()

@router.get("/software/", tags=["software"], response_model=list[Software])
async def read_software(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: str | None = Query(None),
    session: Session = Depends(get_session)
):
    query = select(Software)    
    
    if search:
        query = query.where(
            or_(
                Software.name.contains(search),
                Software.link.contains(search),
                Software.version.contains(search)
            )
        )
    
    query = query.offset(skip).limit(limit)
    software = session.exec(query).all()
    return software

@router.get("/software/count/", tags=["software"])
async def count_software(session: Session = Depends(get_session)):
    count = session.exec(select(func.count(Software.id))).one()
    return {"count": count} 

@router.get("/software/{software_id}", tags=["software"], response_model=Software)
async def read_software_by_id(software_id: int, session: Session = Depends(get_session)):
    software = session.get(Software, software_id)
    if not software:
        raise HTTPException(status_code=404, detail="Software not found")
    return software

@router.get("/software/search/", tags=["software"], response_model=list[Software])
async def search_software(
    name: str | None = Query(None),
    version: str | None = Query(None),
    link: str | None = Query(None),
    plugins_enabled: bool | None = Query(None),
    mods_enabled: bool | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    session: Session = Depends(get_session)
):
    query = select(Software)
    
    filters = []
    if name:
        filters.append(Software.name.contains(name))
    if version:
        filters.append(Software.version.contains(version))
    if link:
        filters.append(Software.link.contains(link))
    if plugins_enabled is not None:
        filters.append(Software.plugins_enabled == plugins_enabled)
    if mods_enabled is not None:
        filters.append(Software.mods_enabled == mods_enabled)
    
    if filters:
        query = query.where(or_(*filters))
    
    query = query.offset(skip).limit(limit)
    software = session.exec(query).all()
    return software

@router.get("/software/ordered/", tags=["software"], response_model=list[Software])
async def read_software_ordered(
    order_by: str = Query("id", regex="^(id|name|version|link|created_at)$"),
    desc: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    session: Session = Depends(get_session)
):
    query = select(Software)
    
    if order_by == "name":
        order_field = Software.name.desc() if desc else Software.name
    elif order_by == "version":
        order_field = Software.version.desc() if desc else Software.version
    elif order_by == "link":
        order_field = Software.link.desc() if desc else Software.link
    elif order_by == "created_at":
        order_field = Software.created_at.desc() if desc else Software.created_at
    else:
        order_field = Software.id.desc() if desc else Software.id
    
    query = query.order_by(order_field).offset(skip).limit(limit)
    software = session.exec(query).all()
    return software

@router.post("/software/", tags=["software"], response_model=Software)
async def create_software(software: Software, session: Session = Depends(get_session)):
    session.add(software)
    session.commit()
    session.refresh(software)
    return software

@router.patch("/software/{software_id}", tags=["software"], response_model=Software)
async def update_software(
    software_id: int,
    software_update: dict,
    session: Session = Depends(get_session)
):
    software = session.get(Software, software_id)
    if not software:
        raise HTTPException(status_code=404, detail="Software not found")
    
    for key, value in software_update.items():
        if hasattr(software, key) and value is not None:
            field_info = Software.model_fields.get(key)
            if field_info:
                try:
                    field_type = field_info.annotation
                    if not isinstance(value, field_type):
                        if field_type in (int, float, str, bool):
                            value = field_type(value)
                        else:
                            raise ValueError(f"Invalid type for field {key}")
                    setattr(software, key, value)
                except (ValueError, TypeError):
                    raise HTTPException(status_code=400, detail=f"Invalid value for field {key}")
    
    session.add(software)
    session.commit()
    session.refresh(software)
    return software

@router.delete("/software/{software_id}", tags=["software"])
async def delete_software(software_id: int, session: Session = Depends(get_session)):
    software = session.get(Software, software_id)
    if not software:
        raise HTTPException(status_code=404, detail="Software not found")
    
    session.delete(software)
    session.commit()
    return {"message": "Software deleted successfully"}