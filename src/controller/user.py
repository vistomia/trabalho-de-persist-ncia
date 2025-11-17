import os
import logging
import tempfile
from database.repositories.user import User
from database.repositories.server import Server
from fastapi import BackgroundTasks
from fastapi.responses import StreamingResponse

class Controller:
    def __init__(self):
        self.user_repo = User()
        self.server_repo = Server()

    # USER CRUD
    
    def register_user(self, username: str, password: str) -> bool:
        if self.user_repo.is_username_taken(username):
            logging.warning(f"Registration failed: Username '{username}' is already taken.")
            return False
        
        if password.strip() == "":
            logging.warning("Registration failed: Password cannot be empty.")
            return False

        if len(password) < 6:
            logging.warning("Registration failed: Password must be at least 6 characters long.")
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
    
    def get_user(self, username: str) -> dict | None:
        return self.user_repo.get(username)
    
    def get_users_paginated(self, limit: int = 5, page: int = 0) -> dict:
        if limit <= 0:
            limit = 5
        users = self.user_repo.db.get_page(page, limit)
        total = self.user_repo.count()
        total_pages = (total + limit - 1) // limit
        
        return {
            "data": users,
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": total_pages
        }
    
    def update_user_password(self, username: str, old_password: str, new_password: str) -> str:
        try:
            if new_password.strip() == "":
                logging.warning("Update failed: Password cannot be empty.")
                return "error"
            
            if len(new_password) < 6:
                logging.warning("Update failed: Password must be at least 6 characters long.")
                return "error"
            
            if not self.authenticate_user(username, old_password):
                logging.warning("Update failed: Old password dont match.")
                return "error"

            self.user_repo.db.update(username, {
                "username": username,
                "password": new_password
            })
            
            ## self.user_repo.db.delete(username)
            ## self.user_repo.insert({"username": username, "password": new_password})

            logging.info(f"User '{username}' updated successfully.")
            return "update succesfully"
        except ValueError as e:
            logging.error(f"Failed to update user '{username}': {e}")
            return False
    
    def delete_user(self, username: str) -> bool:
        if not self.user_repo.get(username):
            logging.warning(f"Delete: User '{username}' does not exist.")
            return False
        
        try:
            self.user_repo.db.delete(username)
            logging.info(f"User '{username}' deleted successfully.")
            return True
        except Exception as e:
            logging.error(f"Failed to delete user '{username}': {e}")
            return False
    
    def count_users(self) -> int:
        return self.user_repo.count()

    def vacuum_users(self) -> None:
        pass