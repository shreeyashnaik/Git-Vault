from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from models import base

class DatabaseConnection:
    db_instance = None
    db_uri = None
    db_session = None

    def __new__(cls, host, port, user, password, database):
        if cls.db_uri is None:
            cls.db_uri =f"mysql://{user}:{password}@{host}:{port}/{database}"
        if cls.db_instance is None:
            cls.db_instance = super(DatabaseConnection, cls).__new__(cls)
            cls.db_instance.engine = create_engine(cls.db_uri)
            cls.db_instance.Session = sessionmaker(bind=cls.db_instance.engine)
            cls.db_session = cls.db_instance.Session()
        return cls.db_instance

    def get_session(self):
        return self.db_session
    
    def init_session(self):
        db_session = self.get_session()

    def create_tables(self):
        base.Base.metadata.create_all(self.db_instance.engine)
    
    def drop_all_tables(self):
        base.Base.metadata.drop_all(self.db_instance.engine)