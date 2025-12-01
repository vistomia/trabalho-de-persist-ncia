from sqlmodel import Field, SQLModel, Relationship
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from .operator import Operator

class User(SQLModel, table=True):
    __tablename__ = "users"
    
    id: int | None = Field(default=None, primary_key=True)
    username: str
    email: str
    password: str
    
    # Relationship with operators
    operators: List["Operator"] = Relationship(back_populates="user")

class UserResponse(SQLModel):
    """User response model without password field"""
    id: int | None
    username: str
    email: str
