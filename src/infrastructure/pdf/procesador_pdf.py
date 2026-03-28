import fitz  # PyMuPDF
import os
import logging
import pytesseract
from PIL import Image
import io
from typing import Set
from src.domain.entities import ResultadoOperacion, ResultadoProcesamientoPDF

logger = logging.getLogger(__name__)

class ProcesadorPDF:
    """Implementación del procesador de PDF cumpliendo IServicioProcesadorPDF."""
    
    def __init__(self, ocr_language: str = 'spa'):
        self.ocr_language = ocr_language

    def validar_archivo(self, ruta: str) -> bool:
        """Valida que el archivo exista y sea un PDF."""
        return os.path.exists(ruta) and ruta.lower().endswith(".pdf")

    def procesar_pdf(self, ruta: str) -> ResultadoOperacion[ResultadoProcesamientoPDF]:
        """Procesa el PDF y extrae su contenido."""
        texto_completo = ""
        documento = None
        requiere_ocr = False
        paginas_con_ocr: Set[int] = set()
        
        try:
            documento = fitz.open(ruta)
            total_paginas = len(documento)
            
            for num_pagina in range(total_paginas):
                pagina = documento.load_page(num_pagina)
                texto_digital = pagina.get_text().strip()
                
                if texto_digital:
                    texto_completo += f"[Página {num_pagina + 1}]:\n{texto_digital}\n\n"
                else:
                    requiere_ocr = True
                    paginas_con_ocr.add(num_pagina + 1)
                    texto_ocr = self._aplicar_ocr(pagina, num_pagina)
                    texto_completo += texto_ocr + "\n\n"
            
            datos = ResultadoProcesamientoPDF(
                contenido_extraido=texto_completo.strip(),
                numero_paginas=total_paginas,
                requiere_ocr=requiere_ocr,
                paginas_con_ocr=paginas_con_ocr
            )
            return ResultadoOperacion(exitoso=True, datos=datos)
            
        except Exception as e:
            logger.error(f"Error procesando PDF: {str(e)}", exc_info=True)
            return ResultadoOperacion(exitoso=False, error=str(e))
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
            return f"[OCR Página {num_pagina + 1}]: Error - {str(e)}"
