from typing import Callable
from starlette.types import ASGIApp, Receive, Scope, Send
import logging

logger = logging.getLogger("uvicorn.error")


class ASGIRawLoggerMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        logger.info("Request: %s", scope)
        await self.app(scope, receive, send)
        logger.info("Response: %s", scope)