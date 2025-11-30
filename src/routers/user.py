from fastapi import APIRouter, Depends, Query, HTTPException
from sqlmodel import Session, select, func, or_
from models.user import User, UserResponse
from database.database import Database

# Create database instance
db = Database(uri='sqlite:///data.sqlite')

def get_session():
    """Dependency to get database session"""
    with Session(db.get_engine()) as session:
        yield session

router = APIRouter()

@router.get("/users/", tags=["users"], response_model=list[UserResponse])
async def read_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: str | None = Query(None),
    session: Session = Depends(get_session)
):
    """List users with pagination and text search"""
    query = select(User)    
    
    if search:
        query = query.where(
            or_(
                User.username.contains(search),
                User.email.contains(search)
            )
        )
    
    query = query.offset(skip).limit(limit)
    users = session.exec(query).all()
    return users

@router.get("/users/{user_id}", tags=["users"], response_model=UserResponse)
async def read_user(user_id: int, session: Session = Depends(get_session)):
    """Get user by ID"""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/users/search/", tags=["users"], response_model=list[UserResponse])
async def search_users(
    username: str | None = Query(None),
    email: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    session: Session = Depends(get_session)
):
    """Search users by username or email with pagination"""
    query = select(User)
    
    filters = []
    if username:
        filters.append(User.username.contains(username))
    if email:
        filters.append(User.email.contains(email))
    
    if filters:
        query = query.where(or_(*filters))
    
    query = query.offset(skip).limit(limit)
    users = session.exec(query).all()
    return users

@router.get("/users/count/", tags=["users"])
async def count_users(session: Session = Depends(get_session)):
    """Get total count of users"""
    count = session.exec(select(func.count(User.id))).one()
    return {"count": count}

@router.get("/users/ordered/", tags=["users"], response_model=list[UserResponse])
async def read_users_ordered(
    order_by: str = Query("id", regex="^(id|username|email)$"),
    desc: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    session: Session = Depends(get_session)
):
    """List users with ordering and pagination"""
    query = select(User)
    
    if order_by == "username":
        order_field = User.username.desc() if desc else User.username
    elif order_by == "email":
        order_field = User.email.desc() if desc else User.email
    else:
        order_field = User.id.desc() if desc else User.id
    
    query = query.order_by(order_field).offset(skip).limit(limit)
    users = session.exec(query).all()
    return users

@router.post("/users/", tags=["users"], response_model=UserResponse)
async def create_user(user: User, session: Session = Depends(get_session)):
    """Create a new user"""
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@router.patch("/users/{user_id}", tags=["users"], response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: dict,
    session: Session = Depends(get_session)
):
    """Update user with PATCH (partial update)"""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    for key, value in user_update.items():
        if hasattr(user, key) and value is not None:
            setattr(user, key, value)
    
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@router.delete("/users/{user_id}", tags=["users"])
async def delete_user(user_id: int, session: Session = Depends(get_session)):
    """Delete user by ID"""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    session.delete(user)
    session.commit()
    return {"message": "User deleted successfully"}
