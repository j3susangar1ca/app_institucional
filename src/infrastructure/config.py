"""
Configuración centralizada de la aplicación.
Implementa el patrón Singleton para acceso global.
"""
from dataclasses import dataclass, field
from functools import lru_cache
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class DatabaseConfig:
    """Configuración de base de datos."""
    url: str = field(default_factory=lambda: os.getenv("DATABASE_URL", "sqlite:///./data/app_datos.db"))
    pool_size: int = 5
    echo: bool = False


@dataclass(frozen=True)
class AIConfig:
    """Configuración del cliente de IA."""
    base_url: str = field(default_factory=lambda: os.getenv("IA_BASE_URL", "http://localhost:1234/v1"))
    api_key: str = field(default_factory=lambda: os.getenv("IA_API_KEY", "lm-studio"))
    model: str = field(default_factory=lambda: os.getenv("IA_MODEL", "local-model"))
    temperature: float = 0.3
    max_tokens: int = 2000
    
    def validate(self) -> None:
        """Valida que la configuración de IA sea válida."""
        if not self.api_key:
            raise ValueError("IA_API_KEY no está configurada")
        if not self.base_url:
            raise ValueError("IA_BASE_URL no está configurada")


@dataclass(frozen=True)
class VectorStoreConfig:
    """Configuración del almacén vectorial."""
    path: str = "./data/chroma_db"
    collection_name: str = "documentos_institucionales"


@dataclass(frozen=True)
class UIConfig:
    """Configuración de la interfaz de usuario."""
    window_width: int = 1100
    window_height: int = 800
    theme_mode: str = "light"
    primary_color: str = "#1a365d"
    padding: int = 30


@dataclass(frozen=True)
class AppConfig:
    """Configuración principal de la aplicación."""
    app_name: str = "Sistema de Archivo e IA"
    version: str = "2.0.0"
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    ai: AIConfig = field(default_factory=AIConfig)
    vector_store: VectorStoreConfig = field(default_factory=VectorStoreConfig)
    ui: UIConfig = field(default_factory=UIConfig)
    
    def validate(self) -> None:
        """Valida toda la configuración de la aplicación."""
        self.ai.validate()


@lru_cache(maxsize=1)
def get_settings() -> AppConfig:
    """
    Obtiene la configuración de la aplicación (Singleton).
    
    Returns:
        AppConfig: Instancia única de configuración.
    """
    return AppConfig()
