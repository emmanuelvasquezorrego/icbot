"""
Formateador de respuestas para WhatsApp.
Convierte la respuesta cruda del RAG en un mensaje amigable con emojis.
"""


from config import RATE_LIMIT_BLOCK_SECONDS


def format_response(answer: str, sources: list[dict] = None, is_first_message: bool = False) -> str:
    """
    Formatear la respuesta del RAG para WhatsApp.
    
    Args:
        answer: Respuesta del RAG
        sources: Documentos fuente (opcional)
        is_first_message: Si es True, incluye saludo completo
    """
    clean_answer = answer.strip()
    
    if is_first_message:
        # Primer mensaje: saludo completo + respuesta
        message = (
            f"👋 ¡Hola!\n\n"
            f"{clean_answer}\n\n"
            f"¿Tienes otra duda? 😊"
        )
    else:
        # Mensajes siguientes: solo respuesta
        message = (
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
        "⏳ Estás enviando muchos mensajes.\n\n"
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
        "👋 ¡Bienvenid@!\n\n"
        "Hola, soy TribuBot. Estoy aquí para ayudarte a encontrar información sobre "
        "dudas que tengas acerca de tu conjunto residencial. Puedes hacerme cualquier pregunta relacionada.\n\n"
        "¿En qué te puedo ayudar? 😊"
    )


def format_history_cleared_response() -> str:
    """Confirmación de que el historial fue limpiado."""
    return (
        "🗑️ Tu historial de conversación fue borrado.\n\n"
        "Podemos empezar de nuevo. 😊"
    )