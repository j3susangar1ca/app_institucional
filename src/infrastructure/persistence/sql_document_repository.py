"""
Implementación del repositorio de documentos con SQLAlchemy.
Capa de infraestructura que implementa la interfaz del dominio.
"""
import logging
import os
from contextlib import contextmanager
from typing import Optional, List
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import StaticPool

from src.infrastructure.config import get_settings
from src.domain.entities import Documento
from src.domain.value_objects import Folio, Asunto, ContenidoTexto, Remitente, RutaArchivo
from src.application.use_cases import IDocumentoRepository
from .models import Base, DocumentoModel

logger = logging.getLogger(__name__)

class DocumentoRepositoryImpl(IDocumentoRepository):
    """
    Implementación del repositorio de documentos usando SQLAlchemy.
    """
    
    def __init__(self):
        settings = get_settings()
        self._engine = create_engine(
            settings.database.url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=settings.database.echo
        )
        self._session_factory = scoped_session(
            sessionmaker(autocommit=False, autoflush=False, bind=self._engine)
        )
    
    def inicializar(self) -> None:
        """Crea las tablas si no existen."""
        os.makedirs("./data", exist_ok=True)
        Base.metadata.create_all(bind=self._engine)
        logger.info("Base de datos inicializada")
    
    @contextmanager
    def _obtener_sesion(self):
        """Context manager para sesiones de base de datos."""
        sesion = self._session_factory()
        try:
            yield sesion
            sesion.commit()
        except Exception as e:
            sesion.rollback()
            logger.error(f"Error en transacción: {e}", exc_info=True)
            raise
        finally:
            sesion.close()
    
    def _a_modelo(self, documento: Documento) -> DocumentoModel:
        """Convierte una entidad de dominio a modelo de persistencia."""
        return DocumentoModel(
            id=documento.id,
            folio=documento.folio.valor,
            asunto=documento.asunto.valor,
            contenido=documento.contenido.valor,
            remitente=documento.remitente.valor if documento.remitente else None,
            ruta_archivo=documento.ruta_archivo.valor if documento.ruta_archivo else None,
            fecha=documento.fecha,
            # fecha_actualizacion no existe en la entidad básica, pero el modelo la tiene
        )
    
    def _a_entidad(self, modelo: DocumentoModel) -> Documento:
        """Convierte un modelo de persistencia a entidad de dominio."""
        return Documento(
            id=modelo.id,
            folio=Folio(modelo.folio),
            asunto=Asunto(modelo.asunto),
            contenido=ContenidoTexto(modelo.contenido),
            remitente=Remitente(modelo.remitente) if modelo.remitente else None,
            ruta_archivo=RutaArchivo(modelo.ruta_archivo) if modelo.ruta_archivo else None,
            fecha=modelo.fecha
        )
    
    def guardar(self, documento: Documento) -> Documento:
        """Guarda un documento en la base de datos."""
        with self._obtener_sesion() as sesion:
            modelo = self._a_modelo(documento)
            # Manejar actualización vs creación
            if modelo.id:
                sesion.merge(modelo)
            else:
                sesion.add(modelo)
            sesion.flush()
            return self._a_entidad(modelo)
    
    def buscar_por_folio(self, folio: str) -> Optional[Documento]:
        """Busca un documento por su folio."""
        with self._obtener_sesion() as sesion:
            modelo = sesion.query(DocumentoModel).filter(DocumentoModel.folio == folio).first()
            return self._a_entidad(modelo) if modelo else None
    
    def existe_folio(self, folio: str) -> bool:
        """Verifica si existe un documento con el folio dado."""
        with self._obtener_sesion() as sesion:
            return sesion.query(DocumentoModel).filter(DocumentoModel.folio == folio).count() > 0
    
    def listar_todos(self, limite: int = 100) -> List[Documento]:
        """Lista todos los documentos."""
        with self._obtener_sesion() as sesion:
            modelos = sesion.query(DocumentoModel).order_by(DocumentoModel.fecha.desc()).limit(limite).all()
            return [self._a_entidad(m) for m in modelos]
