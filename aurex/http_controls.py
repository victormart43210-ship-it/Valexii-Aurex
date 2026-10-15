"""Bounded per-process ingress control and content-free request audit records."""
import json
import logging
import time
import uuid

from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send

logger = logging.getLogger('aurex.http')


class HTTPControls:
    def __init__(self, app: ASGIApp, limit: int = 120) -> None:
        self.app = app
        self.limit = limit
        self.clients: dict[str, tuple[float, int]] = {}

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope['type'] != 'http':
            await self.app(scope, receive, send)
            return
        # Always generated server-side. Never echo arbitrary attacker-controlled header text.
        request_id = str(uuid.uuid4())
        scope.setdefault('state', {})['request_id'] = request_id
        started = time.monotonic()
        client = str((scope.get('client') or ('unknown',))[0])
        self.clients = {k: v for k, v in self.clients.items() if started - v[0] < 60}
        window, count = self.clients.get(client, (started, 0))
        response_status = 500

        async def tracked_send(message: Message) -> None:
            nonlocal response_status
            if message['type'] == 'http.response.start':
                response_status = message['status']
                message.setdefault('headers', []).append((b'x-request-id', request_id.encode()))
            await send(message)

        try:
            if count >= self.limit or (client not in self.clients and len(self.clients) >= 1024):
                await JSONResponse({'detail': 'Rate limit exceeded'}, status_code=429, headers={'Retry-After':'60'})(scope, receive, tracked_send)
            else:
                self.clients[client] = (window, count + 1)
                await self.app(scope, receive, tracked_send)
        finally:
            route = getattr(scope.get('route'), 'path', 'unmatched')
            logger.info(json.dumps({'request_id': request_id, 'route': route, 'status': response_status, 'duration_ms': round((time.monotonic()-started)*1000, 3)}))
