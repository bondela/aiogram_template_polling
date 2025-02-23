from datetime import datetime

from sqlalchemy import BigInteger, Column, String, DateTime
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped

class Base(AsyncAttrs, DeclarativeBase):
    ...

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = Column(BigInteger, primary_key=True)
    username: Mapped[str] = Column(String, nullable=True)
    language: Mapped[str] = Column(String(8), nullable=True, default="en")
    last_activity: Mapped[datetime] = Column(DateTime, default=datetime.now)
    joined_at: Mapped[datetime] = Column(DateTime, default=datetime.now)
