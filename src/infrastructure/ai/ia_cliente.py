"""
Implementación del cliente de IA con OpenAI.
Capa de infraestructura para comunicación con servicios de IA.
"""
import time
import logging
from typing import Optional
from openai import OpenAI

from src.infrastructure.config import get_settings
from src.domain.entities import RespuestaIA, ResultadoOperacion

logger = logging.getLogger(__name__)

class OpenAIClientImpl:
    """
    Implementación del cliente de IA usando OpenAI API.
    """
    
    def __init__(self, settings=None):
        self._settings = settings or get_settings().ai
        self._base_url = self._settings.base_url
        self._api_key = self._settings.api_key
        self._model = self._settings.model
        self._temperature = self._settings.temperature
        self._max_tokens = self._settings.max_tokens
        
        self._validar_configuracion()
        
        self._cliente = OpenAI(
            base_url=self._base_url,
            api_key=self._api_key,
            timeout=60.0,
        )
        
        logger.info(f"Cliente IA inicializado: {self._base_url}")
    
    def _validar_configuracion(self) -> None:
        if not self._api_key:
            raise ValueError("API key no configurada (IA_API_KEY)")
        if not self._base_url:
            raise ValueError("URL no configurada (IA_BASE_URL)")
    
    def generar_respuesta(
        self,
        texto_oficio: str,
        contexto: Optional[str] = None
    ) -> ResultadoOperacion[RespuestaIA]:
        if not texto_oficio or not texto_oficio.strip():
            return ResultadoOperacion.fallo_con_error("Texto vacío", "TEXTO_VACIO")
        
        tiempo_inicio = time.time()
        try:
            system_message = (
                "Eres un asistente experto en correspondencia institucional gubernamental. "
                "Redacta respuestas formales, claras y profesionales."
            )
            
            user_content = f"Redacta respuesta para:\n\n{texto_oficio}"
            if contexto:
                user_content += f"\n\nContexto: {contexto}"
            
            response = self._cliente.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_content}
                ],
                temperature=self._temperature,
                max_tokens=self._max_tokens,
            )
            
            tiempo_total = (time.time() - tiempo_inicio) * 1000
            
            if not response.choices:
                return ResultadoOperacion.fallo_con_error("Sin respuesta", "RESPUESTA_VACIA")
            
            contenido = response.choices[0].message.content or ""
            respuesta = RespuestaIA(
                contenido=contenido,
                modelo=self._model,
                tokens_utilizados=response.usage.total_tokens if response.usage else 0,
                tiempo_respuesta_ms=tiempo_total,
            )
            return ResultadoOperacion.exito_con_datos(respuesta)
            
        except Exception as e:
            logger.error(f"Error IA: {e}", exc_info=True)
            return ResultadoOperacion.fallo_con_error(str(e), "ERROR_CONEXION")
