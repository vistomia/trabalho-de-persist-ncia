from fastapi import APIRouter

router = APIRouter()

@router.get("/servers/", tags=["servers"])
async def read_users():
    return ["usuarios"]
