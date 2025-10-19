import database
import bcrypt

class User:
    def __init__(self):
        with database.Database(
            data_path="store/user_data.csv",
            index_path="store/user_index.seq",
            key_column="username",
            schema=["username", "password_hash"]
        ) as db:
            self.db = db

    def insert(self, user_data: dict):
        password_bytes = user_data['password'].encode('utf-8')
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password_bytes, salt)

        self.db.insert({
                "username": user_data['username'], 
                "password_hash": hashed_password.decode('utf-8')
                })
    
    def get(self, username: str) -> dict | None:
        return self.db.get(username)
    
    def is_username_taken(self, username: str) -> bool:
        return self.get(username) is not None

    def get_all(self) -> list[dict]:
        return self.db.get_all()
    
    def close(self):
        self.db.close()

    def count(self) -> int:
        return self.db.count()

    def verify_password(self, username: str, password: str) -> bool:
        user_record = self.get(username)
        if not user_record:
            return False
        
        stored_hash = user_record['password_hash'].encode('utf-8')
        password_bytes = password.encode('utf-8')
        
        return bcrypt.checkpw(password_bytes, stored_hash)
