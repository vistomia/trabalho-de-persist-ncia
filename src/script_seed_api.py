"""
Script de Seed - Usando TestClient do FastAPI
Este script popula o banco de dados usando o TestClient do FastAPI,
sem precisar fazer requisições HTTP reais.
"""

from fastapi.testclient import TestClient
from main import app
import faker
import random

fake = faker.Faker('pt_BR')

# Gerar 1000 usuários
USERS_DATA = []
for _ in range(1000):
    USERS_DATA.append({
        "username": fake.user_name(),
        "password": fake.password(length=random.randint(8, 16))
    })

# Gerar 1000 servidores
SERVERS_DATA = []
for _ in range(1000):
    server_types = ["Survival", "Criativo", "PvP", "Privado", "Mini-jogos", "Roleplay", "Skyblock"]
    server_type = random.choice(server_types)
    
    SERVERS_DATA.append({
        "name": f"Servidor {server_type} {fake.company()}",
        "motd": fake.text(max_nb_chars=50),
        "version": random.choice(["1.8.9", "1.19.4", "1.20.1", "1.20.2"]),
        "slots": random.randint(10, 100),
        "difficulty": random.choice(["peaceful", "easy", "normal", "hard"]),
        "online_mode": random.choice([True, False]),
        "gamemode": random.choice(["survival", "creative", "adventure", "spectator"]),
        "pvp": random.choice([True, False]),
        "spawn_monsters": random.choice([True, False]),
        "allow_flight": random.choice([True, False]),
        "force_gamemode": random.choice([True, False]),
        "white_list": random.choice([True, False]),
        "enable_command_block": random.choice([True, False]),
        "allow_nether": random.choice([True, False]),
        "spawn_protection": random.randint(0, 32)
    })


# Cores para output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(message):
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")

def print_error(message):
    print(f"{Colors.RED}✗ {message}{Colors.END}")

def print_info(message):
    print(f"{Colors.BLUE}ℹ {message}{Colors.END}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")


def register_users(client: TestClient):
    """Registra usuários via TestClient"""
    print_info("Registrando usuários...")
    success_count = 0
    
    for user in USERS_DATA:
        response = client.post("/register", json=user)
        
        if response.status_code == 200:
            print_success(f"Usuário '{user['username']}' registrado")
            success_count += 1
        else:
            print_warning(f"Usuário '{user['username']}' já existe ou erro: {response.status_code}")
    
    print_info(f"Total de usuários registrados: {success_count}/{len(USERS_DATA)}\n")
    return success_count


def login_user(client: TestClient, username: str, password: str):
    """Faz login usando TestClient"""
    response = client.post("/login", json={"username": username, "password": password})
    
    if response.status_code == 200:
        print_success(f"Login realizado como '{username}'")
        return True
    else:
        print_error(f"Falha no login de '{username}'")
        return False


def create_servers(client: TestClient):
    """Cria servidores via TestClient"""
    print_info("Criando servidores...")
    success_count = 0
    
    for server in SERVERS_DATA:
        response = client.post("/server/create", json=server)
        
        if response.status_code == 200:
            print_success(f"Servidor '{server['name']}' criado")
            success_count += 1
        else:
            print_error(f"Erro ao criar servidor '{server['name']}': {response.status_code} - {response.text}")
    
    print_info(f"Total de servidores criados: {success_count}/{len(SERVERS_DATA)}\n")
    return success_count


def list_users(client: TestClient):
    """Lista todos os usuários"""
    response = client.get("/users")
    
    if response.status_code == 200:
        users = response.json()["users"]
        print_success(f"Total de usuários no banco: {len(users)}")
        # Mostra apenas os primeiros 10 para não poluir o terminal
        for user in users[:10]:
            print(f"  - {user['username']}")
        if len(users) > 10:
            print(f"  ... e mais {len(users) - 10} usuários")
        return users
    else:
        print_error(f"Erro ao listar usuários: {response.status_code}")
        return []


def list_servers(client: TestClient):
    """Lista todos os servidores"""
    response = client.get("/servers")
    
    if response.status_code == 200:
        servers = response.json()["servers"]
        print_success(f"Total de servidores no banco: {len(servers)}")
        # Mostra apenas os primeiros 10 para não poluir o terminal
        for server in servers[:10]:
            print(f"  - {server['name']} (ID: {server.get('id', 'N/A')})")
        if len(servers) > 10:
            print(f"  ... e mais {len(servers) - 10} servidores")
        return servers
    else:
        print_error(f"Erro ao listar servidores: {response.status_code}")
        return []


def test_hash_endpoint(client: TestClient):
    """Testa o endpoint de hash"""
    print_info("\nTestando endpoint de hash...")
    test_data = "teste123"
    
    for hash_type in ["md5", "sha1", "sha256"]:
        response = client.get(f"/hash/{hash_type}/{test_data}")
        if response.status_code == 200:
            hash_value = response.json()["hash"]
            print_success(f"{hash_type.upper()}: {hash_value}")
        else:
            print_error(f"Erro ao calcular {hash_type}")


def get_counts(client: TestClient):
    """Obtém contagem de usuários e servidores"""
    user_count_response = client.get("/users/count")
    server_count_response = client.get("/servers/count")
    
    user_count = user_count_response.json().get("user_count", 0) if user_count_response.status_code == 200 else 0
    server_count = server_count_response.json().get("server_count", 0) if server_count_response.status_code == 200 else 0
    
    return user_count, server_count


def main():
    """Função principal do script de seed"""
    print("\n" + "="*60)
    print("  SCRIPT DE SEED - USANDO TESTCLIENT DO FASTAPI")
    print("="*60 + "\n")
    
    # Cria o TestClient
    print_info("Inicializando TestClient do FastAPI...")
    client = TestClient(app)
    print_success("TestClient inicializado!\n")
    
    # Verifica estado inicial
    print_info("Verificando estado inicial do banco de dados...")
    initial_users, initial_servers = get_counts(client)
    print_info(f"Usuários existentes: {initial_users}")
    print_info(f"Servidores existentes: {initial_servers}\n")
    
    # Registra usuários
    users_created = register_users(client)
    
    # Faz login com o primeiro usuário para teste
    print_info("Fazendo login para teste de autenticação...")
    login_user(client, USERS_DATA[0]["username"], USERS_DATA[0]["password"])
    print()
    
    # Cria servidores
    servers_created = create_servers(client)
    
    # Lista usuários
    print_info("\nListando usuários cadastrados:")
    list_users(client)
    print()
    
    # Lista servidores
    print_info("\nListando servidores cadastrados:")
    list_servers(client)
    
    # Testa endpoint de hash
    test_hash_endpoint(client)
    
    # Verifica estado final
    print_info("\nVerificando estado final do banco de dados...")
    final_users, final_servers = get_counts(client)
    print_info(f"Total de usuários: {final_users}")
    print_info(f"Total de servidores: {final_servers}")
    
    # Resumo final
    print("\n" + "="*60)
    print("  RESUMO DO SEED")
    print("="*60)
    print_info(f"Usuários novos: {users_created}")
    print_info(f"Servidores novos: {servers_created}")
    print_info(f"Total de usuários no banco: {final_users}")
    print_info(f"Total de servidores no banco: {final_servers}")
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_warning("\n\nScript interrompido pelo usuário")
    except Exception as e:
        print_error(f"\n\nErro inesperado: {e}")
        import traceback
        traceback.print_exc()
