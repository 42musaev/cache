from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
)

from db.conf import Base


class Node(Base):
    __tablename__ = 'nodes'

    id = Column(Integer, primary_key=True)
    value = Column(String(50), nullable=False)
    uuid = Column(String(256), unique=True, nullable=True)
    parent_uuid = Column(String(256), nullable=True)
    disable = Column(Boolean, default=False)
