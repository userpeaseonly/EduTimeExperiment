from fastapi import FastAPI, Request, Response, WebSocket, WebSocketDisconnect, status, HTTPException
from pydantic import ValidationError
from schemas import EventNotificationAlert
from starlette.datastructures import UploadFile, FormData
import json, textwrap, logging
import os
import uuid
import httpx # For async HTTP requests to download pictures

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from connection_manager import manager


app = FastAPI()

# --- Configuration for saving pictures ---
# Ensure this directory exists relative to where you run your FastAPI app.
# You might want to make this configurable via environment variables.
PICTURE_SAVE_DIR = "uploaded_pictures"
if not os.path.exists(PICTURE_SAVE_DIR):
    os.makedirs(PICTURE_SAVE_DIR)
    logger.info(f"Created picture save directory: {PICTURE_SAVE_DIR}")

# --- Helper Function for Pretty Logging ---
def pretty(e: EventNotificationAlert) -> str:
    """
    Extracts and formats key information from the EventNotificationAlert model for logging.
    """
    ace = e.access_controller_event
    summary_parts = [
        f"[{e.dateTime.isoformat()}]",
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

# --- New Helper Function: Download Picture from URL ---
async def download_picture_from_url(url: str, device_id: Optional[str] = None) -> Optional[str]:
    """
    Downloads a picture from a given URL and saves it locally.
    Returns the saved file path on success, None otherwise.
    """
    if not url:
        return None

    filename = f"{uuid.uuid4()}" # Generate a unique filename
    if device_id:
        filename = f"{device_id}_{filename}"

    # Try to determine extension from URL, default to .jpg
    _, ext = os.path.splitext(url.split('?')[0]) # Remove query params before splitting extension
    if not ext or len(ext) > 5: # Basic check for valid extension
        ext = ".jpg" # Default to JPG if no clear extension or too long

    file_path = os.path.join(PICTURE_SAVE_DIR, f"{filename}{ext}")

    try:
        async with httpx.AsyncClient(verify=False) as client: # verify=False for self-signed certs, consider removing in prod
            response = await client.get(url, timeout=10.0) # Add timeout
            response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)

            # Check content type if available to refine extension
            content_type = response.headers.get("Content-Type", "")
            if "image/jpeg" in content_type:
                ext = ".jpg"
            elif "image/png" in content_type:
                ext = ".png"
            elif "image/bmp" in content_type:
                ext = ".bmp"
            # Reconstruct file_path with correct extension if changed
            file_path = os.path.join(PICTURE_SAVE_DIR, f"{filename}{ext}")


            with open(file_path, "wb") as f:
                f.write(response.content)
            logger.info(f"Successfully downloaded picture from {url} to {file_path}")
            return file_path
    except httpx.RequestError as e:
        logger.error(f"Error requesting image from {url}: {e}")
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error downloading image from {url}: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        logger.error(f"Failed to download or save picture from {url}: {e}")
    return None

