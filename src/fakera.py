from fakera import Faker
import random

fake = Faker('pt_BR')

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
        "allow_flight": random.choice([True, False]) if random.random() > 0.5 else None,
        "force_gamemode": random.choice([True, False]) if random.random() > 0.7 else None,
        "white_list": random.choice([True, False]) if random.random() > 0.8 else None,
    })
