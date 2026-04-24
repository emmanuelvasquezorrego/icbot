"""
Formateador de respuestas para WhatsApp.
Convierte la respuesta cruda del RAG en un mensaje amigable con emojis.
"""


from config import RATE_LIMIT_BLOCK_SECONDS


def format_response(answer: str, sources: list[dict] = None) -> str:
    """
    Formatear la respuesta del RAG para WhatsApp.
    
    Ejemplo de salida:
    👋 ¡Hola!
    
    📚 *Respuesta:*
    Aquí va la respuesta del bot...
    
    ¿Tienes otra duda? 😊
    """
    # Limpiar respuesta
    clean_answer = answer.strip()

    message = (
        f"👋 ¡Hola!\n\n"
        f"📚 *Respuesta:*\n"
        f"{clean_answer}\n\n"
        f"¿Tienes otra duda? 😊"
    )

    return message


def format_no_info_response() -> str:
    """Respuesta cuando el bot no tiene información sobre el tema."""
    return (
        "🔍 No encontré información sobre eso en mi base de conocimiento.\n\n"
        "Intenta reformular tu pregunta o consulta sobre otro tema. 😊"
    )


def format_rate_limit_response(seconds_remaining: int = None) -> str:
    """Respuesta cuando el usuario supera el límite de mensajes."""

    wait_time = seconds_remaining if seconds_remaining is not None else RATE_LIMIT_BLOCK_SECONDS

    return (
        "⏳ Estás enviando mensajes muy rápido.\n\n"
        f"Por favor espera *{wait_time} segundos* antes de continuar. 🙏"
    )


def format_error_response() -> str:
    """Respuesta genérica de error."""
    return (
        "😕 Ocurrió un error procesando tu mensaje.\n\n"
        "Por favor intenta de nuevo en unos momentos."
    )


def format_welcome_message() -> str:
    """Mensaje de bienvenida para nuevos usuarios o comando /start."""
    return (
        "👋 ¡Bienvenido!\n\n"
        "Soy un asistente que responde preguntas basándome en documentos "
        "específicos. Puedes hacerme cualquier pregunta relacionada con la "
        "información disponible.\n\n"
        "📝 *Comandos disponibles:*\n"
        "• *limpiar* - Borrar el historial de conversación\n"
        "• *ayuda* - Mostrar este mensaje\n\n"
        "¿En qué te puedo ayudar? 😊"
    )


def format_history_cleared_response() -> str:
    """Confirmación de que el historial fue limpiado."""
    return (
        "🗑️ Tu historial de conversación fue borrado.\n\n"
        "Podemos empezar de nuevo. ¿En qué te puedo ayudar? 😊"
    )