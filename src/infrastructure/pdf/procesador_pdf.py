"""
Implementación del procesador de PDF.
Capa de infraestructura para extracción de texto de documentos PDF.
"""
import os
import time
import logging
import io
from typing import Optional, List

import fitz  # PyMuPDF
from PIL import Image
import pytesseract

from src.domain.entities import ResultadoProcesamientoPDF, ResultadoOperacion

logger = logging.getLogger(__name__)

class PDFProcessorImpl:
    """
    Implementación del procesador de PDF con capacidades OCR.
    """
    
    def __init__(self, idioma_ocr: str = 'spa'):
        self._idioma_ocr = idioma_ocr
        logger.info(f"Procesador PDF inicializado: {idioma_ocr}")
    
    def validar_archivo(self, ruta: str) -> bool:
        if not os.path.exists(ruta) or not ruta.lower().endswith('.pdf'):
            return False
        return os.path.isfile(ruta)
    
    def procesar_pdf(self, ruta: str) -> ResultadoOperacion[ResultadoProcesamientoPDF]:
        if not self.validar_archivo(ruta):
            return ResultadoOperacion.fallo_con_error("Archivo inválido", "ARCHIVO_INVALIDO")
        
        tiempo_inicio = time.time()
        documento = None
        
        try:
            documento = fitz.open(ruta)
            total_paginas = len(documento)
            contenido_total = ""
            paginas_con_ocr = []
            errores = []
            
            for num_pagina in range(total_paginas):
                pagina = documento.load_page(num_pagina)
                texto_digital = pagina.get_text().strip()
                
                if texto_digital:
                    contenido_total += f"[Página {num_pagina + 1}]\n{texto_digital}\n\n"
                else:
                    try:
                        texto_ocr = self._aplicar_ocr(pagina)
                        contenido_total += f"[OCR - Página {num_pagina + 1}]\n{texto_ocr}\n\n"
                        paginas_con_ocr.append(num_pagina + 1)
                    except Exception as e:
                        errores.append(f"Error OCR pág {num_pagina + 1}: {str(e)}")
            
            tiempo_total = (time.time() - tiempo_inicio) * 1000
            resultado = ResultadoProcesamientoPDF(
                contenido_extraido=contenido_total.strip(),
                numero_paginas=total_paginas,
                paginas_con_ocr=paginas_con_ocr,
                tiempo_procesamiento_ms=tiempo_total,
                errores=errores,
                requiere_ocr=len(paginas_con_ocr) > 0
            )
            return ResultadoOperacion.exito_con_datos(resultado)
            
        except Exception as e:
            logger.error(f"Error procesando PDF: {e}", exc_info=True)
            return ResultadoOperacion.fallo_con_error(str(e), "ERROR_PROCESAMIENTO")
        finally:
            if documento:
                documento.close()
    
    def _aplicar_ocr(self, pagina) -> str:
        pix = pagina.get_pixmap(matrix=fitz.Matrix(2, 2))
        img_data = pix.tobytes("png")
        imagen = Image.open(io.BytesIO(img_data))
        return pytesseract.image_to_string(imagen, lang=self._idioma_ocr).strip()
