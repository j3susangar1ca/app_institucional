import fitz  # PyMuPDF
import os
import logging
import pytesseract
from PIL import Image
import io

logger = logging.getLogger(__name__)

class ProcesadorPDF:
    """Implementación del procesador de PDF con soporte para OCR."""
    
    def __init__(self, ocr_language: str = 'spa'):
        self.ocr_language = ocr_language

    def extraer_texto(self, ruta_pdf: str) -> str:
        if not os.path.exists(ruta_pdf):
            return f"Error: No se encontró el archivo en {ruta_pdf}"
        
        texto_completo = ""
        documento = None
        
        try:
            documento = fitz.open(ruta_pdf)
            total_paginas = len(documento)
            
            for num_pagina in range(total_paginas):
                pagina = documento.load_page(num_pagina)
                
                # 1. Intentar extracción de texto digital
                texto_digital = pagina.get_text().strip()
                
                if texto_digital:
                    texto_completo += f"[Página {num_pagina + 1}]:\n{texto_digital}\n\n"
                else:
                    # 2. Si falla (es un escaneo), aplicar OCR
                    texto_ocr = self._aplicar_ocr(pagina, num_pagina)
                    texto_completo += texto_ocr + "\n\n"
            
            return texto_completo.strip()
            
        except Exception as e:
            logger.error(f"Error procesando PDF: {str(e)}", exc_info=True)
            return f"Error crítico de procesamiento: {str(e)}"
        finally:
            if documento:
                documento.close()
    
    def _aplicar_ocr(self, pagina, num_pagina: int) -> str:
        try:
            pix = pagina.get_pixmap(matrix=fitz.Matrix(2, 2))
            img_data = pix.tobytes("png")
            imagen = Image.open(io.BytesIO(img_data))
            
            texto_ocr = pytesseract.image_to_string(imagen, lang=self.ocr_language)
            return f"[OCR Página {num_pagina + 1}]:\n{texto_ocr}"
        except Exception as e:
            logger.error(f"Error en OCR para página {num_pagina + 1}: {str(e)}")
            return f"[OCR Página {num_pagina + 1}]: Error al procesar - {str(e)}"
