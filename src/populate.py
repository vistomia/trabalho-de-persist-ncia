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

app = fastapi.FastAPI()
app.include_router(user.router)

db = database.Database(uri='sqlite:///data.sqlite')
engine = db.get_engine()
metadata = MetaData()

SQLModel.metadata.create_all(engine)

metadata.create_all(engine)

with Session(engine) as session:
    # Check if the table has any data
    statement = select(User).limit(1)
    result = session.exec(statement).first()
    
    if result is None:
        print("Table is empty. Inserting sample data...")
        
        users_to_add = [
            User(username="alice", email="alice@example.com", password="password123"),
            User(username="bob", email="bob@example.com", password="password123"),
            User(username="carol", email="carol@example.com", password="password123"),
            User(username="david", email="david@example.com", password="password123"),
            User(username="eve", email="eve@example.com", password="password123")
        ]
        
        java_instances = [
            Java(name="OpenJDK 8", link="https://openjdk.java.net/projects/jdk8/"),
            Java(name="OpenJDK 11", link="https://openjdk.java.net/projects/jdk/11/"),
            Java(name="OpenJDK 17", link="https://openjdk.java.net/projects/jdk/17/"),
            Java(name="OpenJDK 21", link="https://openjdk.java.net/projects/jdk/21/"),
            Java(name="Oracle JDK 8", link="https://www.oracle.com/java/technologies/javase/javase-jdk8-downloads.html")
        ]
        
        server_properties = [
            ServerProperties(difficulty="easy", max_players=20, gamemode="survival", motd="Welcome to Server 1"),
            ServerProperties(difficulty="normal", max_players=50, gamemode="creative", motd="Creative Server"),
            ServerProperties(difficulty="hard", max_players=30, gamemode="adventure", motd="Adventure Awaits"),
            ServerProperties(difficulty="peaceful", max_players=10, gamemode="spectator", motd="Peaceful World"),
            ServerProperties(difficulty="normal", max_players=100, gamemode="survival", motd="Mega Server")
        ]
        
        software_instances = [
            Software(id=1, name="Vanilla", link="https://minecraft.net", version="1.20.1", plugins_enabled=False, mods_enabled=False),
            Software(id=2, name="Paper", link="https://papermc.io", version="1.20.1", plugins_enabled=True, mods_enabled=False),
            Software(id=3, name="Forge", link="https://files.minecraftforge.net", version="1.20.1", plugins_enabled=False, mods_enabled=True),
            Software(id=4, name="Fabric", link="https://fabricmc.net", version="1.20.1", plugins_enabled=False, mods_enabled=True),
            Software(id=5, name="Spigot", link="https://www.spigotmc.org", version="1.20.1", plugins_enabled=True, mods_enabled=False)
        ]

        map_instances = [
            Map(name="Overworld", description="The main dimension", link="https://minecraft.wiki/w/Overworld"),
            Map(name="The Nether", description="Hell dimension", link="https://minecraft.wiki/w/The_Nether"),
            Map(name="The End", description="End dimension with dragon", link="https://minecraft.wiki/w/The_End"),
            Map(name="Custom World", description="Custom generated world", link="https://example.com/custom"),
            Map(name="Skyblock", description="Survival on floating island", link="https://example.com/skyblock")
        ]
        
        # Add all instances to session
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
            
        # Commit to get IDs for foreign key relationships
        session.commit()
        
        # Now create 5 Server instances (need foreign keys from above)
        server_instances = [
            Server(name="Survival Server", owner_id=1, server_properties_id=1, software_id=1, java_id=1),
            Server(name="Creative Server", owner_id=2, server_properties_id=2, software_id=2, java_id=2),
            Server(name="Adventure Server", owner_id=3, server_properties_id=3, software_id=3, java_id=3),
            Server(name="Peaceful Server", owner_id=4, server_properties_id=4, software_id=4, java_id=4),
            Server(name="Mega Server", owner_id=5, server_properties_id=5, software_id=5, java_id=5)
        ]
        
        for server in server_instances:
            session.add(server)
            
        session.commit()
        
        # Create 5 Operator instances (many-to-many relationship)
        operator_instances = [
            Operator(server_id=1, user_id=1, permission_level="admin"),
            Operator(server_id=1, user_id=2, permission_level="moderator"),
            Operator(server_id=2, user_id=3, permission_level="admin"),
            Operator(server_id=3, user_id=4, permission_level="helper"),
            Operator(server_id=4, user_id=5, permission_level="admin")
        ]
        
        for operator in operator_instances:
            session.add(operator)
            
        session.commit()
        print("Sample data inserted for all models!")
    
    # Print all data from User table
    statement = select(User)
    results = session.exec(statement)
    print("\n# Users")
    for user in results:
        print(f"ID: {user.id}, Username: {user.username}, Email: {user.email}")
    
    # Print Java instances
    java_statement = select(Java)
    java_results = session.exec(java_statement)
    print("\n# Java Versions")
    for java in java_results:
        print(f"ID: {java.id}, Name: {java.name}, Link: {java.link}")
    
    # Print Server instances
    server_statement = select(Server)
    server_results = session.exec(server_statement)
    print("\n# Servers")
    for server in server_results:
        print(f"ID: {server.id}, Name: {server.name}, Owner ID: {server.owner_id}")
