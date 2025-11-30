from fastapi import APIRouter, Depends, Query, HTTPException
from sqlmodel import Session, select, func, or_
from models.server_properties import ServerProperties
from database.database import Database

db = Database(uri='sqlite:///data.sqlite')

def get_session():
    """Dependency to get database session"""
    with Session(db.get_engine()) as session:
        yield session

router = APIRouter()

@router.get("/server-properties/", tags=["server-properties"], response_model=list[ServerProperties])
async def read_server_properties(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: str | None = Query(None),
    session: Session = Depends(get_session)
):
    """List server properties with pagination and text search"""
    query = select(ServerProperties)    
    
    if search:
        query = query.where(
            or_(
                ServerProperties.motd.contains(search),
                ServerProperties.level_name.contains(search),
                ServerProperties.gamemode.contains(search),
                ServerProperties.difficulty.contains(search)
            )
        )
    
    query = query.offset(skip).limit(limit)
    properties = session.exec(query).all()
    return properties

@router.get("/server-properties/{properties_id}", tags=["server-properties"], response_model=ServerProperties)
async def read_server_properties_by_id(properties_id: int, session: Session = Depends(get_session)):
    """Get server properties by ID"""
    properties = session.get(ServerProperties, properties_id)
    if not properties:
        raise HTTPException(status_code=404, detail="Server properties not found")
    return properties

@router.get("/server-properties/search/", tags=["server-properties"], response_model=list[ServerProperties])
async def search_server_properties(
    gamemode: str | None = Query(None),
    difficulty: str | None = Query(None),
    motd: str | None = Query(None),
    level_name: str | None = Query(None),
    online_mode: bool | None = Query(None),
    hardcore: bool | None = Query(None),
    max_players: int | None = Query(None, ge=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    session: Session = Depends(get_session)
):
    """Search server properties by various fields with pagination"""
    query = select(ServerProperties)
    
    filters = []
    if gamemode:
        filters.append(ServerProperties.gamemode.contains(gamemode))
    if difficulty:
        filters.append(ServerProperties.difficulty.contains(difficulty))
    if motd:
        filters.append(ServerProperties.motd.contains(motd))
    if level_name:
        filters.append(ServerProperties.level_name.contains(level_name))
    if online_mode is not None:
        filters.append(ServerProperties.online_mode == online_mode)
    if hardcore is not None:
        filters.append(ServerProperties.hardcore == hardcore)
    if max_players is not None:
        filters.append(ServerProperties.max_players == max_players)
    
    if filters:
        query = query.where(or_(*filters))
    
    query = query.offset(skip).limit(limit)
    properties = session.exec(query).all()
    return properties

@router.get("/server-properties/count/", tags=["server-properties"])
async def count_server_properties(session: Session = Depends(get_session)):
    """Get total count of server properties"""
    count = session.exec(select(func.count(ServerProperties.id))).one()
    return {"count": count}

@router.get("/server-properties/ordered/", tags=["server-properties"], response_model=list[ServerProperties])
async def read_server_properties_ordered(
    order_by: str = Query("id", regex="^(id|gamemode|difficulty|motd|level_name|max_players)$"),
    desc: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    session: Session = Depends(get_session)
):
    """List server properties with ordering and pagination"""
    query = select(ServerProperties)
    
    if order_by == "gamemode":
        order_field = ServerProperties.gamemode.desc() if desc else ServerProperties.gamemode
    elif order_by == "difficulty":
        order_field = ServerProperties.difficulty.desc() if desc else ServerProperties.difficulty
    elif order_by == "motd":
        order_field = ServerProperties.motd.desc() if desc else ServerProperties.motd
    elif order_by == "level_name":
        order_field = ServerProperties.level_name.desc() if desc else ServerProperties.level_name
    elif order_by == "max_players":
        order_field = ServerProperties.max_players.desc() if desc else ServerProperties.max_players
    else:
        order_field = ServerProperties.id.desc() if desc else ServerProperties.id
    
    query = query.order_by(order_field).offset(skip).limit(limit)
    properties = session.exec(query).all()
    return properties

@router.post("/server-properties/", tags=["server-properties"], response_model=ServerProperties)
async def create_server_properties(properties: ServerProperties, session: Session = Depends(get_session)):
    """Create new server properties"""
    session.add(properties)
    session.commit()
    session.refresh(properties)
    return properties

@router.patch("/server-properties/{properties_id}", tags=["server-properties"], response_model=ServerProperties)
async def update_server_properties(
    properties_id: int,
    properties_update: dict,
    session: Session = Depends(get_session)
):
    """Update server properties with PATCH (partial update)"""
    properties = session.get(ServerProperties, properties_id)
    if not properties:
        raise HTTPException(status_code=404, detail="Server properties not found")
    
    for key, value in properties_update.items():
        if hasattr(properties, key) and value is not None:
            setattr(properties, key, value)
    
    session.add(properties)
    session.commit()
    session.refresh(properties)
    return properties

@router.delete("/server-properties/{properties_id}", tags=["server-properties"])
async def delete_server_properties(properties_id: int, session: Session = Depends(get_session)):
    """Delete server properties by ID"""
    properties = session.get(ServerProperties, properties_id)
    if not properties:
        raise HTTPException(status_code=404, detail="Server properties not found")
    
    session.delete(properties)
    session.commit()
    return {"message": "Server properties deleted successfully"}