import os
import logging
from typing import Optional
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class IACliente:
    """Cliente para interactuar con modelos de lenguaje locales o remotos."""
    
    def __init__(
        self, 
        base_url: Optional[str] = None, 
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.3
    ):
        """
        Inicializa el cliente de IA.
        
        Args:
            base_url: URL del servidor de IA (por defecto: http://localhost:1234/v1)
            api_key: API key para autenticación
            model: Nombre del modelo a utilizar
            temperature: Temperatura para generación de texto (0.0-1.0)
        """
        self.base_url = base_url or os.getenv("IA_BASE_URL", "http://localhost:1234/v1")
        self.api_key = api_key or os.getenv("IA_API_KEY", "lm-studio")
        self.model = model or os.getenv("IA_MODEL", "local-model")
        self.temperature = temperature
        
        self.client = OpenAI(base_url=self.base_url, api_key=self.api_key)
        logger.info(f"IACliente inicializado con base_url={self.base_url}, model={self.model}")

    def generar_respuesta(self, texto_oficio: str, contexto: Optional[str] = None) -> str:
        """
        Genera una respuesta formal basada en el contenido de un oficio.
        
        Args:
            texto_oficio: Contenido del oficio original
            contexto: Contexto adicional para la generación (opcional)
            
        Returns:
            Respuesta generada por la IA o mensaje de error
        """
        if not texto_oficio or not texto_oficio.strip():
            logger.warning("Intento de generar respuesta con texto vacío")
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
            
            if response.choices and len(response.choices) > 0:
                contenido = response.choices[0].message.content
                logger.info("Respuesta generada exitosamente")
                return contenido or "No se pudo generar contenido"
            else:
                logger.error("La respuesta de la IA no contiene choices")
                return "Error: La IA no generó una respuesta válida"
                
        except Exception as e:
            logger.error(f"Error al conectar con IA: {str(e)}", exc_info=True)
            return f"Error al conectar con el servicio de IA: {str(e)}"