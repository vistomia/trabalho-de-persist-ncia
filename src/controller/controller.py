import logging
import data

class Controller:
    def __init__(self):
        self.user_repo = data.repositories.user.UserRepository()

    def register_user(self, username: str, password: str) -> bool:
        if self.user_repo.is_username_taken(username):
            logging.warning(f"Registration failed: Username '{username}' is already taken.")
            return False
        
        self.user_repo.insert({
            "username": username,
            "password": password
        })
        logging.info(f"User '{username}' registered successfully.")
        return True
    
    def authenticate_user(self, username: str, password: str) -> bool:
        if self.user_repo.verify_password(username, password):
            logging.info(f"User '{username}' authenticated successfully.")
            return True
        else:
            logging.warning(f"Authentication failed for user '{username}'.")
            return False
    
    def get_all_users(self) -> list[dict]:
        return self.user_repo.get_all()
    
    def count_users(self) -> int:
        return len(self.get_all_users())
    
     