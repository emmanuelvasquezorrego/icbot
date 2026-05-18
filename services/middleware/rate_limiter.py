"""
Rate limiter distribuido usando Redis.
"""

import re
import time
import logging
import config

from services.clients.redis_client import redis_client

logger = logging.getLogger(__name__)

_LUA_SCRIPT = """
local block_key  = KEYS[1]
local window_key = KEYS[2]
local now        = tonumber(ARGV[1])
local cutoff     = tonumber(ARGV[2])
local limit      = tonumber(ARGV[3])
local window_ttl = tonumber(ARGV[4])
local block_ttl  = tonumber(ARGV[5])

-- 1. Verificar bloqueo activo
if redis.call('EXISTS', block_key) == 1 then
    return 2 --silent
end

-- 2. Limpiar mensajes fuera de la ventana
redis.call('ZREMRANGEBYSCORE', window_key, 0, cutoff)

-- 3. Contar mensajes recientes
local count = redis.call('ZCARD', window_key)

-- 4. Verificar límite
if count >= limit then
    redis.call('SETEX', block_key, block_ttl, '1')
    return 1 --notify
end

-- 5. Registrar mensaje actual (score único para evitar colisiones)
redis.call('ZADD', window_key, now, tostring(now) .. ':' .. tostring(count))
redis.call('EXPIRE', window_key, window_ttl)

return 0 --ok
"""


class RateLimiter:

    def __init__(self):
        self._script = redis_client.register_script(_LUA_SCRIPT)

    @staticmethod
    def _normalize_phone(phone: str) -> str:

        if not phone:
            return ""

        return re.sub(r"[^0-9]", "", phone)

    def _window_key(self, phone: str) -> str:
        return f"ratelimit:{phone}"

    def _block_key(self, phone: str) -> str:
        return f"ratelimit:block:{phone}"

    def is_allowed(self, phone: str) -> tuple[bool, str | None]:

        phone = self._normalize_phone(phone)
        now   = int(time.time() * 1000)  # tiempo en ms

        result = self._script(
            keys=[
                self._block_key(phone),
                self._window_key(phone),
            ],
            args=[
                now,                                              # tiempo actual
                now - (config.RATE_LIMIT_WINDOW_SECONDS * 1000),  # cutoff
                config.RATE_LIMIT_MAX_MESSAGES,                   # límite
                config.RATE_LIMIT_WINDOW_SECONDS,                 # TTL ventana / sigue en segundos (REDIS EXPIRE)
                config.RATE_LIMIT_BLOCK_SECONDS,                  # TTL bloqueo
            ]
        )

        if result == 0:
            return True, None

        if result == 1:
            logger.warning(f"Rate limit para {phone}")
            return False, "notify"

        # silent
        return False, "silent"