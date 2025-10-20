import faker
import random
import logging
from fastapi.testclient import TestClient
from main import app

fake = faker.Faker('pt_BR')

USERS_DATA = []
for _ in range(50):
    USERS_DATA.append({
        "username": fake.user_name(),
        "password": fake.password(length=random.randint(8, 16))
    })

SERVERS_DATA = []
for _ in range(50):
    server_types = ["Survival", "Criativo", "PvP", "Privado", "Mini-jogos", "Roleplay", "Skyblock"]
    server_type = random.choice(server_types)
    
    SERVERS_DATA.append({
        "name": f"Servidor {server_type} {fake.company()}",
        "motd": fake.text(max_nb_chars=50),
        "version": random.choice(["1.8"]),
        "slots": random.randint(10, 100),
        "difficulty": random.choice(["peaceful", "easy", "normal", "hard"]),
        "online_mode": random.choice([True, False]),
        "enable_command_block": random.choice([True, False]),
        "spawn_monsters": random.choice([True, False]),
        "force_gamemode": random.choice([True, False]),
        "gamemode": random.choice(["survival", "creative", "adventure", "spectator"]),
        "white_list": random.choice([True, False]),
        "pvp": random.choice([True, False]),
        "allow_flight": random.choice([True, False]),
        "allow_nether": random.choice([True, False]),
        "spawn_protection": random.randint(0, 32)
    })

logger = logging.getLogger(__name__)

def register_users(client: TestClient):
    """Registra usuários via TestClient"""
    logger.info("Registrando usuários...")
    success_count = 0
    
    for user in USERS_DATA:
        response = client.post("/register", json=user)
        
        if response.status_code == 200:
            logger.info(f"Usuário '{user['username']}' registrado")
            success_count += 1
        else:
            logger.warning(f"Usuário '{user['username']}' já existe ou erro: {response.status_code}")
    
    logger.info(f"Total de usuários registrados: {success_count}/{len(USERS_DATA)}")
    return success_count

def login_user(client: TestClient, username: str, password: str):
    response = client.post("/login", json={"username": username, "password": password})
    
    if response.status_code == 200:
        logger.info(f"Login realizado como '{username}'")
        return True
    else:
        logger.error(f"Falha no login de '{username}'")
        return False

def create_servers(client: TestClient):
    logger.info("Criando servidores...")
    success_count = 0
    
    for server in SERVERS_DATA:
        response = client.post("/server/create", json=server)
        
        if response.status_code == 200:
            logger.info(f"Servidor '{server['name']}' criado")
        else:
            logger.error(f"Erro ao criar servidor '{server['name']}': {response.status_code} - {response.text}")
    
    return success_count

def main():
    logger.info("Inicializando TestClient do FastAPI...")
    client = TestClient(app)
    logger.info("TestClient inicializado!")
    
    logger.info("Verificando estado inicial do banco de dados...")
    
    create_servers(client)
    register_users(client)
    logger.info("Fazendo login para teste de autenticação...")

main()