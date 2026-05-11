"""
Rate limiter para proteger el chatbot contra spam.
Implementación en memoria con ventana deslizante.
Thread-safe.
"""

import re
import threading
import time
import logging
from collections import defaultdict, deque
import config

logger = logging.getLogger(__name__)


class RateLimiter:

    """
    Limita la cantidad de mensajes por usuario en una ventana de tiempo con sliding window.
    """

    @staticmethod
    def _normalize_phone(phone: str) -> str:

        """Normaliza el número de teléfono eliminando espacios, '+' y dígitos no significativos."""

        if not phone:
            return ""
        
        # Eliminar espacios y caracteres no numéricos
        normalized = re.sub(r'[^0-9]', '', phone)
        return normalized

    def __init__(self):
        # Deque de timestamps
        self.user_windows: dict[str, deque] = defaultdict(lambda: deque())

        self.lock = threading.Lock()

        # Timestamp hasta cuándo está bloqueado
        self.blocked_until: dict[str, float] = {}

        # Si ya se notificó el bloqueo
        self.notified_block: dict[str, bool] = {}

    def is_allowed(self, phone: str) -> tuple[bool, str | None]:

        """
        Retorna:
        - (True, None) → permitido
        - (False, "notify") → bloquear + enviar warning
        - (False, "silent") → bloquear sin enviar nada
        """

        phone = self._normalize_phone(phone)

        with self.lock:
            now = time.time()

            # Si está bloqueado
            if phone in self.blocked_until:
                if now < self.blocked_until[phone]:
                    # Si ya está bloqueado, no enviar más notificaciones
                    return False, "silent"
                else:
                    # Al finalizar el bloqueo, limpiar estado
                    del self.blocked_until[phone]
                    self.notified_block.pop(phone, None)

            # Limpiar ventana
            window = self.user_windows[phone]
            cutoff = now - config.RATE_LIMIT_WINDOW_SECONDS

            while window and window[0] < cutoff:
                window.popleft()

            # Verificar límite
            if len(window) >= config.RATE_LIMIT_MAX_MESSAGES:

                # Activar bloqueo
                self.blocked_until[phone] = now + config.RATE_LIMIT_BLOCK_SECONDS

                logger.warning(
                    f"Rate limit para {phone}: "
                    f"{len(window)} mensajes en {config.RATE_LIMIT_WINDOW_SECONDS}s"
                )

                # Primera vez que se bloquea envia warning
                if not self.notified_block.get(phone, False):
                    self.notified_block[phone] = True
                    return False, "notify"

                # Si ya se notificó no enviar nada
                return False, "silent"

            # Registrar mensaje
            window.append(now)

            return True, None

    def get_usage(self, phone: str) -> dict:

        """Obtener estadísticas de uso."""

        phone = self._normalize_phone(phone)

        with self.lock:
            now = time.time()
            window = self.user_windows.get(phone, deque())
            cutoff = now - config.RATE_LIMIT_WINDOW_SECONDS

            recent = sum(1 for t in window if t > cutoff)

            return {
                "messages_in_window": recent,
                "limit": config.RATE_LIMIT_MAX_MESSAGES,
                "window_seconds": config.RATE_LIMIT_WINDOW_SECONDS,
                "is_blocked": phone in self.blocked_until
                and now < self.blocked_until.get(phone, 0),
            }