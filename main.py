from fastapi import FastAPI, Request, Response, WebSocket, WebSocketDisconnect, status
from starlette.datastructures import UploadFile, FormData
import json, textwrap, logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from connection_manager import manager


app = FastAPI()


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


    if ct.startswith("multipart/form-data"):
        form: FormData = await request.form()
        part = form["event_log"]
        print("Form data received: \n", part)

        if isinstance(part, UploadFile):
            event_json_bytes = await part.read()
        else:                       
            event_json_bytes = str(part).encode()

        event = json.loads(event_json_bytes)
        logger.info(f"Parsed event from multipart/form-data: {event}")

    # ── plain JSON ──────────────────────────────────────────────
    elif ct.startswith("application/json"):
        event = await request.json()

    else:
        return Response(status_code=415)

    print("Summary :", pretty(event))
    
    # Broadcast the event to all connected WebSocket clients
    try:
        await manager.broadcast(pretty(event))
    except Exception as e:
        logger.error(f"Error broadcasting event: {e}")
        
    return Response(status_code=status.HTTP_200_OK)



@app.websocket("/ws/events")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for clients to connect and receive event updates.
    """
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_bytes() # Or bytes, depending on client. Just to keep the loop open.
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("WebSocket client disconnected.")
    except Exception as e:
        logger.error(f"Error in WebSocket connection: {e}")
        manager.disconnect(websocket)