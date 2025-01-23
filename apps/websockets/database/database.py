from duckdb import connect
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text 
from pathlib import Path
import os

# The name of the db should not really matter
# as it is destroyed by the lifespan in app.py
DB_PATH = "websockets.db"

engine = create_async_engine(f"sqlite+aiosqlite:///{DB_PATH}")

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_db():
    async with AsyncSessionLocal() as session:
        async with session.begin():
            await session.execute(text("PRAGMA synchronous=NORMAL"))
            await session.execute(text("PRAGMA wal_autocheckpoint=1000"))
        yield session

async def create_sqlite_db(db_path=DB_PATH):
    schema_path = Path(__file__).parent / "schema_sqlite.sql"

    async with engine.begin() as conn:
        with open(schema_path, "r") as schema_file:
            schema_sql = text(schema_file.read())
            await conn.execute(schema_sql)

def delete_sqlite_db(db_path=DB_PATH):
    if db_path != ":memory:" and os.path.exists(db_path):
        os.remove(db_path)

def con_duckdb(db_sqlite_path=DB_PATH):
    schema_path = Path(__file__).parent / "schema_duckdb.sql"

    con = connect()
    con.execute(f"ATTACH '{db_sqlite_path}' AS db (TYPE SQLITE)")

    with open(schema_path, "r") as schema_file:
        con.execute(schema_file.read())

    return con

