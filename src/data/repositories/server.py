from data.database import Database

class Server:
    def __init__(self):
        self.db = Database(
            data_path="data/store/server_data.csv",
            index_path="data/store/server_index.seq",
            key_column="id",
            schema=["id", "name", "motd", "version", "slots", "difficulty", "online_mode", "enable_command_block", "spawn_monsters", "force_gamemode", "gamemode", "white_list", "pvp", "allow_flight", "allow_nether", "spawn_protection"]
        )

    def insert(self, server_data: dict):
        self.db.insert(server_data)
    
    def get(self, server_id: str) -> dict | None:
        return self.db.get(server_id)

    def get_all(self) -> list[dict]:
        return self.db.get_all()
    
    def update(self, server_id: str, update_data: dict):
        server_record = self.get(server_id)
        if not server_record:
            raise ValueError(f"Server with ID '{server_id}' not found.")
        
        server_record.update(update_data)
        self.db.update(server_id, server_record)
    
    def delete(self, server_id: str):
        self.db.delete(server_id)
    
    def get_server_properties(self, server_id: str) -> dict | None:
        server = self.get(server_id)
        if not server:
            return None

        properties = {}
        for key, value in server.items():
            if key not in ['id', 'name', 'deleted']:
                properties[key] = value
        return properties

    def close(self):
        self.db.close()

    def count(self) -> int:
        return self.db.count()
