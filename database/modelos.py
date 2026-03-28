from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

class Documento(Base):
    __tablename__ = 'documentos'
    id = Column(Integer, primary_key=True)
    folio = Column(String(50), unique=True)
    fecha = Column(DateTime, default=datetime.datetime.utcnow)
    asunto = Column(String(200))
    contenido = Column(Text)
    remitente = Column(String(100))
    ruta_archivo = Column(String(255))
