from src.database.models import Base
from src.database.database import DataBase
import asyncio
import src.config as config


async def main():
    database = DataBase(db_host=config.DB_HOST, db_password=config.DB_PASSWORD, db_user=config.DB_USER,
                        db_name=config.DB_NAME, db_port=config.DB_PORT)
    await database.create_schema(Base)


if __name__ == '__main__':
    asyncio.run(main())
