import os

from sqlalchemy import create_engine

# база SQLite лежит в корне проекта, можно заменить через переменную окружения
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///salon.db")

engine = create_engine(DATABASE_URL)
