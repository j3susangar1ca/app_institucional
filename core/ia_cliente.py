from openai import OpenAI

class IACliente:
    def __init__(self):
        # Conexión por defecto a LM Studio
        self.client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

    def generar_respuesta(self, texto_oficio):
        try:
            response = self.client.chat.completions.create(
                model="local-model",
                messages=[
                    {"role": "system", "content": "Eres un asistente experto en correspondencia institucional."},
                    {"role": "user", "content": f"Redacta una respuesta formal para: {texto_oficio}"}
                ],
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error al conectar con LM Studio: {str(e)}"