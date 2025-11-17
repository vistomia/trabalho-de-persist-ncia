from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer, insert, select
import logging
import logger as logger
from ....models.user import User

class Database:
    """Gerencia um banco de dados baseado em um arquivo CSV com um índice sequencial.
    
    :param str uri: URI do banco de dados.
    :return: None
    """
    def __init__(self, uri: str):
        self.__engine = create_engine(uri, echo_pool=True)
        self.logger = logging.getLogger(__name__)
        user = User()
    
    def get_engine(self):
        return self.__engine


if __name__ == "__main__":
    db = Database(uri='sqlite:///data.sqlite')
    engine = db.get_engine()
    metadata = MetaData()
    print("oi")

    users_table = Table(
        'users',
        metadata,
        Column('id', Integer, primary_key=True),
        Column('username', String(50)),
        Column('email', String(50))
    )

    metadata.create_all(engine)

    with engine.connect() as conn:
        # Check if the table has any data
        result = conn.execute(select(users_table).limit(1))
        
        if result.first() is None:
            print("Table is empty. Inserting sample data...")
            # Create a list of new users to add
            data_to_insert = [
                {"username": "alice", "email": "alice@example.com"},
                {"username": "bob", "email": "bob@example.com"},
                {"username": "carol", "email": "carol@example.com"}
            ]
            
            # Execute the insert statement
            conn.execute(insert(users_table), data_to_insert)
            
            # Commit the changes to the database file
            conn.commit()
            
            # Print all data
            for row in result:
                print(f"ID: {row.id}, Username: {row.username}, Email: {row.email}")
        else:
            pass
        stmt = select(users_table)
        result = conn.execute(stmt)
        for row in result:
            print(f"ID: {row.id}, Username: {row.username}, Email: {row.email}")
