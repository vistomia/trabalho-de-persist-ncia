from fastapi import FastAPI
from contextlib import asynccontextmanager
from routers import home, java_links, minecraft_maps, server_operators, servers, servers_properties, softwares, users
from database import init_db, close_db
from fastapi_pagination import add_pagination
import time
import logging
import custom_logger
import asyncio
import random
from datetime import datetime, timedelta
from database import init_db, close_db
from models.users import User
from models.java_links import Java
from models.softwares import Softwares
from models.servers_properties import ServersProperties
from models.servers_properties import ServersProperties
from models.minecraft_maps import MinecraftMap
from models.servers import Server
from models.operators import Operator
import logging
import custom_logger

logger = logging.getLogger(__name__)

async def clear_collections():
    """Limpar todas as coleções antes de popular"""
    logger.info("Limpando coleções existentes...")
    
    await User.delete_all()
    await Java.delete_all()
    await Softwares.delete_all()
    await ServersProperties.delete_all()
    await MinecraftMap.delete_all()
    await Server.delete_all()
    await Operator.delete_all()
    
    logger.info("Coleções limpas com sucesso!")

async def populate_users():
    """Criar 10 usuários"""
    logger.info("Criando usuários...")
    
    users_data = [
        {"username": "admin", "email": "admin@alternos.com", "password": "admin123"},
        {"username": "moderator", "email": "moderator@alternos.com", "password": "mod123"},
        {"username": "player1", "email": "player1@gmail.com", "password": "player123"},
        {"username": "gamer_pro", "email": "gamer@hotmail.com", "password": "gamer456"},
        {"username": "minecraft_fan", "email": "mcfan@yahoo.com", "password": "minecraft789"},
        {"username": "builder_master", "email": "builder@outlook.com", "password": "build123"},
        {"username": "redstone_guru", "email": "redstone@gmail.com", "password": "redstone456"},
        {"username": "pvp_king", "email": "pvp@gmail.com", "password": "pvp789"},
        {"username": "creative_soul", "email": "creative@hotmail.com", "password": "creative123"},
        {"username": "survival_expert", "email": "survival@yahoo.com", "password": "survival456"},
        {"username": "enderdragon", "email": "enderdragon@gmail.com", "password": "dragon123"},
        {"username": "nether_explorer", "email": "nether@outlook.com", "password": "nether456"},
        {"username": "ocean_guardian", "email": "ocean@yahoo.com", "password": "ocean789"},
        {"username": "sky_warrior", "email": "sky@gmail.com", "password": "sky123"},
        {"username": "cave_dweller", "email": "cave@hotmail.com", "password": "cave456"},
        {"username": "forest_ranger", "email": "forest@outlook.com", "password": "forest789"},
        {"username": "desert_nomad", "email": "desert@gmail.com", "password": "desert123"},
        {"username": "ice_walker", "email": "ice@yahoo.com", "password": "ice456"},
        {"username": "lava_jumper", "email": "lava@hotmail.com", "password": "lava789"},
        {"username": "block_breaker", "email": "breaker@outlook.com", "password": "breaker123"},
        {"username": "enchant_master", "email": "enchant@gmail.com", "password": "enchant456"},
        {"username": "potion_brewer", "email": "potion@yahoo.com", "password": "potion789"},
        {"username": "mob_hunter", "email": "hunter@hotmail.com", "password": "hunter123"},
        {"username": "farm_owner", "email": "farm@outlook.com", "password": "farm456"},
        {"username": "castle_lord", "email": "castle@gmail.com", "password": "castle789"},
        {"username": "village_chief", "email": "village@yahoo.com", "password": "village123"},
        {"username": "treasure_seeker", "email": "treasure@hotmail.com", "password": "treasure456"},
        {"username": "dimension_hopper", "email": "dimension@outlook.com", "password": "dimension789"},
        {"username": "pixel_artist", "email": "pixel@gmail.com", "password": "pixel123"},
        {"username": "server_admin", "email": "serveradmin@yahoo.com", "password": "serveradmin456"}
    ]
    
    users = []
    for data in users_data:
        user = User(**data)
        await user.insert()
        users.append(user)
    
    logger.info(f"{len(users)} usuários criados com sucesso!")
    return users

