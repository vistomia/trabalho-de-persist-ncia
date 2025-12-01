from fastapi import APIRouter, Depends, Query, HTTPException
from sqlmodel import Session, select, func, or_
from models.server import Server
from models.operator import Operator
from database.database import Database

db = Database(uri='sqlite:///data.sqlite')

def get_session():
    """Dependency to get database session"""
    with Session(db.get_engine()) as session:
        yield session

router = APIRouter()

@router.get("/servers/", tags=["servers"], response_model=list[Server])
async def read_servers(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: str | None = Query(None),
    session: Session = Depends(get_session)
):
    """List servers with pagination and text search"""
    query = select(Server)    
    
    if search:
        query = query.where(Server.name.contains(search))
    
    query = query.offset(skip).limit(limit)
    servers = session.exec(query).all()
    return servers

@router.get("/servers/{server_id}", tags=["servers"], response_model=Server)
async def read_server_by_id(server_id: int, session: Session = Depends(get_session)):
    """Get server by ID"""
    server = session.get(Server, server_id)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    return server

@router.get("/server/{server_id}/operators/", tags=["operators"], response_model=list[Operator])
async def read_operators_by_server(
    server_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    session: Session = Depends(get_session)
):
    """Get all operators for a specific server"""
    query = select(Operator).where(Operator.server_id == server_id).offset(skip).limit(limit)
    operators = session.exec(query).all()
    return operators

@router.get("/servers/search/", tags=["servers"], response_model=list[Server])
async def search_servers(
    name: str | None = Query(None),
    owner_id: int | None = Query(None),
    software_id: int | None = Query(None),
    java_id: int | None = Query(None),
    server_properties_id: int | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    session: Session = Depends(get_session)
):
    """Search servers by various fields with pagination"""
    query = select(Server)
    
    filters = []
    if name:
        filters.append(Server.name.contains(name))
    if owner_id:
        filters.append(Server.owner_id == owner_id)
    if software_id:
        filters.append(Server.software_id == software_id)
    if java_id:
        filters.append(Server.java_id == java_id)
    if server_properties_id:
        filters.append(Server.server_properties_id == server_properties_id)
    
    if filters:
        query = query.where(or_(*filters))
    
    query = query.offset(skip).limit(limit)
    servers = session.exec(query).all()
    return servers

@router.get("/servers/by-owner/{owner_id}", tags=["servers"], response_model=list[Server])
async def read_servers_by_owner(
    owner_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    session: Session = Depends(get_session)
):
    """Get servers by owner ID"""
    query = select(Server).where(Server.owner_id == owner_id).offset(skip).limit(limit)
    servers = session.exec(query).all()
    return servers

@router.get("/servers/count/", tags=["servers"])
async def count_servers(session: Session = Depends(get_session)):
    """Get total count of servers"""
    count = session.exec(select(func.count(Server.id))).one()
    return {"count": count}

@router.get("/servers/count/by-owner/{owner_id}", tags=["servers"])
async def count_servers_by_owner(owner_id: int, session: Session = Depends(get_session)):
    """Get count of servers by owner"""
    count = session.exec(select(func.count(Server.id)).where(Server.owner_id == owner_id)).one()
    return {"count": count}

@router.get("/servers/ordered/", tags=["servers"], response_model=list[Server])
async def read_servers_ordered(
    order_by: str = Query("id", regex="^(id|name|owner_id|created_at)$"),
    desc: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    session: Session = Depends(get_session)
):
    """List servers with ordering and pagination"""
    query = select(Server)
    
    if order_by == "name":
        order_field = Server.name.desc() if desc else Server.name
    elif order_by == "owner_id":
        order_field = Server.owner_id.desc() if desc else Server.owner_id
    elif order_by == "created_at":
        order_field = Server.created_at.desc() if desc else Server.created_at
    else:
        order_field = Server.id.desc() if desc else Server.id
    
    query = query.order_by(order_field).offset(skip).limit(limit)
    servers = session.exec(query).all()
    return servers

@router.post("/servers/", tags=["servers"], response_model=Server)
async def create_server(server: Server, session: Session = Depends(get_session)):
    """Create a new server"""
    # Validate foreign key references exist
    from models.user import User
    from models.software import Software
    from models.java import Java
    from models.server_properties import ServerProperties
    
    if not session.get(User, server.owner_id):
        raise HTTPException(status_code=400, detail="Owner not found")
    if not session.get(Software, server.software_id):
        raise HTTPException(status_code=400, detail="Software not found")
    if not session.get(Java, server.java_id):
        raise HTTPException(status_code=400, detail="Java not found")
    if not session.get(ServerProperties, server.server_properties_id):
        raise HTTPException(status_code=400, detail="Server properties not found")
    
    session.add(server)
    session.commit()
    session.refresh(server)
    return server

@router.patch("/servers/{server_id}", tags=["servers"], response_model=Server)
async def update_server(
    server_id: int,
    server_update: dict,
    session: Session = Depends(get_session)
):
    """Update server with PATCH (partial update)"""
    server = session.get(Server, server_id)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    
    # Validate foreign key references if they're being updated
    if "owner_id" in server_update:
        from models.user import User
        if not session.get(User, server_update["owner_id"]):
            raise HTTPException(status_code=400, detail="Owner not found")
    
    if "software_id" in server_update:
        from models.software import Software
        if not session.get(Software, server_update["software_id"]):
            raise HTTPException(status_code=400, detail="Software not found")
    
    if "java_id" in server_update:
        from models.java import Java
        if not session.get(Java, server_update["java_id"]):
            raise HTTPException(status_code=400, detail="Java not found")
    
    if "server_properties_id" in server_update:
        from models.server_properties import ServerProperties
        if not session.get(ServerProperties, server_update["server_properties_id"]):
            raise HTTPException(status_code=400, detail="Server properties not found")
    
    for key, value in server_update.items():
        if hasattr(server, key) and value is not None:
            setattr(server, key, value)
    
    session.add(server)
    session.commit()
    session.refresh(server)
    return server

@router.delete("/servers/{server_id}", tags=["servers"])
async def delete_server(server_id: int, session: Session = Depends(get_session)):
    """Delete server by ID"""
    server = session.get(Server, server_id)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    
    session.delete(server)
    session.commit()
    return {"message": "Server deleted successfully"}
