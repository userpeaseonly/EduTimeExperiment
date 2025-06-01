from fastapi import FastAPI, Request, Response, WebSocket, WebSocketDisconnect, status
from starlette.datastructures import UploadFile, FormData
import json, textwrap, logging
from collections import deque

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from connection_manager import manager


app = FastAPI()
q = deque()

def pretty(e: dict) -> str:
    ac  = e.get("AccessControllerEvent", {})
    return (
        f"[{e.get('dateTime')}] {e.get('deviceID')} {e.get('eventType')}"
        f"  major={ac.get('majorEventType')}  sub={ac.get('subEventType')}"
        f"  mode={ac.get('currentVerifyMode')}"
    )

@app.post("/hik/events")
async def hik_events(request: Request):
    ct = request.headers.get("content-type", "")
    raw_len = int(request.headers.get("content-length", 0))
    print(f"Received {raw_len} bytes • {ct}")

    # ── multipart ───────────────────────────────────────────────
    if ct.startswith("multipart/form-data"):
        form: FormData = await request.form()
        part = form["event_log"]

        if isinstance(part, UploadFile):
            event_json_bytes = await part.read()
        else:                       
            event_json_bytes = str(part).encode()

        event = json.loads(event_json_bytes)

    # ── plain JSON ──────────────────────────────────────────────
    elif ct.startswith("application/json"):
        event = await request.json()

    else:
        return Response(status_code=415)

    # ── log nicely ──────────────────────────────────────────────
    print("\nRaw JSON:\n", textwrap.indent(json.dumps(event, indent=2), "  "))
    print("Summary :", pretty(event))

    return Response(status_code=status.HTTP_200_OK)



@app.websocket("/ws/events")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for clients to connect and receive event updates.
    """
    await manager.connect(websocket)
    try:
        # Keep the connection open. You can also add logic here to receive
        # messages from clients if needed (e.g., for specific event subscriptions).
        while True:
            # This 'await' keeps the connection alive. If the client sends data,
            # it will be received here. For this "push-only" scenario,
            # you might just want it to wait or explicitly pass.
            # await websocket.receive_text() # If you expect messages from client
            await websocket.receive_bytes() # Or bytes, depending on client. Just to keep the loop open.
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("WebSocket client disconnected.")
    except Exception as e:
        logger.error(f"Error in WebSocket connection: {e}")
        manager.disconnect(websocket) # Ensure disconnection on other errors