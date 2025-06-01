from fastapi import FastAPI, Request, Response, status, HTTPException
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
# These models define the expected structure of your incoming JSON payload.
# They provide automatic validation and better type hinting.

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
    Using 'Field(..., alias="AccessControllerEvent")' ensures Pydantic
    correctly maps the JSON key (AccessControllerEvent) to the Python attribute.
    """
    dateTime: str
    deviceID: str
    eventType: str
    AccessControllerEvent: AccessControllerEvent = Field(alias="AccessControllerEvent")

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

# --- FastAPI Endpoint ---

@app.post("/hik/events")
async def hik_events(request: Request):
    """
    Handles incoming Hikvision webhook events.
    Supports both 'multipart/form-data' and 'application/json' content types.
    """
    content_type = request.headers.get("content-type", "")
    raw_length = int(request.headers.get("content-length", 0))
    logger.info(f"Received {raw_length} bytes • Content-Type: {content_type}")

    event_payload: dict = {}

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
        # Use Pydantic model to validate the parsed event_payload
        validated_event = HikvisionEvent(**event_payload)
        logger.info("Event payload validated successfully with Pydantic.")

        # Log the raw and summarized event data
        logger.info(f"\nRaw JSON:\n{textwrap.indent(json.dumps(event_payload, indent=2), '  ')}")
        # Pass the original dictionary for the pretty function as it expects a dict
        logger.info(f"Summary: {pretty(event_payload)}")

    except ValidationError as e:
        logger.error(f"Pydantic validation error: {e.errors()}")
        raise HTTPException(status_code=422, detail=f"Validation Error: {e.errors()}")
    except Exception as e:
        logger.error(f"Unexpected error during event processing: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

    return Response(status_code=status.HTTP_200_OK)