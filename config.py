"""
Configuración del sistema RAG con Qdrant
"""

import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Lista de placeholders a rechazar (case-insensitive)
_PLACEHOLDERS = [
    "tu_api_key", "your-api-key", "api_key_aqui", "cambiar_en_produccion",
    "changeme", "placeholder", "test", "your_token", "your_secret"
]

def _is_invalid(value: str) -> bool:
    if not value:
        return True
    low = value.lower()
    return any(p in low for p in _PLACEHOLDERS)

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
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY")
FLASK_DEBUG      = os.getenv("FLASK_DEBUG", "false").lower() == "true"
PORT             = int(os.getenv("PORT", 5000))
 
# Conversaciones (multi-usuario)
CONVERSATIONS_FILE = "./data/conversations.json"
 
# Logger de conversaciones
LOGS_FILE = "./data/logs.jsonl"
MAX_LOG_TEXT = 500
 
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
    "FLASK_SECRET_KEY": FLASK_SECRET_KEY,
}
 
_invalid_keys = [k for k, v in _required.items() if _is_invalid(v)]

if _invalid_keys:
    
    raise ValueError(
        "Error de configuración: algunas variables de entorno son inválidas o faltan.\n"
        "Asegúrate de que todas las credenciales estén definidas en el archivo .env con valores reales (no placeholders)."
    )