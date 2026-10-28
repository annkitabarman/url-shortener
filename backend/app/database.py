
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = (
    "postgresql+psycopg://postgres:Ankita288%40@localhost:5432/url_shortener"
)

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


class Base(DeclarativeBase):
    pass
