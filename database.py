from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from models import Base


sqlite_filepath = './var/flatfy.db'


engine = create_engine(f"sqlite:///{sqlite_filepath}")


Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)

Session.configure()

session = Session()
