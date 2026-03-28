import fitz  # PyMuPDF
import os
import logging
from typing import Optional
import pytesseract
from PIL import Image
import io

logger = logging.getLogger(__name__)


class ProcesadorPDF:
    """Clase para extraer texto de archivos PDF, incluyendo OCR para documentos escaneados."""
    
    def __init__(self, ocr_language: str = 'spa'):
        """
        Inicializa el procesador de PDF.
        
        Args:
            ocr_language: Idioma para OCR (por defecto: 'spa' para español)
        """
        self.ocr_language = ocr_language
        logger.info(f"ProcesadorPDF inicializado con idioma OCR: {ocr_language}")
    
    @staticmethod
    def validar_archivo(ruta_pdf: str) -> bool:
        """Verifica si el archivo existe y es un PDF válido."""
        if not os.path.exists(ruta_pdf):
            logger.warning(f"Archivo no encontrado: {ruta_pdf}")
            return False
        
        if not ruta_pdf.lower().endswith('.pdf'):
            logger.warning(f"El archivo no tiene extensión .pdf: {ruta_pdf}")
            return False
            
        return True
    
    def extraer_texto(self, ruta_pdf: str) -> str:
        """
        Extrae texto de un archivo PDF, usando OCR si es necesario.
        
        Args:
            ruta_pdf: Ruta al archivo PDF
            
        Returns:
            Texto extraído del PDF o mensaje de error
        """
        if not self.validar_archivo(ruta_pdf):
            return f"Error: No se encontró el archivo en {ruta_pdf}"
        
        texto_completo = ""
        documento = None
        
        try:
            documento = fitz.open(ruta_pdf)
            total_paginas = len(documento)
            logger.info(f"Procesando PDF: {ruta_pdf} ({total_paginas} páginas)")
            
            for num_pagina in range(total_paginas):
                pagina = documento.load_page(num_pagina)
                
                # 1. Intentar extracción de texto digital
                texto_digital = pagina.get_text().strip()
                
                if texto_digital:
                    texto_completo += f"[Página {num_pagina + 1}]:\n{texto_digital}\n\n"
                    logger.debug(f"Página {num_pagina + 1}: texto digital extraído ({len(texto_digital)} chars)")
                else:
                    # 2. Si falla (es un escaneo), aplicar OCR
                    logger.info(f"Página {num_pagina + 1}: aplicando OCR")
                    texto_ocr = self._aplicar_cr(pagina, num_pagina)
                    texto_completo += texto_ocr + "\n\n"
            
            logger.info(f"Extracción completada: {len(texto_completo)} caracteres totales")
            return texto_completo.strip()
            
        except fitz.FileDataError as e:
            logger.error(f"Error: Archivo PDF corrupto o inválido: {str(e)}")
            return f"Error: El archivo PDF parece estar corrupto o no es válido"
        except Exception as e:
            logger.error(f"Error crítico de procesamiento: {str(e)}", exc_info=True)
            return f"Error crítico de procesamiento: {str(e)}"
        finally:
            if documento:
                documento.close()
    
    def _aplicar_ocr(self, pagina, num_pagina: int) -> str:
        """
        Aplica OCR a una página del PDF.
        
        Args:
            pagina: Objeto página de PyMuPDF
            num_pagina: Número de página (índice base 0)
            
        Returns:
            Texto extraído mediante OCR
        """
        try:
            # Convertimos la página a una imagen (pixmap) con zoom 2x para mejor calidad
            pix = pagina.get_pixmap(matrix=fitz.Matrix(2, 2))
            img_data = pix.tobytes("png")
            imagen = Image.open(io.BytesIO(img_data))
            
            # Ejecutar OCR en el idioma configurado
            texto_ocr = pytesseract.image_to_string(imagen, lang=self.ocr_language)
            
            return f"[OCR Página {num_pagina + 1}]:\n{texto_ocr}"
            
        except Exception as e:
            logger.error(f"Error en OCR para página {num_pagina + 1}: {str(e)}")
            return f"[OCR Página {num_pagina + 1}]: Error al procesar - {str(e)}"