from src.infrastructure.pdf.procesador_pdf import ProcesadorPDF
from src.infrastructure.ai.ia_cliente import IACliente
from src.application.dto.documento_dto import DocumentoDTO

class ProcesarDocumentoUseCase:
    """Caso de uso para extraer texto de PDF y generar respuesta con IA."""
    
    def __init__(self, procesador: ProcesadorPDF, ia: IACliente):
        self.procesador = procesador
        self.ia = ia

    def extraer_texto(self, ruta_pdf: str) -> str:
        return self.procesador.extraer_texto(ruta_pdf)

    def generar_respuesta(self, texto_oficio: str) -> str:
        return self.ia.generar_respuesta(texto_oficio)
