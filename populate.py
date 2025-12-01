import fastapi
from routers import user
from database import database
from sqlmodel import SQLModel, Session, select, MetaData, insert
from models.user import User
from models.map import Map
from models.operator import Operator
from models.java import Java
from models.server_properties import ServerProperties
from models.software import Software
from models.server import Server
from datetime import datetime
import os
from dotenv import load_dotenv

app = fastapi.FastAPI()
app.include_router(user.router)

load_dotenv()

db = database.Database(uri=os.getenv('DATABASE_URL', 'sqlite:///data.sqlite'))
engine = db.get_engine()
metadata = MetaData()

SQLModel.metadata.create_all(engine)

metadata.create_all(engine)

with Session(engine) as session:
    statement = select(User).limit(1)
    result = session.exec(statement).first()
    
    if True:
        print("Table is empty. Inserting sample data...")
        
        users_to_add = [
            User(username="alice", email="alice@example.com", password="password123"),
            User(username="bob", email="bob@example.com", password="password123"),
            User(username="carol", email="carol@example.com", password="password123"),
            User(username="david", email="david@example.com", password="password123"),
            User(username="eve", email="eve@example.com", password="password123"),
            User(username="frank", email="frank@example.com", password="password123"),
            User(username="grace", email="grace@example.com", password="password123"),
            User(username="henry", email="henry@example.com", password="password123"),
            User(username="iris", email="iris@example.com", password="password123"),
            User(username="jack", email="jack@example.com", password="password123"),
            User(username="kate", email="kate@example.com", password="password123"),
            User(username="liam", email="liam@example.com", password="password123"),
            User(username="mia", email="mia@example.com", password="password123"),
            User(username="noah", email="noah@example.com", password="password123"),
            User(username="olivia", email="olivia@example.com", password="password123"),
            User(username="peter", email="peter@example.com", password="password123"),
            User(username="quinn", email="quinn@example.com", password="password123"),
            User(username="ruby", email="ruby@example.com", password="password123"),
            User(username="sam", email="sam@example.com", password="password123"),
            User(username="tina", email="tina@example.com", password="password123")
        ]
        
        java_instances = [
            Java(name="OpenJDK 8", link="https://openjdk.java.net/projects/jdk8/"),
            Java(name="OpenJDK 11", link="https://download.java.net/java/GA/jdk11/13/GPL/openjdk-11.0.1_linux-x64_bin.tar.gz"),
            Java(name="OpenJDK 17", link="https://download.java.net/java/GA/jdk17.0.1/2a2082e5a09d4267845be086888add4f/12/GPL/openjdk-17.0.1_linux-x64_bin.tar.gz"),
            Java(name="OpenJDK 20", link="https://download.java.net/java/GA/jdk20.0.2/6e380f22cbe7469fa75fb448bd903d8e/9/GPL/openjdk-20.0.2_linux-x64_bin.tar.gz"),
            Java(name="OpenJDK 21", link="https://download.java.net/java/GA/jdk21.0.2/f2283984656d49d69e91c558476027ac/13/GPL/openjdk-21.0.2_linux-x64_bin.tar.gz"),
            Java(name="OpenJDK 22", link="https://download.java.net/java/GA/jdk22.0.2/c9ecb94cd31b495da20a27d4581645e8/9/GPL/openjdk-22.0.2_linux-x64_bin.tar.gz"),
            Java(name="OpenJDK 23", link="https://download.java.net/java/GA/jdk23.0.2/6da2a6609d6e406f85c491fcb119101b/7/GPL/openjdk-23.0.2_linux-x64_bin.tar.gz"),
            Java(name="OpenJDK 24", link="https://download.java.net/java/GA/jdk24.0.2/fdc5d0102fe0414db21410ad5834341f/12/GPL/openjdk-24.0.2_linux-x64_bin.tar.gz"),
            Java(name="OpenJDK 25", link="https://download.java.net/java/GA/jdk25.0.1/2fbf10d8c78e40bd87641c434705079d/8/GPL/openjdk-25.0.1_linux-x64_bin.tar.gz"),
            Java(name="TemurinJDK", link="https://adoptium.net/pt-BR/download?link=https%3A%2F%2Fgithub.com%2Fadoptium%2Ftemurin25-binaries%2Freleases%2Fdownload%2Fjdk-25.0.1%252B8%2FOpenJDK25U-jdk_x64_linux_hotspot_25.0.1_8.tar.gz&vendor=Adoptium")
        ]
        
        server_properties = [
            ServerProperties(difficulty="easy", max_players=20, gamemode="survival", motd="Welcome to Server 1"),
            ServerProperties(difficulty="normal", max_players=50, gamemode="creative", motd="Creative Server"),
            ServerProperties(difficulty="hard", max_players=30, gamemode="adventure", motd="Adventure Awaits"),
            ServerProperties(difficulty="peaceful", max_players=10, gamemode="spectator", motd="Peaceful World"),
            ServerProperties(difficulty="normal", max_players=100, gamemode="survival", motd="Mega Server"),
            ServerProperties(difficulty="easy", max_players=15, gamemode="creative", motd="Build Your Dreams"),
            ServerProperties(difficulty="hard", max_players=40, gamemode="survival", motd="Hardcore Survival"),
            ServerProperties(difficulty="normal", max_players=25, gamemode="adventure", motd="Quest Server"),
            ServerProperties(difficulty="peaceful", max_players=60, gamemode="creative", motd="Relaxed Building"),
            ServerProperties(difficulty="easy", max_players=80, gamemode="survival", motd="Community Server")
        ]
        
        software_instances = [
            Software(name="Vanilla", link="https://magmafoundation.org/api/versions/21.1.47-beta/download?type=installer", version="1.8.0", plugins_enabled=True, mods_enabled=True),
            Software(name="Vanilla", link="https://minecraft.net", version="1.20.1", plugins_enabled=False, mods_enabled=False),
            Software(name="Paper", link="https://fill-data.papermc.io/v1/objects/a61a0585e203688f606ca3a649760b8ba71efca01a4af7687db5e41408ee27aa/paper-1.21.10-117.jar", version="1.20.1", plugins_enabled=True, mods_enabled=False),
            Software(name="Folia", link="https://fill-data.papermc.io/v1/objects/233843cfd5001b6f658fcab549178d694cc37f0277d004ea295de0a94c57278f/folia-1.21.8-6.jar", version="1.21.8", plugins_enabled=True, mods_enabled=False),
            Software(name="Magma", link="https://magmafoundation.org/api/versions/21.1.47-beta/download?type=installer", version="1.21.x", plugins_enabled=True, mods_enabled=True),
            Software(name="Forge", link="https://files.minecraftforge.net", version="1.20.1", plugins_enabled=False, mods_enabled=True),
            Software(name="Fabric", link="https://meta.fabricmc.net/v2/versions/loader/1.21.10/0.18.1/1.1.0/server/jar", version="1.21.10", plugins_enabled=False, mods_enabled=True),
            Software(name="Spigot", link="https://www.spigotmc.org", version="1.20.1", plugins_enabled=True, mods_enabled=False),
            Software(name="Magma", link="https://magmafoundation.org/api/versions/21.1.47-beta/download?type=installer", version="1.21.x", plugins_enabled=True, mods_enabled=True),
            Software(name="NeoForge", link="https://magmafoundation.org/api/versions/21.1.47-beta/download?type=installer", version="1.21.x", plugins_enabled=True, mods_enabled=True),
        ]

        map_instances = [
            Map(name="Parkour", description="A challenging parkour course with jumps, obstacles, and time trials", link="https://minecraft.wiki/w/Overworld"),
            Map(name="Eggwars", description="Team-based PvP map where players protect their egg while destroying others", link="https://minecraft.wiki/w/The_Nether"),
            Map(name="Challenge", description="An adventure map filled with puzzles, quests, and combat challenges", link="https://minecraft.wiki/w/The_End"),
            Map(name="Bedrock", description="A survival map set in an underground cavern system with limited resources", link="https://example.com/custom"),
            Map(name="Skyblock", description="Classic survival challenge starting on a small floating island in the void", link="https://example.com/skyblock"),
            Map(name="Prison", description="Escape-themed map where players must break out of a maximum security prison", link="https://example.com/prison"),
            Map(name="Murder Mystery", description="Social deduction game where players must find the murderer among them", link="https://example.com/murder-mystery"),
            Map(name="Build Battle", description="Creative competition map where teams compete to build the best structures", link="https://example.com/build-battle"),
            Map(name="Survival Games", description="Battle royale style map with weapons, supplies, and shrinking play area", link="https://example.com/survival-games"),
            Map(name="Maze Runner", description="Complex labyrinth map with traps, secrets, and multiple escape routes", link="https://example.com/maze-runner")
        ]
        
        for user in users_to_add:
            session.add(user)
        for java in java_instances:
            session.add(java)
        for props in server_properties:
            session.add(props)
        for software in software_instances:
            session.add(software)
        for map_inst in map_instances:
            session.add(map_inst)
            
        session.commit()
        
        server_instances = [
            Server(name="Survival Server", owner_id=1, server_properties_id=1, software_id=1, java_id=1),
            Server(name="Creative Server", owner_id=2, server_properties_id=2, software_id=2, java_id=2),
            Server(name="Adventure Server", owner_id=3, server_properties_id=3, software_id=3, java_id=3),
            Server(name="Peaceful Server", owner_id=4, server_properties_id=4, software_id=4, java_id=4),
            Server(name="Mega Server", owner_id=5, server_properties_id=5, software_id=5, java_id=5),
            Server(name="Build World", owner_id=6, server_properties_id=5, software_id=5, java_id=5),
            Server(name="PvP Arena", owner_id=7, server_properties_id=5, software_id=5, java_id=5),
            Server(name="Skyblock Haven", owner_id=8, server_properties_id=5, software_id=5, java_id=5),
            Server(name="Modded Paradise", owner_id=9, server_properties_id=5, software_id=5, java_id=5),
            Server(name="Prison Escape", owner_id=10, server_properties_id=5, software_id=5, java_id=5)
        ]
        
        for server in server_instances:
            session.add(server)
            
        session.commit()
        
        operator_instances = [
            Operator(server_id=1, user_id=2, permission_level="admin"),
            Operator(server_id=2, user_id=3, permission_level="moderator"),
            Operator(server_id=3, user_id=4, permission_level="admin"),
            Operator(server_id=4, user_id=5, permission_level="helper"),
            Operator(server_id=5, user_id=6, permission_level="helper"),
            Operator(server_id=6, user_id=7, permission_level="helper"),
            Operator(server_id=7, user_id=8, permission_level="helper"),
            Operator(server_id=8, user_id=9, permission_level="admin"),
        ]
        
        for operator in operator_instances:
            session.add(operator)
            
        session.commit()
        print("Sample data inserted for all models!")
    
    statement = select(User)
    results = session.exec(statement)
    print("\n# Users")
    for user in results:
        print(f"ID: {user.id}, Username: {user.username}, Email: {user.email}")
    
    java_statement = select(Java)
    java_results = session.exec(java_statement)
    print("\n# Java Versions")
    for java in java_results:
        print(f"ID: {java.id}, Name: {java.name}, Link: {java.link}")
    
    server_statement = select(Server)
    server_results = session.exec(server_statement)
    print("\n# Servers")
    for server in server_results:
        print(f"ID: {server.id}, Name: {server.name}, Owner ID: {server.owner_id}")
