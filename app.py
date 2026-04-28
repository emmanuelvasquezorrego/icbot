"""
Servidor Flask – Webhook de WhatsApp Cloud API (Meta)
Punto de entrada principal de la aplicación.
"""

import hashlib
import hmac
import logging
import time
from threading import Thread

from flask import Flask, request, jsonify, abort

import config
from whatsapp_client import WhatsAppClient
from conversation_manager import ConversationManager
from rate_limiter import RateLimiter
from conv_logger import ConversationLogger
from response_formatter import (
    format_response,
    format_rate_limit_response,
    format_error_response,
    format_welcome_message,
    format_history_cleared_response,
)
from rag_agent import RAGAgent

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s – %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Flask
app = Flask(__name__)
app.secret_key = config.FLASK_SECRET_KEY

# Inicializar componentes globales (clientes, gestores, etc.)
logger.info("Inicializando componentes...")
whatsapp   = WhatsAppClient()
conv_mgr   = ConversationManager()
rate_lim   = RateLimiter()
conv_log   = ConversationLogger()

logger.info("Cargando agente RAG (puede tardar unos segundos)...")
rag_agent  = RAGAgent(conversation_manager=conv_mgr)
logger.info("Agente RAG listo ✓")

def verify_meta_signature(request_data: bytes, signature_header: str) -> bool:

    """
    Verificar que el webhook realmente proviene de Meta usando HMAC-SHA256.
    """

    if not signature_header or not signature_header.startswith("sha256="):
        return False

    expected_signature = signature_header[len("sha256="):]
    computed = hmac.new(
        config.WHATSAPP_APP_SECRET.encode("utf-8"),
        request_data,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(computed, expected_signature)


# Lógica principal de procesamiento

# Comandos especiales (sin consultar al agente RAG)
SPECIAL_COMMANDS = {
    "hola", "inicio", "start", "ayuda", "help", "/start", "/help", "/ayuda"
}
CLEAR_COMMANDS = {"limpiar", "clear", "borrar", "/limpiar", "/clear", "/borrar"}


def process_message(phone: str, message_id: str, text: str):
    """
    Procesar un mensaje entrante de WhatsApp.
    """
    start_time = time.time()
    
    # Marcar como leído
    whatsapp.mark_as_read(message_id)
    
    # ── Rate limiting ──────────────────────────────────────
    allowed, reason = rate_lim.is_allowed(phone)
    
    if not allowed:
        if reason == "notify":
            response_text = format_rate_limit_response()
            whatsapp.send_message(phone, response_text)
            conv_log.log_rate_limit_event(phone, "rate_limit_notify")
        else:
            conv_log.log_rate_limit_event(phone, "rate_limit_silent")
        return
    
    text_lower = text.strip().lower()
    
    # ── Comandos especiales ────────────────────────────────
    if text_lower in SPECIAL_COMMANDS:
        whatsapp.send_message(phone, format_welcome_message())
        return
    
    if text_lower in CLEAR_COMMANDS:
        conv_mgr.clear_history(phone)
        whatsapp.send_message(phone, format_history_cleared_response())
        return
    
    # ── Consulta RAG ───────────────────────────────────────
    try:
        # Detectar si es el primer mensaje del usuario
        user_history = conv_mgr.get_history(phone)
        is_first = len(user_history) == 0  # ← No hay mensajes previos
        
        # Consultar al agente RAG
        answer, retrieved_docs = rag_agent.query(
            phone=phone,
            question=text
        )
        
        # Formatear respuesta según si es primer mensaje o no
        response_text = format_response(
            answer=answer,
            sources=retrieved_docs,
            is_first_message=is_first  # ← Pasar el indicador
        )
        
        whatsapp.send_message(phone, response_text)
        
        # Log de la interacción
        processing_ms = int((time.time() - start_time) * 1000)
        conv_log.log_interaction(
            phone=phone,
            question=text,
            answer=answer,
            retrieved_docs=retrieved_docs,
            processing_time_ms=processing_ms
        )
        
    except Exception as e:
        logger.exception(f"Error procesando mensaje de {phone}: {e}")
        whatsapp.send_message(phone, format_error_response())

# Rutas Flask
@app.get("/webhook")
def webhook_verify():

    """
    Verificación del webhook por parte de Meta.
    Meta llama a este endpoint con GET para verificar que el servidor es legítimo
    """

    mode      = request.args.get("hub.mode")
    token     = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == config.WHATSAPP_VERIFY_TOKEN:
        logger.info("Webhook verificado correctamente por Meta ✓")
        return challenge, 200

    logger.warning(f"Verificación de webhook fallida: mode={mode}, token={token}")
    abort(403)


@app.post("/webhook")
def webhook_receive():

    """
    Recepción de mensajes entrantes de WhatsApp.
    Meta envía un POST con el payload del mensaje.
    """

    # Verificar firma HMAC
    raw_body  = request.get_data()
    signature = request.headers.get("X-Hub-Signature-256", "")

    if not verify_meta_signature(raw_body, signature):
        logger.warning("Firma HMAC inválida – petición rechazada")
        abort(403)

    # Parsear payload
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"status": "ignored"}), 200

    parsed = whatsapp.parse_webhook_message(data)
    if not parsed:
        # Puede ser un status update (mensaje entregado, leído, etc.)
        return jsonify({"status": "ignored"}), 200

    phone      = parsed["from"]
    message_id = parsed["message_id"]
    text       = parsed["text"]

    logger.info(f"Mensaje de {phone[:3]}***{phone[-3:]}: '{text[:50]}'")

    # Procesar en hilo separado para responder a Meta en < 5 s
    thread = Thread(
        target=process_message,
        args=(phone, message_id, text),
        daemon=True
    )
    thread.start()

    # Meta requiere respuesta 200 inmediata
    return jsonify({"status": "ok"}), 200

@app.get("/health")
def health_check():
    """Health check para Railway, AWS ELB, etc."""
    return jsonify({
        "status": "healthy",
        "users_in_memory": conv_mgr.get_user_count(),
    }), 200


@app.get("/")
def index():
    return jsonify({"message": "RAG WhatsApp Bot corriendo"}), 200

# Entry point (solo para desarrollo local)
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=config.PORT,
        debug=config.FLASK_DEBUG
    )