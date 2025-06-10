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


def pretty(e: EventNotificationAlert) -> str:
    """
    Extracts and formats key information from the EventNotificationAlert model for logging.
    """
    ace = e.access_controller_event
    summary_parts = [
        f"[{e.date_time.isoformat()}]",
        f"DevID={e.device_id or 'N/A'}",
        f"Type={e.event_type}",
        f"Major={ace.major_event_type}",
        f"Sub={ace.sub_event_type}",
        f"Mode={ace.current_verify_mode or 'N/A'}"
    ]
    if ace.employee_no:
        summary_parts.append(f"EmpNo={ace.employee_no}")
    if ace.name:
        summary_parts.append(f"Name='{ace.name}'")
    if ace.card_no:
        summary_parts.append(f"CardNo={ace.card_no}")
    if ace.picture_url:
        summary_parts.append(f"PicURL='{ace.picture_url}'")

    return " ".join(summary_parts)


@app.post("/hik/events")
async def hik_events(request: Request):
    content_type = request.headers.get("content-type", "")
    raw_length = int(request.headers.get("content-length", 0))
    logger.info(f"Received {raw_length} bytes • Content-Type: {content_type}")

    event_payload_dict: dict = {}

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

            event_payload_dict = json.loads(event_json_bytes)
            logger.info("Successfully parsed multipart/form-data.")
            logger.debug(f"Form data received (parsed dict): {event_payload_dict}")

        except json.JSONDecodeError as e:
            logger.error(f"JSON decoding error in multipart/form-data: {e}")
            raise HTTPException(status_code=400, detail="Invalid JSON in 'event_log' part")
        except Exception as e:
            logger.error(f"Error processing multipart/form-data: {e}")
            raise HTTPException(status_code=400, detail="Failed to process multipart data")

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
    else:
        logger.warning(f"Unsupported content type: {content_type}")
        raise HTTPException(status_code=415, detail=f"Unsupported Media Type: {content_type}")

    try:
        validated_event = EventNotificationAlert.model_validate(event_payload_dict)
        logger.info("Event payload validated successfully with Pydantic.")

        raw_json_str = json.dumps(event_payload_dict, indent=2)
        logger.info(f"\nRaw JSON:\n{textwrap.indent(raw_json_str, '  ')}")

        summary_str = pretty(validated_event)
        logger.info(f"Summary: {summary_str}")
        
    except ValidationError as e:
        logger.error(f"Pydantic validation error: {e.errors()}")
        raise HTTPException(status_code=422, detail=f"Validation Error: {e.errors()}")
    except Exception as e:
        logger.error(f"Unexpected error during event processing or broadcasting: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

    return Response(status_code=status.HTTP_200_OK)

