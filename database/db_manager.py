import os
import logging
from contextlib import contextmanager
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import StaticPool
from .modelos import Base, Documento
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Obtener la URL de la base de datos o usar la ruta por defecto
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/app_datos.db")

# Para SQLite en apps multihilo (Flet), configuramos StaticPool y desactivamos el chequeo de hilos
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False  # Cambiar a True para debug de SQL
)

# Usar scoped_session para manejo seguro de hilos
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))


@contextmanager
def get_db_session():
    """
    Context manager para manejar sesiones de base de datos de forma segura.
    
    Yields:
        Sesión de SQLAlchemy
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Error en transacción de BD: {str(e)}")
        raise e
    finally:
        db.close()


def _remove_session():
    """Remover la sesión actual del scoped_session."""
    SessionLocal.remove()


def init_db():
    """Crea las carpetas necesarias y las tablas en la base de datos."""
    try:
        # Asegurar que la carpeta 'data' exista para evitar errores al crear el .db
        data_dir = os.path.dirname("./data/app_datos.db")
        os.makedirs(data_dir, exist_ok=True)
        
        Base.metadata.create_all(bind=engine)
        logger.info("Base de datos inicializada correctamente")
    except Exception as e:
        logger.error(f"Error al inicializar la base de datos: {str(e)}", exc_info=True)
        raise e


def save_document(folio: str, asunto: str, contenido: str, remitente: str, ruta: str) -> dict:
    """
    Guarda un documento en la base de datos.
    
    Args:
        folio: Identificador único del documento
        asunto: Asunto del documento
        contenido: Contenido textual del documento
        remitente: Remitente del documento
        ruta: Ruta al archivo PDF
        
    Returns:
        Diccionario con los datos del documento guardado
        
    Raises:
        ValueError: Si faltan datos requeridos o el folio ya existe
        Exception: Si ocurre un error al guardar
    """
    if not folio or not folio.strip():
        raise ValueError("El folio es requerido")
    if not asunto or not asunto.strip():
        raise ValueError("El asunto es requerido")
    if not contenido or not contenido.strip():
        raise ValueError("El contenido es requerido")
    
    with get_db_session() as db:
        # Verificar si ya existe un documento con ese folio
        existing = db.query(Documento).filter(Documento.folio == folio).first()
        if existing:
            logger.warning(f"Intento de guardar documento con folio duplicado: {folio}")
            raise ValueError(f"Ya existe un documento con el folio '{folio}'")
        
        nuevo_doc = Documento(
            folio=folio.strip(),
            asunto=asunto.strip(),
            contenido=contenido,
            remitente=remitente,
            ruta_archivo=ruta
        )
        db.add(nuevo_doc)
        db.flush()
        doc_id = nuevo_doc.id
        logger.info(f"Documento guardado exitosamente: {nuevo_doc.folio} (ID: {doc_id})")
        return {"id": doc_id, "folio": nuevo_doc.folio, "asunto": nuevo_doc.asunto}


def get_document_by_folio(folio: str) -> dict | None:
    """
    Busca un documento por su folio.
    
    Args:
        folio: Folio del documento a buscar
        
    Returns:
        Diccionario con los datos del documento si existe, None en caso contrario
    """
    with get_db_session() as db:
        doc = db.query(Documento).filter(Documento.folio == folio).first()
        if doc:
            return doc.to_dict()
        return None


def get_all_documents(limit: int = 100) -> list[dict]:
    """
    Obtiene todos los documentos de la base de datos.
    
    Args:
        limit: Máximo número de documentos a retornar
        
    Returns:
        Lista de diccionarios con los datos de los documentos
    """
    with get_db_session() as db:
        docs = db.query(Documento).order_by(Documento.fecha.desc()).limit(limit).all()
        return [doc.to_dict() for doc in docs]
