import os
import logging
import time
from typing import Optional
from openai import OpenAI
from src.infrastructure.config import get_settings
from src.domain.entities import ResultadoOperacion, RespuestaIA

logger = logging.getLogger(__name__)

class IACliente:
    """Implementación del cliente de IA cumpliendo IServicioIA."""
    
    def __init__(self, settings=None):
        self.settings = settings or get_settings().ai
        self.client = OpenAI(base_url=self.settings.base_url, api_key=self.settings.api_key)

    def generar_respuesta(self, texto_oficio: str, contexto: Optional[str] = None) -> ResultadoOperacion[RespuestaIA]:
        if not texto_oficio or not texto_oficio.strip():
            return ResultadoOperacion(exitoso=False, error="Texto vacío")
        
        start_time = time.time()
        try:
            system_message = "Eres un asistente experto en correspondencia institucional."
            user_content = f"Redacta respuesta para:\n\n{texto_oficio}"
            if contexto:
                user_content += f"\n\nContexto: {contexto}"
            
            response = self.client.chat.completions.create(
                model=self.settings.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_content}
                ],
                temperature=self.settings.temperature,
                max_tokens=self.settings.max_tokens
            )
            
            duration_ms = int((time.time() - start_time) * 1000)
            
            if response.choices:
                contenido = response.choices[0].message.content or ""
                datos = RespuestaIA(
                    contenido=contenido,
                    modelo=self.settings.model,
                    tokens_utilizados=response.usage.total_tokens if response.usage else 0,
                    tiempo_respuesta_ms=duration_ms
                )
                return ResultadoOperacion(exitoso=True, datos=datos)
                
            return ResultadoOperacion(exitoso=False, error="Sin respuesta de IA")
                
        except Exception as e:
            logger.error(f"Error IA: {str(e)}", exc_info=True)
            return ResultadoOperacion(exitoso=False, error=str(e))
