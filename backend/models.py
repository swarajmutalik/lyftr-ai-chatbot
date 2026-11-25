
from sqlalchemy import Column, Integer, String, Text
from database import Base

class Message(Base):
    __tablename__ = "messages"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    session_id = Column(
        String(128),
        nullable=False,
        index=True
    )

    role = Column(
        String,
        nullable=False
    )

    content = Column(
        Text,
        nullable=False
    )

    metadata_json = Column(
        "metadata",
        Text,
        nullable=True
    )

    created_at = Column(
        String,
        nullable=False
    )
