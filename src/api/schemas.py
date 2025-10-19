import pydantic
from pydantic import BaseModel
from typing import Optional

class ServerModel(BaseModel):
    id: Optional[str] = None
    name: str
    motd: str
    version: str = "1.8"
    slots: int
    difficulty: str
    online_mode: bool = True
    enable_command_block: bool = False
    spawn_monsters: bool = True
    force_gamemode: bool = False
    gamemode: str = "survival"
    white_list: bool = False
    pvp: bool = True
    allow_flight: bool = False
    allow_nether: bool = True
    spawn_protection: int = 16

class UserModel(BaseModel):
    username: str
    password: str