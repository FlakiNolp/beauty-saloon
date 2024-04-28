from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import URL
import src.config as config
import sqlalchemy.exc
from src.utils.singleton import Singleton


class DataBase(metaclass=Singleton):
    def __init__(self, db_user: str = config.DB_USER,
                 db_password: str = config.DB_PASSWORD,
                 db_host: str = config.DB_HOST,
                 db_port: int = config.DB_PORT,
                 db_name: str = config.DB_NAME,
                 test_mode: bool = False):
        if test_mode:
            self._url = URL.create(drivername="postgresql+asyncpg", username=db_user, password=db_password,
                                   host=db_host,
                                   port=db_port,
                                   database="test")
        else:
            self._url = URL.create(drivername="postgresql+asyncpg", username=db_user, password=db_password,
                                   host=db_host,
                                   port=db_port,
                                   database=db_name)
        self._async_engine = create_async_engine(self._url)
        self.async_session_maker = async_sessionmaker(self._async_engine, expire_on_commit=False)

    async def create_schema(self, schema):
        async with self._async_engine.begin() as conn:
            await conn.run_sync(schema.metadata.create_all)

    async def get_db(self):
        async with self.async_session_maker() as session:
            try:
                yield session
            except sqlalchemy.exc.SQLAlchemyError:
                await session.rollback()
            finally:
                await session.close()
