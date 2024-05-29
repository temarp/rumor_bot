from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy import BigInteger, String, ForeignKey, Text, Integer, DateTime, Float
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs

engine = create_async_engine(url='postgresql+asyncpg://postgres:postgres@localhost:5444/postgres', echo=True)

async_session = async_sessionmaker(engine)

class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger)
    group_id: Mapped[int] = mapped_column(Integer, ForeignKey('groups.id'), nullable=True)
    road_id: Mapped[int] = mapped_column(Integer, ForeignKey('roads.id'), nullable=True)


class Event(Base):
    __tablename__ = 'events'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    group_id: Mapped[int] = mapped_column(Integer, ForeignKey('groups.id'), nullable=True)
    road_id: Mapped[int] = mapped_column(Integer, ForeignKey('roads.id'), nullable=True)
    picture: Mapped[str] = mapped_column(Text)
    description: Mapped[str] = mapped_column(Text)
    date_start = mapped_column(DateTime)
    mark: Mapped[int] = mapped_column(Integer, default=0)
    count_mark: Mapped[int] = mapped_column(Integer, default=0)

class Group(Base):
    __tablename__ = 'groups'

    id: Mapped[int] = mapped_column(primary_key=True)
    region: Mapped[str] = mapped_column(String(50))
    city: Mapped[str] = mapped_column(String(50))
    podrazd: Mapped[str] = mapped_column(Text)


class Road(Base):
    __tablename__ = 'roads'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    level: Mapped[str] = mapped_column(String(15))

class NoteBook(Base):
    __tablename__ = 'notebook'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    event_id: Mapped[int] = mapped_column(Integer, ForeignKey('events.id'))
    mark: Mapped[int] = mapped_column(Integer, default=0)


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

