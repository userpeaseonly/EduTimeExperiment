from fastapi import FastAPI, Request, Response, status, WebSocket, WebSocketDisconnect, HTTPException
from starlette.datastructures import UploadFile, FormData
from pydantic import BaseModel, Field, ValidationError
import json
import textwrap
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI()

# --- Pydantic Models for Data Validation ---

class AccessControllerEvent(BaseModel):
    """
    Represents the AccessControllerEvent part of the Hikvision webhook payload.
    """
    majorEventType: int
    subEventType: int
    currentVerifyMode: int

class HikvisionEvent(BaseModel):
    """
    Represents the main Hikvision event payload structure.
    """
    dateTime: str
    deviceID: str
    eventType: str
    access_controller_event: AccessControllerEvent = Field(alias="AccessControllerEvent")

# --- Helper Function for Pretty Logging ---

def pretty(event_data: dict) -> str:
    """
    Extracts and formats key information from the event dictionary for logging.
    """
    ac = event_data.get("AccessControllerEvent", {})
    return (
        f"[{event_data.get('dateTime')}] {event_data.get('deviceID')} {event_data.get('eventType')}"
        f"  major={ac.get('majorEventType')}  sub={ac.get('subEventType')}"
        f"  mode={ac.get('currentVerifyMode')}"
    )

# --- WebSocket Manager ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected: {websocket.client.host}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected: {websocket.client.host}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        disconnected_connections = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except WebSocketDisconnect:
                disconnected_connections.append(connection)
                logger.warning(f"WebSocket connection lost during broadcast: {connection.client.host}")
            except Exception as e:
                logger.error(f"Error broadcasting to WebSocket {connection.client.host}: {e}")
                disconnected_connections.append(connection)

        # Remove disconnected connections
        for connection in disconnected_connections:
            self.active_connections.remove(connection)
            logger.info(f"Removed disconnected WebSocket: {connection.client.host}")


manager = ConnectionManager()

# --- FastAPI Endpoint for Webhook ---

@app.post("/hik/events")
async def hik_events(request: Request):
    """
    Handles incoming Hikvision webhook events.
    Supports both 'multipart/form-data' and 'application/json' content types.
    After processing, broadcasts the event to all connected WebSocket clients.
    """
    content_type = request.headers.get("content-type", "")
    raw_length = int(request.headers.get("content-length", 0))
    logger.info(f"Received {raw_length} bytes • Content-Type: {content_type}")

    event_payload: dict = {}

    # --- Handle multipart/form-data ---
    if content_type.startswith("multipart/form-data"):
        try:
            form: FormData = await request.form()
            event_part = form.get("event_log")

            if event_part is None:
                logger.error("Missing 'event_log' part in multipart/form-data.")
                raise HTTPException(status_code=400, detail="Missing 'event_log' part")

            if isinstance(event_part, UploadFile):
                event_json_bytes = await event_part.read()
            else:
                event_json_bytes = str(event_part).encode('utf-8')

            event_payload = json.loads(event_json_bytes)
            logger.info("Successfully parsed multipart/form-data.")

        except json.JSONDecodeError as e:
            logger.error(f"JSON decoding error in multipart/form-data: {e}")
            raise HTTPException(status_code=400, detail="Invalid JSON in 'event_log' part")
        except Exception as e:
            logger.error(f"Error processing multipart/form-data: {e}")
            raise HTTPException(status_code=400, detail="Failed to process multipart data")

    # --- Handle plain JSON ---
    elif content_type.startswith("application/json"):
        try:
            event_payload = await request.json()
            logger.info("Successfully parsed application/json.")
        except json.JSONDecodeError as e:
            logger.error(f"JSON decoding error in application/json: {e}")
            raise HTTPException(status_code=400, detail="Invalid JSON payload")
        except Exception as e:
            logger.error(f"Error processing application/json: {e}")
            raise HTTPException(status_code=400, detail="Failed to process JSON data")

    # --- Unsupported Content Type ---
    else:
        logger.warning(f"Unsupported content type: {content_type}")
        raise HTTPException(status_code=415, detail=f"Unsupported Media Type: {content_type}")

    # --- Validate and Log Event ---
    try:
        validated_event = HikvisionEvent(**event_payload)
        logger.info("Event payload validated successfully with Pydantic.")

        # Log the raw and summarized event data
        logger.info(f"\nRaw JSON:\n{textwrap.indent(json.dumps(event_payload, indent=2), '  ')}")
        logger.info(f"Summary: {pretty(event_payload)}")

        # --- Broadcast to WebSockets ---
        # You can choose to send the raw JSON, the pretty summary, or the validated Pydantic model's dict.
        # Sending the raw JSON (dumped as a string) is often flexible for client-side parsing.
        await manager.broadcast(json.dumps(event_payload))
        logger.info("Event broadcasted to connected WebSocket clients.")

    except ValidationError as e:
        logger.error(f"Pydantic validation error: {e.errors()}")
        raise HTTPException(status_code=422, detail=f"Validation Error: {e.errors()}")
    except Exception as e:
        logger.error(f"Unexpected error during event processing: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

    return Response(status_code=status.HTTP_200_OK)

# --- FastAPI WebSocket Endpoint ---

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