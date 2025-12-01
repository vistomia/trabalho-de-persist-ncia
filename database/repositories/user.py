from database.database import Database
import hashlib

class User:
    def __init__(self):
        self.db = Database(
            data_path="data/store/user_data.csv",
            index_path="data/store/user_index.seq",
            key_column="username",
            schema=["username", "password_hash", "token"]
        )

    def insert(self, user_data: dict):
        try:
            password_bytes = user_data['password'].encode('utf-8')
            result = self.db.insert({
                    "username": user_data['username'], 
                    "password": hashed_password.decode('utf-8'),
                    "token": token
                    })
            return result
        except Exception as e:
            print(f"Error inserting user: {e}")
            return False
    
    def get(self, username: str) -> dict | None:
        return self.db.get(username)
    
    def is_username_taken(self, username: str) -> bool:
        return self.get(username) is not None
    
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
