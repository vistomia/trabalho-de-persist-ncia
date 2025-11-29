from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer, insert, select
# import logging
# import logger as logger
from models.user import User
from sqlmodel import SQLModel, Field, create_engine, Session, select

class Database:
    """Gerencia um banco de dados baseado em um arquivo CSV com um índice sequencial.
    
    :param str uri: URI do banco de dados.
    :return: None
    """
    def __init__(self, uri: str):
        self.__engine = create_engine(uri, echo_pool=True)
        # self.logger = logging.getLogger(__name__)
        user = User()
    
    def get_engine(self):
        return self.__engine


if __name__ == "__main__":
    db = Database(uri='sqlite:///data.sqlite')
    engine = db.get_engine()
    metadata = MetaData()
    
    # Create tables
    SQLModel.metadata.create_all(engine)

    # Use User model instead of users_table
    metadata.create_all(engine)

    with engine.connect() as conn:
        # Check if the table has any data
        result = conn.execute(select(User).limit(1))
        
        if result.first() is None:
            print("Table is empty. Inserting sample data...")
            # Create a list of new users to add
            data_to_insert = [
                {"username": "alice", "email": "alice@example.com"},
                {"username": "bob", "email": "bob@example.com"},
                {"username": "carol", "email": "carol@example.com"}
            ]
            
            # Execute the insert statement
            conn.execute(insert(User), data_to_insert)
            
            # Commit the changes to the database file
            conn.commit()
            
            # Print all data
            for row in result:
                print(f"ID: {row.id}, Username: {row.username}, Email: {row.email}")
        else:
            pass
        stmt = select(User)
        result = conn.execute(stmt)
        for row in result:
            print(f"ID: {row.id}, Username: {row.username}, Email: {row.email}")
