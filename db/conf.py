import databases
import sqlalchemy
from sqlalchemy.orm import declarative_base
from config.conf import RootConfig

DATABASE_URL = RootConfig.DB_URL

database = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()

engine = sqlalchemy.create_engine(
    DATABASE_URL
)

Base = declarative_base()

# models
from node.models import Node
