from sqlalchemy import Column, Integer, String, DateTime, Text, Index
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Documento(Base):
    """Modelo para representar un documento en la base de datos."""
    
    __tablename__ = 'documentos'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    folio = Column(String(50), unique=True, nullable=False, index=True)
    fecha = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    asunto = Column(String(200), nullable=False)
    contenido = Column(Text, nullable=False)
    remitente = Column(String(100), nullable=True)
    ruta_archivo = Column(String(255), nullable=True)
    
    # Índices adicionales para búsquedas eficientes
    __table_args__ = (
        Index('ix_documentos_asunto', 'asunto'),
        Index('ix_documentos_remitente', 'remitente'),
    )
    
    def __repr__(self):
        return f"<Documento(id={self.id}, folio='{self.folio}', asunto='{self.asunto}')>"
    
    def to_dict(self) -> dict:
        """Convierte el documento a un diccionario."""
        return {
            'id': self.id,
            'folio': self.folio,
            'fecha': self.fecha.isoformat() if self.fecha else None,
            'asunto': self.asunto,
            'contenido': self.contenido,
            'remitente': self.remitente,
            'ruta_archivo': self.ruta_archivo
        }
