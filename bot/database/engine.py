from redis.asyncio import Redis, ConnectionPool
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from config_reader import config
from database.models import Base

engine: AsyncEngine = create_async_engine(url=config.database.postgres.dsn.unicode_string(),
                                          pool_size=-1,
                                          max_overflow=-1,
                                          pool_pre_ping=True,
                                          future=True)


database_session: async_sessionmaker = async_sessionmaker(bind=engine, 
                                                          expire_on_commit=False, 
                                                          class_=AsyncSession)

redis_client: Redis = Redis.from_pool(
    connection_pool=ConnectionPool.from_url(url=config.database.redis.dsn.unicode_string(),
                                            decode_response=True))

async def postgres_connect() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(fn=Base.metadata.create_all, checkfirst=True)

