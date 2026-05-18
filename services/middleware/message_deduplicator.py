"""
Evita procesar mensajes duplicados.
"""

import hashlib
import logging
import config

from services.clients.redis_client import redis_client

logger = logging.getLogger(__name__)


class MessageDeduplicator:

    @staticmethod
    def _id_key(message_id: str) -> str:
        return f"message:id:{message_id}"

    @staticmethod
    def _content_key(phone: str, text: str) -> str:

        normalized = text.strip().lower()

        content_hash = hashlib.sha256(
            f"{phone}:{normalized}".encode("utf-8")
        ).hexdigest()

        return f"message:content:{content_hash}"

    def is_duplicate(
        self,
        message_id: str,
        phone: str = "",
        text: str = ""
    ) -> bool:

        if not message_id:
            logger.warning("message_id vacío")
            return False

        try:

            # ── Deduplicación por contenido ─────────────

            if phone and text.strip():

                content_key = self._content_key(phone, text)

                created_by_content = redis_client.set(
                    content_key,
                    "1",
                    nx=True,
                    ex=5
                )

                if not created_by_content:

                    logger.warning(
                        f"Duplicado por contenido: "
                        f"{phone} - '{text[:30]}'"
                    )

                    return True

            # ── Deduplicación por ID ────────────────────

            id_key = self._id_key(message_id)

            created_by_id = redis_client.set(
                id_key,
                "1",
                nx=True,
                ex=config.MESSAGE_DEDUP_TTL_SECONDS
            )

            if not created_by_id:

                logger.warning(
                    f"Duplicado por ID: {message_id}"
                )

                return True

            logger.info(
                f"Mensaje nuevo registrado: {message_id}"
            )

            return False

        except Exception:
            logger.exception(
                "Error usando Redis en MessageDeduplicator"
            )

            # Fail-open para no bloquear mensajes reales
            return False