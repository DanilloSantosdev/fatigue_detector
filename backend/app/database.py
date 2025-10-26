"""
Configuração do banco de dados PostgreSQL com SQLAlchemy async
"""
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv

load_dotenv()

# URL do banco de dados
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/fatigue_db")

# Engine assíncrono
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Log SQL queries (desabilitar em produção)
    future=True,
    pool_pre_ping=True,  # Verifica conexões antes de usar
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base para os models
Base = declarative_base()


# Dependency para injeção de sessão
async def get_db():
    """Dependency que fornece sessão do banco de dados"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Inicializa o banco de dados (cria tabelas)"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database initialized successfully!")

