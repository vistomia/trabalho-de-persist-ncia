import database
"""
slots
difficulty
online-mode
enable-command-block
spawn-monsters
force-gamemode
gamemode
white-list
pvp
allow-flight
allow-nether
spawn-protection
"""

class Server:
    def __init__(self):
        with database.Database(
            data_path="store/server_data.csv",
            index_path="store/server_index.seq",
            key_column="id",
            schema=["id", "name", "motd", "version", "slots", "difficulty", "online-mode", "enable-command-block", "spawn-monsters", "force-gamemode", "gamemode", "white-list", "pvp", "allow-flight", "allow-nether", "spawn-protection"]
        ) as db:
            self.db = db

    def insert(self, server_data: dict):
        self.db.insert(server_data)
    
    def get(self, server_id: str) -> dict | None:
        return self.db.get(server_id)

    def get_all(self) -> list[dict]:
        return self.db.get_all()
    
    def close(self):
        self.db.close()

    def count(self) -> int:
        return self.db.count()
