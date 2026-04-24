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
GROQ_MODEL_FAST = "llama-3.1-8b-instant"

# Memoria conversacional
MAX_CONVERSATION_HISTORY = 100  # Guardar en disco
MAX_CONTEXT_MESSAGES = 6        # Enviar al LLM

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

# WhatsApp Cloud API (Meta)
WHATSAPP_ACCESS_TOKEN   = os.getenv("WHATSAPP_ACCESS_TOKEN")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
WHATSAPP_VERIFY_TOKEN   = os.getenv("WHATSAPP_VERIFY_TOKEN")   # Token que tú inventas
WHATSAPP_APP_SECRET     = os.getenv("WHATSAPP_APP_SECRET")     # Clave secreta de la app Meta
 
# Flask / Servidor
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "cambiar_en_produccion")
FLASK_DEBUG      = os.getenv("FLASK_DEBUG", "false").lower() == "true"
PORT             = int(os.getenv("PORT", 5000))
 
# Conversaciones (multi-usuario)
CONVERSATIONS_FILE = "./data/conversations.json"
 
# Logs
LOGS_FILE = "./data/logs.jsonl"
 
# Rate Limiter
RATE_LIMIT_MAX_MESSAGES   = int(os.getenv("RATE_LIMIT_MAX_MESSAGES", 3))
RATE_LIMIT_WINDOW_SECONDS = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", 20))
RATE_LIMIT_BLOCK_SECONDS  = int(os.getenv("RATE_LIMIT_BLOCK_SECONDS", 60))
 
# Validaciones al iniciar
_required = {
    "GROQ_API_KEY": GROQ_API_KEY,
    "WHATSAPP_ACCESS_TOKEN": WHATSAPP_ACCESS_TOKEN,
    "WHATSAPP_PHONE_NUMBER_ID": WHATSAPP_PHONE_NUMBER_ID,
    "WHATSAPP_VERIFY_TOKEN": WHATSAPP_VERIFY_TOKEN,
    "WHATSAPP_APP_SECRET": WHATSAPP_APP_SECRET,
}
 
_missing = [k for k, v in _required.items() if not v]
if _missing:
    raise ValueError(
        f"Faltan variables de entorno obligatorias: {', '.join(_missing)}\n"
    )