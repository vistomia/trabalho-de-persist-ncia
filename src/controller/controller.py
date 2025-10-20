import logging
from data.repositories.server import Server
from data.repositories.user import User
import data
import zipfile
import os
import io
import tempfile
from fastapi import BackgroundTasks
from fastapi.responses import StreamingResponse
from data.dump import zip_store_files
import hashlib
import core.server

class Controller:
    def __init__(self):
        self.user_repo = User()
        self.server_repo = Server()

    # ============= USER CRUD =============
    
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
    
    def get_user(self, username: str) -> dict | None:
        return self.user_repo.get(username)
    
    def get_users_paginated(self, limit: int, page: int = 0) -> dict:
        users = self.user_repo.db.get_page(page, limit)
        total = self.user_repo.count()
        total_pages = (total + limit - 1) // limit  # Ceiling division
        
        return {
            "data": users,
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": total_pages
        }
    
    def update_user(self, username: str, updates: dict) -> bool:
        try:
            self.user_repo.db.update(username, updates)
            logging.info(f"User '{username}' updated successfully.")
            return True
        except ValueError as e:
            logging.error(f"Failed to update user '{username}': {e}")
            return False
    
    def delete_user(self, username: str) -> bool:
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
        self.user_repo.db.vacuum()

    # ============= SERVER CRUD =============
    
    def create_server(self, server_data: dict) -> str:
        try:
            self.server_repo.insert(server_data)
            return f"Server '{server_data.get('name')}' created successfully"
        except Exception as e:
            logging.error(f"Failed to create server: {e}")
            return f"Error creating server: {e}"
    
    def get_server(self, server_id: str) -> dict | None:
        return self.server_repo.get(server_id)
    
    def get_servers_paginated(self, limit: int, page: int = 0) -> dict:
        servers = self.server_repo.db.get_page(page, limit)
        total = self.server_repo.count()
        total_pages = (total + limit - 1) // limit  # Ceiling division
        
        return {
            "data": servers,
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": total_pages
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
        
        # Aqui você implementaria a lógica de iniciar o servidor
        logging.info(f"Starting server '{server_id}'...")
        return f"Server '{server_id}' started successfully"

    def vacuum_servers(self) -> bool:
        return self.server_repo.db.vacuum()

    # ============= DATABASE OPERATIONS =============

    def dump_database(self, background_tasks: BackgroundTasks):
        """Cria um backup usando dump.py, compacta em um arquivo temporário e faz o stream dele."""
        
        from data.dump import zip_store_files
        
        # 1. Cria um arquivo temporário para o backup
        with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp_zip_file:
            zip_path = tmp_zip_file.name
        
        # 2. Usa a função do dump.py para criar o backup
        store_path = "data/store"
        success = zip_store_files(store_path, zip_path)
        
        if not success:
            # Remove o arquivo temporário se falhou
            if os.path.exists(zip_path):
                os.remove(zip_path)
            raise Exception("Falha ao criar o backup do banco de dados")
        
        # 3. Cria um gerador que lê o arquivo temporário em pedaços
        def file_iterator(file_path: str):
            try:
                with open(file_path, "rb") as f:
                    while chunk := f.read(8192): # Lê em pedaços de 8KB
                        yield chunk
            finally:
                # O arquivo será limpo pela background task
                pass

        # 4. Adiciona a tarefa de limpeza para ser executada em segundo plano
        background_tasks.add_task(os.remove, zip_path)

        # 5. Retorna o StreamingResponse com o GERADOR
        return StreamingResponse(
            file_iterator(zip_path),
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename=database_backup.zip"}
        )