async def populate_java_versions():
    """Criar 10 versões Java"""
    logger.info("Criando versões Java...")
    
    java_data = [
        {"name": "OpenJDK 8", "version": "8", "link": "https://openjdk.java.net/install/"},
        {"name": "OpenJDK 11", "version": "11", "link": "https://jdk.java.net/11/"},
        {"name": "OpenJDK 17", "version": "17", "link": "https://jdk.java.net/17/"},
        {"name": "OpenJDK 21", "version": "21", "link": "https://jdk.java.net/21/"},
        {"name": "Oracle JDK 8", "version": "8u401", "link": "https://www.oracle.com/java/technologies/javase/javase8-archive-downloads.html"},
        {"name": "Oracle JDK 11", "version": "11.0.22", "link": "https://www.oracle.com/java/technologies/javase/jdk11-archive-downloads.html"},
        {"name": "Oracle JDK 17", "version": "17.0.10", "link": "https://www.oracle.com/java/technologies/javase/jdk17-archive-downloads.html"},
        {"name": "Azul Zulu 8", "version": "8.76.0.17", "link": "https://www.azul.com/downloads/?version=java-8-lts"},
        {"name": "Azul Zulu 11", "version": "11.70.15", "link": "https://www.azul.com/downloads/?version=java-11-lts"},
        {"name": "Azul Zulu 17", "version": "17.50.19", "link": "https://www.azul.com/downloads/?version=java-17-lts"}
    ]
    
    java_versions = []
    for data in java_data:
        java = Java(**data)
        await java.insert()
        java_versions.append(java)
    
    logger.info(f"{len(java_versions)} versões Java criadas com sucesso!")
    return java_versions

async def populate_softwares():
    """Criar 10 softwares"""
    logger.info("Criando softwares...")
    
    softwares_data = [
        {"name": "Vanilla", "version": "1.20.4", "link": "https://launcher.mojang.com/v1/objects/8dd1a28015f51b1803213892b50b7b4fc76931d4/server.jar", "plugins_enabled": False, "mods_enabled": False},
        {"name": "Paper", "version": "1.20.4", "link": "https://api.papermc.io/v2/projects/paper/versions/1.20.4/builds/497/downloads/paper-1.20.4-497.jar", "plugins_enabled": True, "mods_enabled": False},
        {"name": "Spigot", "version": "1.20.4", "link": "https://hub.spigotmc.org/jenkins/job/BuildTools/lastSuccessfulBuild/artifact/target/BuildTools.jar", "plugins_enabled": True, "mods_enabled": False},
        {"name": "Bukkit", "version": "1.20.4", "link": "https://hub.spigotmc.org/jenkins/job/BuildTools/lastSuccessfulBuild/artifact/target/BuildTools.jar", "plugins_enabled": True, "mods_enabled": False},
        {"name": "Forge", "version": "1.20.4", "link": "https://maven.minecraftforge.net/net/minecraftforge/forge/1.20.4-49.0.50/forge-1.20.4-49.0.50-installer.jar", "plugins_enabled": False, "mods_enabled": True},
        {"name": "Fabric", "version": "1.20.4", "link": "https://meta.fabricmc.net/v2/versions/loader/1.20.4/0.15.6/1.0.0/server/jar", "plugins_enabled": False, "mods_enabled": True},
        {"name": "Quilt", "version": "1.20.4", "link": "https://maven.quiltmc.org/repository/release/org/quiltmc/quilt-loader/0.24.0/quilt-loader-0.24.0.jar", "plugins_enabled": False, "mods_enabled": True},
        {"name": "Purpur", "version": "1.20.4", "link": "https://api.purpurmc.org/v2/purpur/1.20.4/latest/download", "plugins_enabled": True, "mods_enabled": False},
        {"name": "Pufferfish", "version": "1.20.4", "link": "https://ci.pufferfish.host/job/Pufferfish-1.20/lastSuccessfulBuild/artifact/build/libs/pufferfish-paperclip-1.20.4-R0.1-SNAPSHOT-reobf.jar", "plugins_enabled": True, "mods_enabled": False},
        {"name": "Airplane", "version": "1.17.1", "link": "https://github.com/TECHNOVE/Airplane/releases/download/v1.17.1-10/airplane-paperclip-1.17.1-R0.1-SNAPSHOT-reobf.jar", "plugins_enabled": True, "mods_enabled": False}
    ]
    
    softwares = []
    for data in softwares_data:
        software = Softwares(**data)
        await software.insert()
        softwares.append(software)
    
    logger.info(f"{len(softwares)} softwares criados com sucesso!")
    return softwares

