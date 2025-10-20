import os
import logging
import tempfile
from data.repositories.user import User
from data.repositories.server import Server
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
    
    def update_user_password(self, username: str, password: str) -> bool:
        try:
            if password.strip() == "":
                logging.warning("Update failed: Password cannot be empty.")
                return False
            
            if len(password) < 6:
                logging.warning("Update failed: Password must be at least 6 characters long.")
                return False
            
            if not self.user_repo.get(username):
                logging.warning(f"Update failed: User '{username}' does not exist.")
                return False
            
            if username:
                logging.warning("Update failed: Username cannot be changed.")
                return False
            
            self.user_repo.delete(username)
            self.user_repo.insert({
                "username": username,
                "password": password
            })
            logging.info(f"User '{username}' updated successfully.")
            return True
        except ValueError as e:
            logging.error(f"Failed to update user '{username}': {e}")
            return False
    
    def delete_user(self, username: str) -> bool:
        if not self.user_repo.get(username):
            logging.warning(f"Delete failed: User '{username}' does not exist.")
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
        return self.user_repo.db.vacuum()
    
    # SERVER CRUD
    
    def create_server(self, server_data: dict) -> str:
        if server_data.get('name') is None or server_data.get('name').strip() == "":
            logging.warning("Server creation failed: 'name' field is required.")
            return "Error creating server: 'name' field is required."
        
        if server_data.get('version') is None or server_data.get('version').strip() == "":
            logging.warning("Server creation failed: 'version' field is required.")
            return "Error creating server: 'version' field is required."
        
        
        if server_data.get('difficulty') not in ['peaceful', 'easy', 'normal', 'hard']:
            logging.warning("Server creation failed: 'difficulty' must be one of peaceful, easy, normal, hard.")
            return "Error creating server: 'difficulty' must be one of peaceful, easy, normal, hard."
        
        

        try:
            self.server_repo.insert(server_data)
            return f"Server '{server_data.get('name')}' created successfully"
        except Exception as e:
            logging.error(f"Failed to create server: {e}")
            return f"Error creating server: {e}"
    
    def get_server(self, server_id: str) -> dict | None:
        return self.server_repo.get(server_id)
    
    def get_servers_paginated(self, limit: int, page: int) -> dict:
        servers = self.server_repo.db.get_page(page, limit)
        
        return {
            "data": servers
        }
    
    def update_server(self, server_id: str, updates: dict) -> bool:
        try:
            self.server_repo.update(server_id, updates)
            logging.info(f"Server '{server_id}' updated successfully.")
            return True
        except ValueError as e:
            logging.error(f"Failed to update server '{server_id}': {e}")
            return False
    
    def delete_server(self, server_id: str) -> bool:
        try:
            self.server_repo.delete(server_id)
            logging.info(f"Server '{server_id}' deleted successfully.")
            return True
        except Exception as e:
            logging.error(f"Failed to delete server '{server_id}': {e}")
            return False
    
    def count_servers(self) -> int:
        return self.server_repo.count()
    
    def start_server(self, server_id: str) -> str:
        server = self.get_server(server_id)
        if not server:
            return f"Server with ID '{server_id}' not found"
        
        logging.info(f"Starting server '{server_id}'...")

        with Server(name=server['name'], properties_dict=server) as srv:
            if not Server.server_exists(server['name']):
                srv.download_server_jar()
                srv.eula()
                srv.properties(server)
            srv.run_core()

        return f"Server '{server_id}' started successfully"

    def vacuum_servers(self) -> bool:
        return self.server_repo.db.vacuum()

    # Dump

    def dump_database(self, background_tasks: BackgroundTasks):
        """Cria um backup usando dump.py, compacta em um arquivo temporário e faz o stream dele."""
        
        from data.dump import zip_store_files
        
        # arquivo temporario
        with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp_zip_file:
            zip_path = tmp_zip_file.name
        
        store_path = "data/store"
        success = zip_store_files(store_path, zip_path)
        
        if not success:
            if os.path.exists(zip_path):
                os.remove(zip_path)
            raise Exception("Falha ao criar o backup do banco de dados")
        
        # leitor dos pedaços do zip
        def file_iterator(file_path: str):
            with open(file_path, "rb") as f:
                while chunk := f.read(8192): # 8kb
                    yield chunk

        background_tasks.add_task(os.remove, zip_path)

        return StreamingResponse(
            file_iterator(zip_path),
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename=database_backup.zip"}
        )

if __name__ == "__main__":
    controller = Controller()
    controller.start_server("1")