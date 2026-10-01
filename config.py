import os
from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# Carga variables desde el archivo .env si existe
load_dotenv(os.path.join(BASE_DIR, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'almacen-repuestos-seguro-key-2026'
    
    _raw_db_url = os.environ.get('DATABASE_URL')
    if _raw_db_url:
        # Corrige el esquema postgres:// a postgresql://
        if _raw_db_url.startswith('postgres://'):
            _raw_db_url = _raw_db_url.replace('postgres://', 'postgresql://', 1)
        # Asegura compatibilidad con el driver psycopg2
        if _raw_db_url.startswith('postgresql://') and not _raw_db_url.startswith('postgresql+psycopg2://'):
            _raw_db_url = _raw_db_url.replace('postgresql://', 'postgresql+psycopg2://', 1)

    SQLALCHEMY_DATABASE_URI = _raw_db_url or f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'inventarios.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Optimización del pool para bases de datos en la nube (Supabase, Neon, etc.)
    if _raw_db_url and 'postgresql' in _raw_db_url:
        SQLALCHEMY_ENGINE_OPTIONS = {
            'pool_pre_ping': True,
            'pool_recycle': 300,
        }

    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'app', 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

