import logging
from urllib.parse import quote

from fastapi import Request

logger = logging.getLogger(__name__)


def task_cache_key_builder(
    func, namespace: str, request: Request, response=None, *args, **kwargs
) -> str:
    raw = f"{request.url.path}?{request.url.query}"
    safe = quote(raw, safe="")
    key = f"{namespace}:{safe}"

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("Generated cache key: %s", key)
    return key
