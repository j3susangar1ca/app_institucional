import os
import logging
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import StaticPool
from dotenv import load_dotenv
from .models import Base
from ..config import get_settings

settings = get_settings()

engine = create_engine(
    settings.database.url, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=settings.database.echo
)

SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

@contextmanager
def get_db_session():
    """Manejo seguro de sesiones de base de datos."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Error en sesión de BD: {str(e)}")
        raise e
    finally:
        db.close()
        SessionLocal.remove()

def init_db():
    """Inicializa la base de datos y crea las tablas."""
    data_dir = os.path.dirname("./data/app_datos.db")
    os.makedirs(data_dir, exist_ok=True)
    Base.metadata.create_all(bind=engine)
    logger.info("Infraestructura de persistencia inicializada")
