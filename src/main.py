import fastapi
import hashlib

from controller import Controller
from schemas import UserModel, ServerModel
from fastapi import BackgroundTasks

app = fastapi.FastAPI()
controller_instance = Controller()

# USER

@app.post("/register")
def register_user(user: UserModel):
    success = controller_instance.register_user(user.username, user.password)
    if success:
        return {"message": "User registered successfully."}
    else:
        raise fastapi.HTTPException(status_code=400, detail="Username is already taken.")

@app.post("/login")
def login_user(user: UserModel, response: fastapi.Response):
    authenticated = controller_instance.authenticate_user(user.username, user.password)
    if authenticated:
        token = 1
        response.set_cookie(key="token", value=token)
        return {"message": "User authenticated successfully.", "token": token}
    else:
        raise fastapi.HTTPException(status_code=401, detail="Invalid username or password.")

@app.get("/user")
def get_user(request: fastapi.Request,):
    token = request.cookies.get("token")    

    if not token:
        raise fastapi.HTTPException(status_code=401, detail="Authentication required.")
    
    if token != "1":
        raise fastapi.HTTPException(status_code=401, detail="Invalid token.")
    
    return {"user": user}

@app.get("/users/count")
def count_users():
    count = controller_instance.count_users()
    return {"user_count": count}

@app.get("/user/{username}")
def get_user(username: str):
    user = controller_instance.get_user(username)
    if user:
        return {"user": user}
    else:
        raise fastapi.HTTPException(status_code=404, detail="User not found.")

@app.get("/users")
def get_users(limit: int = 10, page: int = 0):
    users_data = controller_instance.get_users_paginated(limit, page)
    return users_data

# SERVER

@app.get("/servers")
def get_servers(limit: int = 10, page: int = 0):
    server_data = controller_instance.get_servers_paginated(limit, page)
    return server_data

@app.get("/servers/count")
def count_servers():
    count = controller_instance.count_servers()
    return {"server_count": count}

@app.get("/server/{server_id}")
def get_server(server_id: str):
    server = controller_instance.get_server(server_id)
    if server:
        return {"server": server}
    else:
        raise fastapi.HTTPException(status_code=404, detail="Server not found.")

@app.post("/server/create")
def create_server(server: ServerModel):
    server_data = server.model_dump()
    message = controller_instance.create_server(server_data)
    return {"message": message}

@app.get("/server/start/{id}")
def start_server(id: str):
    message = controller_instance.start_server(id)
    return {"message": message}

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
        return {"error": "Unsupported hash type. Use MD5, SHA1, or SHA256."}
    
    return {"hash": hash_object.hexdigest()}

@app.get("/dump_database")
def dump_database(background_tasks: BackgroundTasks):
    return controller_instance.dump_database(background_tasks)