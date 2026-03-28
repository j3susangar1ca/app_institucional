import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from .modelos import Base, Documento
from dotenv import load_dotenv

load_dotenv()

# Obtener la URL de la base de datos o usar la ruta por defecto
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/app_datos.db")

# Para SQLite en apps multihilo (Flet), configuramos StaticPool y desactivamos el chequeo de hilos
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Crea las carpetas necesarias y las tablas en la base de datos."""
    # Asegurar que la carpeta 'data' exista para evitar errores al crear el .db
    os.makedirs("./data", exist_ok=True)
    Base.metadata.create_all(bind=engine)

def save_document(folio, asunto, contenido, remitente, ruta):
    db = SessionLocal()
    try:
        nuevo_doc = Documento(
            folio=folio,
            asunto=asunto,
            contenido=contenido,
            remitente=remitente,
            ruta_archivo=ruta
        )
        db.add(nuevo_doc)
        db.commit()
        db.refresh(nuevo_doc)
        return nuevo_doc
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
