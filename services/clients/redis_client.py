"""
Cliente Redis compartido.
"""

import redis
import logging
import config

logger = logging.getLogger(__name__)

redis_client = redis.Redis(
    host=config.REDIS_HOST,
    port=config.REDIS_PORT,
    db=config.REDIS_DB,
    decode_responses=config.REDIS_DECODE_RESPONSES,
)

try:
    redis_client.ping()
    logger.info("Conectado a Redis ✓")

except Exception:
    logger.exception("No se pudo conectar a Redis")
    raise