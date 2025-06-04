from fastapi import FastAPI, Request, Response, WebSocket, WebSocketDisconnect, status, HTTPException
from pydantic import ValidationError
from schemas import EventNotificationAlert 
from starlette.datastructures import UploadFile, FormData
import json, textwrap, logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from connection_manager import manager


app = FastAPI()


# --- Helper Function for Pretty Logging (updated for new schema) ---
def pretty(e: EventNotificationAlert) -> str:
    """
    Extracts and formats key information from the EventNotificationAlert model for logging.
    """
    # Accessing fields directly from the validated Pydantic model
    ace = e.access_controller_event
    summary_parts = [
        f"[{e.dateTime.isoformat()}]", # datetime object
        f"DevID={e.deviceID or 'N/A'}",
        f"Type={e.eventType}",
        f"Major={ace.majorEventType}",
        f"Sub={ace.subEventType}",
        f"Mode={ace.currentVerifyMode or 'N/A'}"
    ]
    if ace.employeeNo:
        summary_parts.append(f"EmpNo={ace.employeeNo}")
    if ace.name:
        summary_parts.append(f"Name='{ace.name}'")
    if ace.cardNo:
        summary_parts.append(f"CardNo={ace.cardNo}")
    if ace.pictureURL:
        summary_parts.append(f"PicURL='{ace.pictureURL}'")

    return " ".join(summary_parts)


@app.post("/hik/events")
async def hik_events(request: Request):
    """
    Handles incoming Hikvision webhook events.
    Supports both 'multipart/form-data' and 'application/json' content types.
    Parses and validates the event using Pydantic, then broadcasts to WebSockets.
    """
    content_type = request.headers.get("content-type", "")
    raw_length = int(request.headers.get("content-length", 0))
    logger.info(f"Received {raw_length} bytes • Content-Type: {content_type}")

    event_payload_dict: dict = {} # Will hold the raw dictionary payload

    # --- Handle multipart/form-data ---
    if content_type.startswith("multipart/form-data"):
        try:
            form: FormData = await request.form()
            # Hikvision often sends the event JSON in a part named "event_log"
            event_part = form.get("event_log")

            if event_part is None:
                logger.error("Missing 'event_log' part in multipart/form-data.")
                raise HTTPException(status_code=400, detail="Missing 'event_log' part")

            if isinstance(event_part, UploadFile):
                event_json_bytes = await event_part.read()
            else:
                # Fallback for if 'event_log' is sent as a plain string field, though less common for JSON
                event_json_bytes = str(event_part).encode('utf-8')

            event_payload_dict = json.loads(event_json_bytes)
            logger.info("Successfully parsed multipart/form-data.")
            logger.debug(f"Form data received (parsed dict): {event_payload_dict}") # Use debug for verbose output

        except json.JSONDecodeError as e:
            logger.error(f"JSON decoding error in multipart/form-data: {e}")
            raise HTTPException(status_code=400, detail="Invalid JSON in 'event_log' part")
        except Exception as e:
            logger.error(f"Error processing multipart/form-data: {e}")
            raise HTTPException(status_code=400, detail="Failed to process multipart data")

    # --- Handle plain JSON ---
    elif content_type.startswith("application/json"):
        try:
            event_payload_dict = await request.json()
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

    # --- Validate and Log Event with Pydantic ---
    validated_event: EventNotificationAlert # Declare type for clarity
    try:
        # Use the EventNotificationAlert model to validate the parsed dictionary
        validated_event = EventNotificationAlert.model_validate(event_payload_dict)
        logger.info("Event payload validated successfully with Pydantic.")

        # Log the raw JSON (for full context) and a pretty summary
        raw_json_str = json.dumps(event_payload_dict, indent=2)
        logger.info(f"\nRaw JSON:\n{textwrap.indent(raw_json_str, '  ')}")

        # Use the validated Pydantic model for pretty logging
        summary_str = pretty(validated_event)
        logger.info(f"Summary: {summary_str}")

        # --- BROADCAST TO WEBSOCKETS ---
        # You can choose what to broadcast:
        # 1. A pretty, human-readable summary (as currently implemented)
        await manager.broadcast(summary_str)
        # 2. The full raw JSON string received from Hikvision
        # await manager.broadcast(raw_json_str)
        # 3. The validated Pydantic model converted back to JSON (best for structured client-side parsing)
        # await manager.broadcast(validated_event.model_dump_json(by_alias=True, indent=2))

    except ValidationError as e:
        logger.error(f"Pydantic validation error: {e.errors()}")
        raise HTTPException(status_code=422, detail=f"Validation Error: {e.errors()}")
    except Exception as e:
        logger.error(f"Unexpected error during event processing or broadcasting: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

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