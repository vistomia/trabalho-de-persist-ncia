import database as db

server = db.Database(
    data_path="store/server_data.csv",
    index_path="store/server_index.seq",
    key_column="id",
    schema=["id", "name", "motd", "version"]
)

server = db.Database(
    data_path="store/server_data.csv",
    index_path="store/server_index.seq",
    key_column="id",
    schema=["id", "name", "motd", "version"]
)

def print_header():
    for key in server.get("1").keys():
        print(f"{key:<10}", end='\t')
    print()

def print_entries():
    for entry in server.get_all():
        for value in entry.values():
            print(f"{str(value):<10}", end='\t')
        print()
