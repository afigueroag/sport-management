"""
Configuración de la base de datos con SQLAlchemy
"""

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool

from .config import settings

# Crear engine asincrónico
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,  # Log todas las queries en desarrollo
    future=True,
    poolclass=NullPool,  # Usar NullPool para mejor manejo en async
)

# Crear factory de sesiones
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

# Base para los modelos
Base = declarative_base()


async def get_db():
    """Dependency para inyectar sesión de BD en endpoints"""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Inicializar la base de datos (crear tablas)"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """Cerrar conexiones de la base de datos"""
    await engine.dispose()
