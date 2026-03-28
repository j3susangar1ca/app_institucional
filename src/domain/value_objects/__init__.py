from dataclasses import dataclass

@dataclass(frozen=True)
class Folio:
    valor: str
    def __post_init__(self):
        if not self.valor or len(self.valor) < 3:
            raise ValueError("Folio inválido")

@dataclass(frozen=True)
class Asunto:
    valor: str
    def __post_init__(self):
        if not self.valor:
            raise ValueError("Asunto requerido")

@dataclass(frozen=True)
class ContenidoTexto:
    valor: str
    def __post_init__(self):
        if not self.valor:
            raise ValueError("Contenido requerido")

@dataclass(frozen=True)
class Remitente:
    valor: str

@dataclass(frozen=True)
class RutaArchivo:
    valor: str
