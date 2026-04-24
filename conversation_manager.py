"""
Gestor de conversaciones multi-usuario
- Memoria de los últimos N mensajes por número de teléfono
- Persistencia en disco (JSON) para sobrevivir reinicios
"""

import json
import os
import threading
import logging
from collections import deque
from datetime import datetime
import config
from langchain_core.messages import HumanMessage, AIMessage

logger = logging.getLogger(__name__)


class ConversationManager:

    """
    Gestiona el historial de conversaciones por usuario.
    Thread-safe para uso con Gunicorn multi-worker.
    """

    def __init__(self):
        self.conversations: dict[str, deque] = {}
        self.lock = threading.Lock()
        self._load_from_disk()

    def add_message(self, phone: str, role: str, content: str):
        """
        Agregar un mensaje al historial del usuario.
        role: 'user' | 'assistant'
        """
        with self.lock:
            if phone not in self.conversations:
                self.conversations[phone] = deque(maxlen=config.MAX_CONVERSATION_HISTORY)

            self.conversations[phone].append({
                "role": role,
                "content": content,
                "timestamp": datetime.now().isoformat()
            })
            self._save_to_disk()

    def get_history(self, phone: str) -> list[dict]:

        """Retorna el historial del usuario como lista (más recientes al final)."""

        with self.lock:
            if phone not in self.conversations:
                return []
            return list(self.conversations[phone])

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

    def clear_history(self, phone: str):

        """Limpiar historial de un usuario específico."""

        with self.lock:
            if phone in self.conversations:
                del self.conversations[phone]
                self._save_to_disk()
                logger.info(f"Historial limpiado para {phone}")

    def get_user_count(self) -> int:

        """Cantidad de usuarios únicos con historial."""

        with self.lock:
            return len(self.conversations)
        
    def get_messages_for_llm(self, phone: str, limit: int = None):

        """
        Retorna los últimos N mensajes como objetos LangChain.
        """

        if limit is None:
            limit = config.MAX_CONTEXT_MESSAGES
        
        history = self.get_history(phone)
        recent_history = history[-limit:] if history else []
        
        messages = []
        for msg in recent_history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))
        
        return messages

    # -------------------------------------------------------------------------
    # Persistencia en disco
    # -------------------------------------------------------------------------

    def _save_to_disk(self):

        """Guardar historial en JSON. Llamar siempre dentro del lock."""

        try:
            os.makedirs(os.path.dirname(config.CONVERSATIONS_FILE), exist_ok=True)

            # Convertir deques a listas para serializar
            serializable = {
                phone: list(msgs)
                for phone, msgs in self.conversations.items()
            }

            # Escritura atómica: escribir en temp y luego rename
            tmp_path = config.CONVERSATIONS_FILE + ".tmp"
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(serializable, f, ensure_ascii=False, indent=2)
            os.replace(tmp_path, config.CONVERSATIONS_FILE)

        except Exception as e:
            logger.error(f"Error guardando conversaciones: {e}")

    def _load_from_disk(self):

        """Cargar historial desde JSON al iniciar."""
        
        if not os.path.exists(config.CONVERSATIONS_FILE):
            logger.info("No existe archivo de conversaciones previas, iniciando vacío")
            return

        try:
            with open(config.CONVERSATIONS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

            for phone, messages in data.items():
                # Respetar el límite máximo al cargar
                self.conversations[phone] = deque(
                    messages[-config.MAX_CONVERSATION_HISTORY:],
                    maxlen=config.MAX_CONVERSATION_HISTORY
                )

            logger.info(
                f"Historial cargado: {len(self.conversations)} usuarios"
            )

        except (json.JSONDecodeError, Exception) as e:
            logger.error(f"Error cargando conversaciones, iniciando vacío: {e}")