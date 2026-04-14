"""
Configuración del sistema RAG con Qdrant
"""

import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de Groq
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama-3.3-70b-versatile"

# Configuración de Qdrant
# Modo embebido (sin Docker) - Para producción cambiar a host/port
QDRANT_PATH = "./qdrant_storage"  # Persistencia local
QDRANT_HOST = None  # Para Docker: "localhost"
QDRANT_PORT = None  # Para Docker: 6333

COLLECTION_NAME = "documentos_rag"

# Configuración de embeddings
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384  # Dimensión del modelo all-MiniLM-L6-v2

# Configuración de documentos
DOCUMENTS_PATH = "./documents"

# Configuración de retrieval
TOP_K_RESULTS = 3

# Validar que existe la API key
if not GROQ_API_KEY:
    raise ValueError(
        "No se encontró GROQ_API_KEY. "
    )