async def populate_server_properties():
    """Criar 10 configurações de servidor"""
    logger.info("Criando propriedades de servidor...")
    
    properties_data = [
        {"level_name": "world", "gamemode": "survival", "difficulty": "easy", "max_players": 20, "motd": "Servidor de Sobrevivência"},
        {"level_name": "creative_world", "gamemode": "creative", "difficulty": "peaceful", "max_players": 50, "motd": "Servidor Criativo"},
        {"level_name": "pvp_arena", "gamemode": "adventure", "difficulty": "hard", "max_players": 100, "motd": "Arena PvP", "hardcore": True},
        {"level_name": "skyblock", "gamemode": "survival", "difficulty": "normal", "max_players": 30, "motd": "SkyBlock Challenge"},
        {"level_name": "prison", "gamemode": "survival", "difficulty": "normal", "max_players": 80, "motd": "Servidor Prison"},
        {"level_name": "factions", "gamemode": "survival", "difficulty": "hard", "max_players": 150, "motd": "Factions War"},
        {"level_name": "minigames", "gamemode": "adventure", "difficulty": "easy", "max_players": 200, "motd": "Hub de Minigames"},
        {"level_name": "roleplay", "gamemode": "adventure", "difficulty": "normal", "max_players": 60, "motd": "Roleplay Medieval"},
        {"level_name": "anarchy", "gamemode": "survival", "difficulty": "hard", "max_players": 40, "motd": "Anarquia Total"},
        {"level_name": "modded_world", "gamemode": "survival", "difficulty": "normal", "max_players": 25, "motd": "Servidor Modded"}
    ]
    
    server_properties = []
    for data in properties_data:
        props = ServersProperties(**data)
        await props.insert()
        server_properties.append(props)
    
    logger.info(f"{len(server_properties)} propriedades de servidor criadas com sucesso!")
    return server_properties

async def populate_minecraft_maps():
    """Criar 10 mapas"""
    logger.info("Criando mapas do Minecraft...")
    
    maps_data = [
        {"name": "Spawn Moderno", "description": "Um spawn moderno com prédios e áreas comerciais", "link": "https://www.planetminecraft.com/project/modern-spawn/", "size_mb": 25.5, "world_type": "survival"},
        {"name": "Castelo Medieval", "description": "Grande castelo medieval com vila ao redor", "link": "https://www.planetminecraft.com/project/medieval-castle/", "size_mb": 45.2, "world_type": "creative"},
        {"name": "Arena PvP", "description": "Arena circular para combates PvP", "link": "https://www.planetminecraft.com/project/pvp-arena/", "size_mb": 12.8, "world_type": "adventure"},
        {"name": "Cidade Futurística", "description": "Cidade com arquitetura futurística e arranha-céus", "link": "https://www.planetminecraft.com/project/futuristic-city/", "size_mb": 78.9, "world_type": "creative"},
        {"name": "Ilha Tropical", "description": "Ilha paradisíaca com praias e palmeiras", "link": "https://www.planetminecraft.com/project/tropical-island/", "size_mb": 32.1, "world_type": "survival"},
        {"name": "Base Militar", "description": "Complexo militar com hangares e veículos", "link": "https://www.planetminecraft.com/project/military-base/", "size_mb": 56.7, "world_type": "adventure"},
        {"name": "Parque de Diversões", "description": "Parque temático com montanha-russa e brinquedos", "link": "https://www.planetminecraft.com/project/theme-park/", "size_mb": 89.3, "world_type": "creative"},
        {"name": "Dungeon das Trevas", "description": "Masmorra sombria cheia de desafios", "link": "https://www.planetminecraft.com/project/dark-dungeon/", "size_mb": 18.6, "world_type": "adventure"},
        {"name": "Fazenda Automática", "description": "Complexo de fazendas automáticas de recursos", "link": "https://www.planetminecraft.com/project/auto-farms/", "size_mb": 41.4, "world_type": "survival"},
        {"name": "Laboratório Científico", "description": "Laboratório moderno com equipamentos de pesquisa", "link": "https://www.planetminecraft.com/project/science-lab/", "size_mb": 35.8, "world_type": "creative"}
    ]
    
    maps = []
    for data in maps_data:
        map_obj = MinecraftMap(**data)
        await map_obj.insert()
        maps.append(map_obj)
    
    logger.info(f"{len(maps)} mapas criados com sucesso!")
    return maps

