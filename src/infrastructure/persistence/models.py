from sqlalchemy import Column, Integer, String, DateTime, Text, Index
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class DocumentoModel(Base):
    """Modelo de SQLAlchemy para la tabla de documentos."""
    
    __tablename__ = 'documentos'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    folio = Column(String(50), unique=True, nullable=False, index=True)
    fecha = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    asunto = Column(String(200), nullable=False)
    contenido = Column(Text, nullable=False)
    remitente = Column(String(100), nullable=True)
    ruta_archivo = Column(String(255), nullable=True)
    
    __table_args__ = (
        Index('ix_documentos_asunto', 'asunto'),
        Index('ix_documentos_remitente', 'remitente'),
    )

    def __repr__(self):
        return f"<DocumentoModel(id={self.id}, folio='{self.folio}')>"
