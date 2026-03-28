import fitz  # PyMuPDF
import os
import pytesseract
from PIL import Image
import io

class ProcesadorPDF:
    @staticmethod
    def extraer_texto(ruta_pdf: str) -> str:
        if not os.path.exists(ruta_pdf):
            return f"Error: No se encontró el archivo en {ruta_pdf}"
        
        texto_completo = ""
        try:
            documento = fitz.open(ruta_pdf)
            
            for num_pagina in range(len(documento)):
                pagina = documento.load_page(num_pagina)
                
                # 1. Intentar extracción de texto digital
                texto_digital = pagina.get_text().strip()
                
                if texto_digital:
                    texto_completo += texto_digital + "\n\n"
                else:
                    # 2. Si falla (es un escaneo), aplicar OCR
                    # Convertimos la página a una imagen (pixmap)
                    pix = pagina.get_pixmap(matrix=fitz.Matrix(2, 2)) # Zoom 2x para mejor calidad
                    img_data = pix.tobytes("png")
                    imagen = Image.open(io.BytesIO(img_data))
                    
                    # Ejecutar OCR en español
                    texto_ocr = pytesseract.image_to_string(imagen, lang='spa')
                    texto_completo += f"[OCR Página {num_pagina+1}]:\n{texto_ocr}\n\n"
            
            documento.close()
            return texto_completo.strip()
            
        except Exception as e:
            return f"Error crítico de procesamiento: {str(e)}"