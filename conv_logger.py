"""
Logger de conversaciones en formato JSON.
Registra cada interacción completa: usuario, pregunta, respuesta, tiempo, score.
"""

import json
import os
import threading
import logging
from datetime import datetime
import config

logger = logging.getLogger(__name__)


class ConversationLogger:

    """Registra conversaciones completas en un archivo JSON estructurado."""

    def __init__(self):
        self.lock = threading.Lock()
        os.makedirs(os.path.dirname(config.LOGS_FILE), exist_ok=True)

        # Crear archivo si no existe
        if not os.path.exists(config.LOGS_FILE):
            with open(config.LOGS_FILE, 'a', encoding='utf-8') as f:
                pass

    def log_interaction(
        self,
        phone: str,
        question: str,
        answer: str,
        retrieved_docs: list,
        processing_time_ms: int,
        rate_limited: bool = False
    ):
        
        """
        Registrar una interacción completa.
        Se agrega al archivo JSON como una línea (JSON Lines format).
        """

        record = {
            "timestamp": datetime.now().isoformat(),
            "phone": self._mask_phone(phone),
            "question": question[:config.MAX_LOG_TEXT] + ("..." if len(question) > config.MAX_LOG_TEXT else ""),
            "answer": answer[:config.MAX_LOG_TEXT] + ("..." if len(answer) > config.MAX_LOG_TEXT else ""),
            "sources": [
                {
                    "source": doc["metadata"]["source"],
                    "score": round(doc.get("score", 0), 4),
                    "chunk_index": doc["metadata"].get("chunk_index", 0)
                }
                for doc in retrieved_docs
            ],
            "processing_time_ms": processing_time_ms,
            "rate_limited": rate_limited,
            "docs_retrieved": len(retrieved_docs)
        }

        with self.lock:
            try:
                with open(config.LOGS_FILE, "a", encoding="utf-8") as f:
                    f.write(json.dumps(record, ensure_ascii=False) + "\n")
            except Exception:
                logger.exception("Error guardando log")

    def log_rate_limit_event(self, phone: str, reason: str):

        """Registrar cuando un usuario es bloqueado por rate limiting."""

        record = {
            "timestamp": datetime.now().isoformat(),
            "phone": self._mask_phone(phone),
            "event": "rate_limit",
            "reason": reason
        }
        with self.lock:
            try:
                with open(config.LOGS_FILE, "a", encoding="utf-8") as f:
                    f.write(json.dumps(record, ensure_ascii=False) + "\n")
            except Exception:
                logger.exception("Error guardando log de rate limit")

    @staticmethod
    def _mask_phone(phone: str) -> str:

        """Enmascarar los dígitos centrales del número por privacidad."""

        if len(phone) <= 6:
            return phone
        return phone[:3] + "****" + phone[-3:]