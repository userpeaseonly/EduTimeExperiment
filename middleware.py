from starlette.types import ASGIApp, Receive, Scope, Send
from starlette.requests import Request
import logging
import json

logger = logging.getLogger("uvicorn.error")


class ASGIRawLoggerMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Capture body from receive
        body = b""
        more_body = True

        async def custom_receive():
            nonlocal body, more_body
            message = await receive()
            if message["type"] == "http.request":
                body += message.get("body", b"")
                more_body = message.get("more_body", False)
            return message

        # Log useful request info
        method = scope.get("method")
        path = scope.get("path")
        query = scope.get("query_string", b"").decode()
        headers = {k.decode(): v.decode() for k, v in scope.get("headers", [])}

        logger.info("====== Incoming Request ======")
        logger.info(f"Method: {method}")
        logger.info(f"Path: {path}")
        logger.info(f"Query: {query}")
        logger.info(f"Headers: {json.dumps(headers, indent=2)}")

        if "content-type" in headers:
            content_type = headers["content-type"]
            if "application/json" in content_type:
                try:
                    parsed_body = json.loads(body.decode())
                    logger.info("JSON Body:\n%s", json.dumps(parsed_body, indent=2))
                except Exception as e:
                    logger.warning("Could not parse JSON body: %s", e)
                    logger.info("Raw Body:\n%s", body.decode(errors="replace"))
            elif "multipart/form-data" in content_type or "application/x-www-form-urlencoded" in content_type:
                logger.info("Form/raw body received (binary or multipart): skipped detailed logging.")
            else:
                logger.info("Raw Body:\n%s", body.decode(errors="replace"))
        else:
            logger.info("No Content-Type header found, raw body:\n%s", body.decode(errors="replace"))

        logger.info("================================")

        await self.app(scope, lambda: custom_receive(), send)
