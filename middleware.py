import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

class LogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request : Request, call_next):
        logger.info(f'-> {request.method} {request.url}')
        response = await call_next(request)
        if response.status_code >= 400:
            logger.error(f'<- {response.status_code} {request.method} {request.url}')
        else:
            logger.info(f'<- {response.status_code} {request.method} {request.url}')
        return response