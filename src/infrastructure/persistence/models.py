"""
Modelos de persistencia con SQLAlchemy.
Representan las tablas de la base de datos.
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Index
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class DocumentoModel(Base):
    """
    Modelo de persistencia para documentos.
    
    Mapea la entidad Documento a una tabla relacional.
    """
    __tablename__ = 'documentos'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    folio = Column(String(50), unique=True, nullable=False, index=True)
    fecha = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    asunto = Column(String(200), nullable=False)
    contenido = Column(Text, nullable=False)
    remitente = Column(String(100), nullable=True)
    ruta_archivo = Column(String(500), nullable=True)
    fecha_actualizacion = Column(DateTime, nullable=True)
    
    # Índices compuestos para búsquedas eficientes
    __table_args__ = (
        Index('ix_documentos_asunto', 'asunto'),
        Index('ix_documentos_remitente', 'remitente'),
        Index('ix_documentos_fecha_desc', fecha.desc()),
    )
    
    def __repr__(self) -> str:
        return f"<DocumentoModel(id={self.id}, folio='{self.folio}')>"
    
    def to_dict(self) -> dict:
        """Convierte el modelo a diccionario."""
        return {
            'id': self.id,
            'folio': self.folio,
            'fecha': self.fecha.isoformat() if self.fecha else None,
            'asunto': self.asunto,
            'contenido': self.contenido,
            'remitente': self.remitente,
            'ruta_archivo': self.ruta_archivo,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None,
        }
