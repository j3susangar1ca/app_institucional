import os
import logging
from typing import Optional
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class IACliente:
    """Implementación del cliente de IA usando OpenAI (LM Studio)."""
    
    def __init__(
        self, 
        base_url: Optional[str] = None, 
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.3
    ):
        self.base_url = base_url or os.getenv("IA_BASE_URL", "http://localhost:1234/v1")
        self.api_key = api_key or os.getenv("IA_API_KEY", "lm-studio")
        self.model = model or os.getenv("IA_MODEL", "local-model")
        self.temperature = temperature
        
        self.client = OpenAI(base_url=self.base_url, api_key=self.api_key)

    def generar_respuesta(self, texto_oficio: str, contexto: Optional[str] = None) -> str:
        if not texto_oficio or not texto_oficio.strip():
            return "Error: El texto del oficio está vacío"
        
        try:
            system_message = "Eres un asistente experto en correspondencia institucional. Redacta respuestas formales, claras y profesionales."
            user_content = f"Redacta una respuesta formal para el siguiente oficio:\n\n{texto_oficio}"
            if contexto:
                user_content += f"\n\nContexto adicional: {contexto}"
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_content}
                ],
                temperature=self.temperature,
                max_tokens=2000
            )
            
            if response.choices:
                return response.choices[0].message.content or "No se pudo generar contenido"
            return "Error: La IA no generó una respuesta válida"
                
        except Exception as e:
            logger.error(f"Error al conectar con IA: {str(e)}", exc_info=True)
            return f"Error al conectar con el servicio de IA: {str(e)}"
