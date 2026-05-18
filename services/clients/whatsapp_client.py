"""
Cliente para Meta WhatsApp Cloud API
Maneja el envío de mensajes y verificación de webhook
"""

import requests
import logging
import config
import os

logger = logging.getLogger(__name__)


class WhatsAppClient:

    """Cliente para interactuar con la Meta WhatsApp Cloud API"""

    def __init__(self):
        self.api_url = (
            f"https://graph.facebook.com/v19.0/"
            f"{config.WHATSAPP_PHONE_NUMBER_ID}/messages"
        )
    @property
    def headers(self):
        return {
            "Authorization": f"Bearer {os.getenv('WHATSAPP_ACCESS_TOKEN')}",
            "Content-Type": "application/json"
        }

    def send_message(self, to: str, message: str) -> bool:

        """
        Enviar mensaje de texto a un número de WhatsApp.
        'to' debe ser el número en formato internacional sin '+': ej. '573001234567'
        """
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": message
            }
        }

        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            logger.info(f"Mensaje enviado a {to}: OK")
            return True

        except requests.exceptions.HTTPError as e:
            logger.error(f"Error HTTP enviando mensaje a {to}: {e.response.text}")
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Error de red enviando mensaje a {to}: {e}")
            return False

    @staticmethod
    def parse_webhook_message(data: dict) -> dict | None:

        """
        Extraer la información relevante del payload del webhook de Meta.
        Retorna dict con 'from', 'message_id', 'text' o None si no es mensaje de texto.
        """

        try:
            entry = data["entry"][0]
            changes = entry["changes"][0]
            value = changes["value"]

            # Verificar que hay mensajes (no solo status updates)
            if "messages" not in value:
                return None

            message = value["messages"][0]

            # Solo procesar mensajes de texto por ahora
            if message["type"] != "text":
                logger.info(f"Mensaje no-texto ignorado: tipo={message['type']}")
                return None

            return {
                "from": message["from"],          # Número del usuario
                "message_id": message["id"],       # ID del mensaje (para mark_as_read)
                "text": message["text"]["body"],   # Contenido del mensaje
                "timestamp": message["timestamp"]
            }

        except (KeyError, IndexError) as e:
            logger.warning(f"Payload webhook inesperado: {e}")
            return None

    def mark_as_read(self, message_id: str):

        """Marcar un mensaje como leído (muestra los dos ticks azules)"""

        payload = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id
        }
        try:
            requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=5
            )
        except Exception as e:
            logger.warning(f"No se pudo marcar como leído: {e}")