# --- Main Event Handling Endpoint ---
@app.post("/hik/events")
async def hik_events(request: Request):
    content_type = request.headers.get("content-type", "")
    raw_length = int(request.headers.get("content-length", 0))
    logger.info(f"Received {raw_length} bytes • Content-Type: {content_type}")

    event_payload_dict: dict = {}
    picture_file_path: Optional[str] = None # To store path of saved picture

    # --- Handle multipart/form-data ---
    if content_type.startswith("multipart/form-data"):
        try:
            form: FormData = await request.form()

            # Process event_log part
            event_part = form.get("event_log")
            if event_part is None:
                logger.error("Missing 'event_log' part in multipart/form-data.")
                raise HTTPException(status_code=400, detail="Missing 'event_log' part")

            if isinstance(event_part, UploadFile):
                event_json_bytes = await event_part.read()
            else:
                event_json_bytes = str(event_part).encode('utf-8')
            event_payload_dict = json.loads(event_json_bytes)
            logger.info("Successfully parsed event from multipart/form-data.")

            # Process picData part (if present)
            pic_part = form.get("picData")
            if pic_part and isinstance(pic_part, UploadFile):
                try:
                    # Generate a unique filename for the picture
                    filename = f"{uuid.uuid4()}"
                    # Try to infer extension, default to .jpg
                    if pic_part.filename:
                        _, ext = os.path.splitext(pic_part.filename)
                        if not ext: ext = ".jpg" # Default if no extension
                    else:
                        ext = ".jpg" # Default if no filename
                    
                    # Ensure the file is saved with a proper extension and path
                    file_path = os.path.join(PICTURE_SAVE_DIR, f"{filename}{ext}")
                    
                    # Read and save the picture content
                    picture_content = await pic_part.read()
                    with open(file_path, "wb") as f:
                        f.write(picture_content)
                    picture_file_path = file_path
                    logger.info(f"Successfully saved uploaded picture to {picture_file_path}")
                except Exception as e:
                    logger.error(f"Error saving picData part: {e}")
                    # Don't fail the entire request just for picture saving failure

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
    validated_event: EventNotificationAlert
    try:
        validated_event = EventNotificationAlert.model_validate(event_payload_dict)
        logger.info("Event payload validated successfully with Pydantic.")

        raw_json_str = json.dumps(event_payload_dict, indent=2)
        logger.info(f"\nRaw JSON:\n{textwrap.indent(raw_json_str, '  ')}")

        summary_str = pretty(validated_event)
        logger.info(f"Summary: {summary_str}")

        # --- Picture Management Logic ---
        # If picture wasn't directly uploaded in multipart, check for pictureURL
        if not picture_file_path and validated_event.access_controller_event.pictureURL:
            logger.info(f"Attempting to download picture from URL: {validated_event.access_controller_event.pictureURL}")
            picture_file_path = await download_picture_from_url(
                validated_event.access_controller_event.pictureURL,
                validated_event.deviceID # Pass deviceID for better filenames
            )

        # You can now use `picture_file_path` for database saving or further processing
        if picture_file_path:
            logger.info(f"Associated picture saved/downloaded at: {picture_file_path}")
            # Here you would typically save `picture_file_path` to your database
            # alongside other event details.
            # Example: db_event_record['picture_path'] = picture_file_path

        # --- BROADCAST TO WEBSOCKETS ---
        # You might want to include the local picture path in the broadcast message
        # if the client needs to display it from your server.
        broadcast_message = summary_str
        if picture_file_path:
            # Assuming you want to serve these pictures statically
            # You'd need a FastAPI static files setup for this.
            # E.g., app.mount("/pictures", StaticFiles(directory="uploaded_pictures"), name="pictures")
            # Then broadcast_message += f" LocalPic=/pictures/{os.path.basename(picture_file_path)}"
            broadcast_message += f" LocalPic={os.path.basename(picture_file_path)}" # Send just the filename for client

        await manager.broadcast(broadcast_message)

    except ValidationError as e:
        logger.error(f"Pydantic validation error: {e.errors()}")
        raise HTTPException(status_code=422, detail=f"Validation Error: {e.errors()}")
    except Exception as e:
        logger.error(f"Unexpected error during event processing or broadcasting: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

    return Response(status_code=status.HTTP_200_OK)

# --- WebSocket Endpoint (same as before) ---
@app.websocket("/ws/events")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for clients to connect and receive event updates.
    """
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_bytes() # Or `receive_text()`, or `receive_json()`
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("WebSocket client disconnected.")
    except Exception as e:
        logger.error(f"Error in WebSocket connection: {e}")
        manager.disconnect(websocket)

# --- To serve saved pictures statically ---
from fastapi.staticfiles import StaticFiles
app.mount("/pictures", StaticFiles(directory=PICTURE_SAVE_DIR), name="pictures")