from typing import List, Optional
from src.domain.entities.documento import Documento as DomainDocumento
from src.domain.repositories.document_repository import IDocumentRepository
from .models import DocumentoModel
from .database import get_db_session

class SqlAlchemyDocumentRepository(IDocumentRepository):
    """Implementación de SQLAlchemy para el repositorio de documentos."""
    
    def save(self, documento: DomainDocumento) -> DomainDocumento:
        with get_db_session() as db:
            model = DocumentoModel(
                folio=documento.folio,
                asunto=documento.asunto,
                contenido=documento.contenido,
                remitente=documento.remitente,
                ruta_archivo=documento.ruta_archivo,
                fecha=documento.fecha
            )
            # Si el dominio ya tiene ID, es una actualización (aunque aquí simplificamos a creación)
            if documento.id:
                model.id = documento.id
            
            db.add(model)
            db.flush()
            documento.id = model.id
            return documento

    def get_by_folio(self, folio: str) -> Optional[DomainDocumento]:
        with get_db_session() as db:
            model = db.query(DocumentoModel).filter(DocumentoModel.folio == folio).first()
            if not model:
                return None
            return self._to_domain(model)

    def get_all(self, limit: int = 100) -> List[DomainDocumento]:
        with get_db_session() as db:
            models = db.query(DocumentoModel).order_by(DocumentoModel.fecha.desc()).limit(limit).all()
            return [self._to_domain(m) for m in models]

    def _to_domain(self, model: DocumentoModel) -> DomainDocumento:
        return DomainDocumento(
            id=model.id,
            folio=model.folio,
            asunto=model.asunto,
            contenido=model.contenido,
            fecha=model.fecha,
            remitente=model.remitente,
            ruta_archivo=model.ruta_archivo
        )
