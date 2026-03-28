from src.domain.entities.documento import Documento
from src.domain.repositories.document_repository import IDocumentRepository
from src.application.dto.documento_dto import DocumentoDTO

class GuardarDocumentoUseCase:
    """Caso de uso para persistir un documento en el repositorio."""
    
    def __init__(self, repository: IDocumentRepository):
        self.repository = repository

    def execute(self, dto: DocumentoDTO) -> DocumentoDTO:
        entity = Documento(
            folio=dto.folio,
            asunto=dto.asunto,
            contenido=dto.contenido,
            remitente=dto.remitente,
            ruta_archivo=dto.ruta_archivo
        )
        saved_entity = self.repository.save(entity)
        return DocumentoDTO.from_domain(saved_entity)