async def populate_servers(users, java_versions, softwares, server_properties, maps):
    """Criar 10 servidores"""
    logger.info("Criando servidores...")
    
    server_names = [
        "AlternosCraft", "SurvivalPro", "CreativeHub", "PvPArena", "SkyBlockWorld",
        "PrisonBreak", "FactionsWar", "MinigamesCenter", "RoleplayMedieval", "AnarchyLands"
    ]
    
    servers = []
    for i, name in enumerate(server_names):
        # Distribuir recursos entre os servidores
        owner = users[i % len(users)]
        java = java_versions[i % len(java_versions)]
        software = softwares[i % len(softwares)]
        props = server_properties[i % len(server_properties)]
        map_obj = maps[i % len(maps)] if random.choice([True, False]) else None
        
        server_data = {
            "name": name,
            "owner_id": owner.id,
            "server_properties_id": props.id,
            "software_id": software.id,
            "java_id": java.id,
            "status": random.choice(["online", "offline", "maintenance"]),
            "ip_address": f"192.168.1.{100 + i}",
            "port": 25565 + i
        }
        
        if map_obj:
            server_data["map_id"] = map_obj.id
        
        server = Server(**server_data)
        await server.insert()
        servers.append(server)
    
    logger.info(f"{len(servers)} servidores criados com sucesso!")
    return servers

async def populate_operators(users, servers):
    """Criar operadores para os servidores"""
    logger.info("Criando operadores...")
    
    operators = []
    permission_levels = ["admin", "moderator", "helper"]
    
    # Garantir que cada servidor tenha pelo menos 1 operador
    for server in servers:
        # Admin principal (dono do servidor)
        admin_op = Operator(
            server_id=server.id,
            user_id=server.owner_id,
            permission_level="admin",
            granted_by=server.owner_id
        )
        await admin_op.insert()
        operators.append(admin_op)
        
        # Adicionar 1-3 operadores aleatórios
        num_operators = random.randint(1, 3)
        available_users = [u for u in users if u.id != server.owner_id]
        
        for _ in range(num_operators):
            if not available_users:
                break
            
            user = random.choice(available_users)
            available_users.remove(user)
            
            operator = Operator(
                server_id=server.id,
                user_id=user.id,
                permission_level=random.choice(permission_levels),
                granted_by=server.owner_id
            )
            await operator.insert()
            operators.append(operator)
    
    logger.info(f"{len(operators)} operadores criados com sucesso!")
    return operators

async def main():
    try:
        logger.info("Iniciando populate do MongoDB...")
        
        await init_db()
        await clear_collections()
        
        users = await populate_users()
        java_versions = await populate_java_versions()
        softwares = await populate_softwares()
        server_properties = await populate_server_properties()
        maps = await populate_minecraft_maps()
        servers = await populate_servers(users, java_versions, softwares, server_properties, maps)
        operators = await populate_operators(users, servers)
        
        logger.info(f"Usuários: {len(users)}")
        logger.info(f"Versões Java: {len(java_versions)}")
        logger.info(f"Softwares: {len(softwares)}")
        logger.info(f"Propriedades: {len(server_properties)}")
        logger.info(f"Mapas: {len(maps)}")
        logger.info(f"Servidores: {len(servers)}")
        logger.info(f"Operadores: {len(operators)}")
        total_docs = len(users) + len(java_versions) + len(softwares) + len(server_properties) + len(maps) + len(servers) + len(operators)
        logger.info(f"Total de documentos criados: {total_docs}")
        
    except Exception as e:
        logger.error(f"E: {str(e)}")
        raise
    finally:
        # Fechar conexão
        await close_db()

if __name__ == "__main__":
    asyncio.run(main())