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
    
    def validate_token(self, token: str) -> bool:
        for user in self.get_all_users():
            expected_token = hashlib.md5(f"{user['username']}{hash(user['password_hash'])}".encode()).hexdigest()
            if token == expected_token:
                return True
        return False
    
    def server_exists(self, server_id: str) -> bool:
        return core.server.Server.server_exists(server_id)
    
    def server_repo(self):
        return data.database.Server()

    def dump_database(self, background_tasks: BackgroundTasks):
        """Cria um backup usando dump.py, compacta em um arquivo temporário e faz o stream dele."""
        
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

    def create_server(self, server_data: dict) -> str:
        self.server_repo.insert(server_data)
        return f"created successfully."
    
    def start_server(self, server_id: str) -> str:
        properties = self.server_repo.get_server_properties(server_id)
        print(properties)
        core.server.Server(server_id, properties)
        if core.server.Server.server_exists(server_id):
            with core.server.Server(server_id) as server:
                server.run_core()
        else:
            with core.server.Server(server_id) as server:
                server.download_server_jar()
                server.eula()
                server.run_core()
