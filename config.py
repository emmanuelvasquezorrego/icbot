"""
Configuración del sistema RAG con Qdrant
"""

import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de Groq
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

# Memoria conversacional
MAX_CONVERSATION_HISTORY = 100  # Número máximo de mensajes a guardar por usuario
MAX_CONTEXT_MESSAGES = 6        # Mensajes maximos a enviar al LLM para contexto(recientes primero)

# Configuración de Qdrant
# Modo cliente-servidor (con Docker)
QDRANT_PATH = os.getenv("QDRANT_PATH", "./qdrant_storage" )
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))

# Nombre de la colección en Qdrant
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "documentos_rag")

# Configuración de embeddings
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", "384"))  # Dimensión del modelo de embeddings

# Configuración de documentos
DOCUMENTS_PATH = os.getenv("DOCUMENTS_PATH", "./documents")

# Configuración de retrieval
TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", "5"))

# WhatsApp Cloud API (Meta)
WHATSAPP_ACCESS_TOKEN   = os.getenv("WHATSAPP_ACCESS_TOKEN")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
WHATSAPP_VERIFY_TOKEN   = os.getenv("WHATSAPP_VERIFY_TOKEN") # Token para verificar el webhook (puede ser cualquier string, pero debe coincidir con lo configurado en Meta)
WHATSAPP_APP_SECRET     = os.getenv("WHATSAPP_APP_SECRET")
 
# Flask
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "cambiar_en_produccion")
FLASK_DEBUG      = os.getenv("FLASK_DEBUG", "false").lower() == "true"
PORT             = int(os.getenv("PORT", 5000))
 
# Conversaciones (multi-usuario)
CONVERSATIONS_FILE = "./data/conversations.json"
 
# Logs
LOGS_FILE = "./data/logs.jsonl"
 
# Rate Limiter
RATE_LIMIT_MAX_MESSAGES   = 3 # Máximo de mensajes por ventana de tiempo
RATE_LIMIT_WINDOW_SECONDS = 20 # Ventana de tiempo en segundos
RATE_LIMIT_BLOCK_SECONDS  = 60 # Tiempo que se bloquea al usuario si excede el límite
 
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