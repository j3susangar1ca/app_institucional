from typing import List, Optional
from src.domain.entities import Documento as DomainDocumento
from src.domain.value_objects import Folio, Asunto, ContenidoTexto, Remitente, RutaArchivo
from src.application.use_cases import IDocumentoRepository
from .models import DocumentoModel
from .database import get_db_session

class SqlAlchemyDocumentRepository(IDocumentoRepository):
    """Implementación de SQLAlchemy para el repositorio de documentos."""
    
    def guardar(self, documento: DomainDocumento) -> DomainDocumento:
        with get_db_session() as db:
            model = DocumentoModel(
                folio=documento.folio.valor,
                asunto=documento.asunto.valor,
                contenido=documento.contenido.valor,
                remitente=documento.remitente.valor if documento.remitente else None,
                ruta_archivo=documento.ruta_archivo.valor if documento.ruta_archivo else None,
                fecha=documento.fecha
            )
            if documento.id:
                model.id = documento.id
            
            db.add(model)
            db.flush()
            documento.id = model.id
            return documento

    def buscar_por_folio(self, folio: str) -> Optional[DomainDocumento]:
        with get_db_session() as db:
            model = db.query(DocumentoModel).filter(DocumentoModel.folio == folio).first()
            if not model:
                return None
            return self._to_domain(model)

    def existe_folio(self, folio: str) -> bool:
        with get_db_session() as db:
            return db.query(DocumentoModel).filter(DocumentoModel.folio == folio).count() > 0

    def listar_todos(self, limite: int = 100) -> List[DomainDocumento]:
        with get_db_session() as db:
            models = db.query(DocumentoModel).order_by(DocumentoModel.fecha.desc()).limit(limite).all()
            return [self._to_domain(m) for m in models]

    def _to_domain(self, model: DocumentoModel) -> DomainDocumento:
        return DomainDocumento(
            id=model.id,
            folio=Folio(model.folio),
            asunto=Asunto(model.asunto),
            contenido=ContenidoTexto(model.contenido),
            fecha=model.fecha,
            remitente=Remitente(model.remitente) if model.remitente else None,
            ruta_archivo=RutaArchivo(model.ruta_archivo) if model.ruta_archivo else None
        )
