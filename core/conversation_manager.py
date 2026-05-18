"""
Gestor de conversaciones usando Redis.
"""

import json
import logging
from datetime import datetime

import config

from services.clients.redis_client import redis_client
from langchain_core.messages import HumanMessage, AIMessage

logger = logging.getLogger(__name__)


class ConversationManager:

    def _key(self, phone: str) -> str:
        return f"conversation:{phone}"

    def add_message(self, phone: str, role: str, content: str):

        key = self._key(phone)

        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }

        # Agregar al final
        redis_client.rpush(key, json.dumps(message))

        # Mantener máximo N mensajes
        redis_client.ltrim(
            key,
            -config.MAX_CONVERSATION_HISTORY,
            -1
        )

    def get_history(self, phone: str) -> list[dict]:

        key = self._key(phone)

        messages = redis_client.lrange(key, 0, -1)

        return [json.loads(m) for m in messages]

    def clear_history(self, phone: str):

        redis_client.delete(self._key(phone))

        logger.info(f"Historial limpiado para {phone}")

    def get_user_count(self) -> int:

        keys = redis_client.keys("conversation:*")
        return len(keys)

    
    def get_context_string(self, phone: str, limit: int = None) -> str:

        """
        Retorna el historial formateado como string.
        Si limit es None, usa el valor de config.
        """

        if limit is None:
            limit = config.MAX_CONTEXT_MESSAGES
        
        history = self.get_history(phone)

        if not history:
            return ""
        
        # Tomar solo los últimos N mensajes
        recent_history = history[-limit:]
        
        lines = []

        for msg in recent_history:
            prefix = "Usuario" if msg["role"] == "user" else "Asistente"
            lines.append(f"{prefix}: {msg['content']}")
        
        return "\n".join(lines)
    

    def get_messages_for_llm(
        self,
        phone: str,
        limit: int = None
    ):

        if limit is None:
            limit = config.MAX_CONTEXT_MESSAGES

        history = self.get_history(phone)

        recent_history = history[-limit:] if history else []

        messages = []

        for msg in recent_history:

            if msg["role"] == "user":
                messages.append(
                    HumanMessage(content=msg["content"])
                )

            elif msg["role"] == "assistant":
                messages.append(
                    AIMessage(content=msg["content"])
                )

        return messages