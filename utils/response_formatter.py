"""
Formateador de respuestas para WhatsApp.
Convierte la respuesta cruda del RAG en un mensaje amigable con emojis.
"""


from config import RATE_LIMIT_BLOCK_SECONDS


def format_response(answer: str, is_first_message: bool = False) -> str:
    """
    Formatear la respuesta del RAG para WhatsApp.
    
    Args:
        answer: Respuesta del RAG
        is_first_message: Si es True, incluye saludo completo
    """
    clean_answer = answer.strip()
    
    if is_first_message:
        # Primer mensaje: saludo completo + respuesta
        message = (
            f"👋 ¡Hola!\n\n"
            f"{clean_answer}\n\n"
        )
    else:
        # Mensajes siguientes: solo respuesta
        message = (
            f"{clean_answer}\n\n"
        )
    
    return message


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
        "tu conjunto residencial.\n\n"
        "*Puedo ayudarte con:*\n"
        "• Horarios de áreas comunes\n"
        "• Pagos y cuotas de administración\n"
        "• Normas de convivencia\n"
        "• Información general del conjunto\n\n"
        "*Comandos disponibles:*\n"
        "• */pqrs* → Radicar una Petición, Queja o Reclamo\n"
        "• */limpiar* → Borrar historial de conversación\n\n"
        "¿En qué te puedo ayudar? 😊"
    )


def format_history_cleared_response() -> str:
    """Confirmación de que el historial fue limpiado."""
    return (
        "🗑️ Tu historial de conversación fue borrado.\n\n"
        "Podemos empezar de nuevo. 😊"
    )


def format_pqr_info() -> str:

    """Comando /pqrs explícito — información completa."""

    return (
        "📋 *Peticiones, Quejas y Reclamos (PQR)*\n\n"
        "Las PQR deben ser atendidas directamente por la administración.\n\n"
        "*¿Cómo radicar tu PQR?*\n"
        "*Comunícate a:*\n"
        "• 📧 Correo: admin@villaverde.com\n"
        "• 📞 Teléfono: +57 300 123 4567\n"
        "• 🕐 Horario: Lunes a viernes, 8:00 AM – 5:00 PM\n\n"
        "Tu solicitud será atendida en un plazo máximo de *5 días hábiles*."
    )


def format_pqr_redirect() -> str:

    """Detección por keyword — redirección breve."""

    return (
        "Lo siento. Eso está fuera de lo que puedo ayudarte.\n\n"
        "Para este tipo de situaciones, contacta directamente "
        "a la administración:\n"
        "• 📧 admin@villaverde.com\n"
        "• 📞 +57 300 123 4567\n"
        "• 🕐 Lunes a viernes, 8:00 AM – 5:00 PM"
    )