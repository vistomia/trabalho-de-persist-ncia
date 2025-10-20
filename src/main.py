import fastapi
import hashlib

from controller import Controller
from schemas import UserModel, ServerModel
from fastapi import BackgroundTasks

app = fastapi.FastAPI()
controller_instance = Controller()

# Endpoints do User

@app.post("/register")
def register_user(user: UserModel):
    success = controller_instance.register_user(user.username, user.password)
    if success:
        return {"message": "Usuário registrado com sucesso."}
    else:
        raise fastapi.HTTPException(status_code=400, detail="Erro na senha ou usuario.")

@app.post("/login")
def login_user(user: UserModel, response: fastapi.Response):
    authenticated = controller_instance.authenticate_user(user.username, user.password)
    if authenticated:
        token = 1
        response.set_cookie(key="token", value=token)
        return {"message": "Usuário autenticado com sucesso.", "token": token}
    else:
        raise fastapi.HTTPException(status_code=401, detail="Nome de usuário ou senha inválidos.")

@app.get("/users/count")
def count_users():
    count = controller_instance.count_users()
    if count is None:
        raise fastapi.HTTPException(status_code=500, detail="Erro ao contar usuários.")
    return {"user_count": count}

@app.get("/user/{username}")
def get_user(username: str):
    user = controller_instance.get_user(username)
    if user:
        return {"user": user}
    else:
        raise fastapi.HTTPException(status_code=404, detail="Usuário não encontrado.")

@app.get("/users")
def get_users(limit: int = 10, page: int = 0):
    users_data = controller_instance.get_users_paginated(limit, page)
    if users_data is None:
        raise fastapi.HTTPException(status_code=500, detail="Erro ao buscar usuários.")
    return users_data

@app.delete("/user/{username}")
def delete_user(username: str):
    try:
        message = controller_instance.delete_user(username)
        return {"message": message}
    except Exception as e:
        raise fastapi.HTTPException(status_code=500, detail="Erro ao deletar usuário.")

@app.delete("/server/{server_id}")
def delete_server(server_id: str):
    try:
        message = controller_instance.delete_server(server_id)
        return {"message": message}
    except Exception as e:
        raise fastapi.HTTPException(status_code=500, detail="Erro ao deletar servidor.")

# Endpoints do  Server

@app.get("/servers")
def get_servers(limit: int = 10, page: int = 0):
    server_data = controller_instance.get_servers_paginated(limit, page)
    if server_data is None:
        raise fastapi.HTTPException(status_code=500, detail="Erro ao buscar servidores.")
    return server_data

@app.get("/servers/count")
def count_servers():
    count = controller_instance.count_servers()
    if count is None:
        raise fastapi.HTTPException(status_code=500, detail="Erro ao contar servidores.")
    return {"server_count": count}

@app.get("/server/{server_id}")
def get_server(server_id: str):
    server = controller_instance.get_server(server_id)
    if server:
        return {"server": server}
    else:
        raise fastapi.HTTPException(status_code=404, detail="Servidor não encontrado.")

@app.post("/server/create")
def create_server(server: ServerModel):
    try:
        server_data = server.model_dump()
        message = controller_instance.create_server(server_data)
        return {"message": message}
    except Exception as e:
        raise fastapi.HTTPException(status_code=500, detail="Erro ao criar servidor.")

@app.get("/server/start/{id}")
def start_server(id: str):
    try:
        message = controller_instance.start_server(id)
        if "erro" in message.lower() or "falha" in message.lower():
            raise fastapi.HTTPException(status_code=500, detail=message)
        return {"message": message}
    except Exception as e:
        raise fastapi.HTTPException(status_code=500, detail="Erro ao iniciar servidor.")

# Aquele endpoint do hash

@app.get("/hash/{hash_name}/{data}")
def compute_hash(hash_name: str, data: str):
    hash_name = hash_name.lower()
    if hash_name == "md5":
        hash_object = hashlib.md5(data.encode())
    elif hash_name == "sha1":
        hash_object = hashlib.sha1(data.encode())
    elif hash_name == "sha256":
        hash_object = hashlib.sha256(data.encode())
    else:
        raise fastapi.HTTPException(status_code=400, detail="Erro. Use MD5, SHA1, ou SHA256.")
    
    return {"hash": hash_object.hexdigest()}

@app.delete("/server/{server_id}")
def delete_server(server_id: str):
    try:
        message = controller_instance.delete_server(server_id)
        return {"message": message}
    except Exception as e:
        raise fastapi.HTTPException(status_code=500, detail="Erro ao deletar servidor.")

# Endpoints do banco de dados

@app.get("/dump_database")
def dump_database(background_tasks: BackgroundTasks):
    return controller_instance.dump_database(background_tasks)

@app.get("/vacuum_users")
def vacuum_users():
    if controller_instance.vacuum_users():
        return {"message": "User database vacuumed successfully."}
    else:
        raise fastapi.HTTPException(status_code=500, detail="Falha ao vacuum user database.")

@app.get("/vacuum_servers")
def vacuum_servers():
    if controller_instance.vacuum_servers():
        return {"message": "Server database vacuumed successfully."}
    else:
        raise fastapi.HTTPException(status_code=500, detail="Falha ao vacuum server database.")
