from fastapi import FastAPI, Request, Response, WebSocket, WebSocketDisconnect, status, HTTPException
from starlette.datastructures import UploadFile, FormData
import json, textwrap, logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from connection_manager import manager


app = FastAPI()



def pretty(event_data: dict) -> str:
    """
    Extracts and formats key information from the event dictionary for logging.
    Adjusted to handle the new nested structure of EventNotificationAlert.
    """
    alert = event_data.get("EventNotificationAlert", {})
    ac = alert.get("AccessControllerEvent", {})
    return (
        f"[{alert.get('dateTime')}] Device:{alert.get('devIndex')}"
        f" EventType:{alert.get('eventType')}"
        f" Major:{ac.get('majorEventType')} Sub:{ac.get('subEventType')}"
        f" CardNo:{ac.get('cardNo')} EmpNo:{ac.get('employeeNo')}"
        f" PictureURL:{ac.get('pictureURL')}"
    )

# def pretty(e: dict) -> str:
#     ac  = e.get("AccessControllerEvent", {})
#     return (
#         f"[{e.get('dateTime')}] {e.get('deviceID')} {e.get('eventType')}"
#         f"  major={ac.get('majorEventType')}  sub={ac.get('subEventType')}"
#         f"  mode={ac.get('currentVerifyMode')}"
#     )



@app.post("/hik/events")
async def hik_events(request: Request):
    """
    Handles incoming Hikvision webhook events, validates them with Pydantic,
    logs them, and broadcasts a summary to all connected WebSocket clients.
    """
    content_type = request.headers.get("content-type", "")
    raw_length = int(request.headers.get("content-length", 0))
    logger.info(f"Received {raw_length} bytes • Content-Type: {content_type}")

    event_payload: dict = {} # Initialize as an empty dict

    # --- 1. Extract Raw Event Payload based on Content-Type ---
    if content_type.startswith("multipart/form-data"):
        try:
            form: FormData = await request.form()
            event_part = form.get("event_log") # Hikvision typically sends event_log

            if event_part is None:
                logger.error("400 Bad Request: Missing 'event_log' part in multipart/form-data.")
                raise HTTPException(status_code=400, detail="Missing 'event_log' part in multipart/form-data")

            if isinstance(event_part, UploadFile):
                event_json_bytes = await event_part.read()
            else:
                event_json_bytes = str(event_part).encode('utf-8')

            event_payload = json.loads(event_json_bytes)
            logger.info("Successfully extracted event from multipart/form-data.")

        except json.JSONDecodeError as e:
            logger.error(f"400 Bad Request: JSON decoding error in multipart/form-data: {e}")
            raise HTTPException(status_code=400, detail="Invalid JSON in 'event_log' part")
        except Exception as e:
            logger.error(f"400 Bad Request: Error processing multipart/form-data: {e}")
            raise HTTPException(status_code=400, detail="Failed to process multipart data")

    elif content_type.startswith("application/json"):
        try:
            event_payload = await request.json()
            logger.info("Successfully extracted event from application/json.")
        except json.JSONDecodeError as e:
            logger.error(f"400 Bad Request: JSON decoding error in application/json: {e}")
            raise HTTPException(status_code=400, detail="Invalid JSON payload")
        except Exception as e:
            logger.error(f"400 Bad Request: Error processing application/json: {e}")
            raise HTTPException(status_code=400, detail="Failed to process JSON data")

    else:
        logger.warning(f"415 Unsupported Media Type: {content_type}")
        raise HTTPException(status_code=415, detail=f"Unsupported Media Type: {content_type}")

    # --- 2. Validate Event Payload with Pydantic ---
    validated_payload: HikvisionWebhookPayload
    try:
        validated_payload = HikvisionWebhookPayload.model_validate(event_payload)
        logger.info("Event payload validated successfully with Pydantic.")

        # At this point, 'validated_payload' is a fully type-hinted and validated Pydantic model
        # You can now safely access its attributes like:
        # alert = validated_payload.event_notification_alert
        # ace = alert.access_controller_event
        # print(ace.employeeNo) # and so on.

        # --- Operations (e.g., saving to database) ---
        # You would typically perform database operations here
        # Example: save_event_to_db(validated_payload)
        # You can convert back to a dictionary for ORMs if needed:
        # event_dict_for_db = validated_payload.model_dump(by_alias=True)
        # Or just access specific fields:
        # employee_number = ace.employeeNo
        # picture_url = ace.pictureURL


    except ValidationError as e:
        logger.error(f"422 Validation Error: Pydantic validation failed for incoming event: {e.errors()}")
        raise HTTPException(status_code=422, detail=f"Validation Error: {e.errors()}")
    except Exception as e:
        logger.error(f"500 Internal Server Error: An unexpected error occurred during validation: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error during validation")

    # --- 3. Log and Broadcast Event ---
    try:
        # Log the raw JSON (useful for debugging)
        raw_json_str = json.dumps(event_payload, indent=2)
        logger.info(f"\nRaw JSON (from incoming request):\n{textwrap.indent(raw_json_str, '  ')}")

        # Log a pretty summary
        summary_str = pretty(event_payload) # Use the original payload dict for pretty, as it's simpler
        logger.info(f"Summary: {summary_str}")

        # Broadcast the summary to all connected WebSocket clients
        await manager.broadcast(summary_str)
        logger.info("Event summary broadcasted to WebSocket clients.")

    except Exception as e:
        logger.error(f"500 Internal Server Error: Error during logging or broadcasting event: {e}")
        # Decide if you want to return a 500 here or still send 200 OK
        # If the event was processed but broadcast failed, 200 OK might still be appropriate.
        # For simplicity, we'll keep the 200 OK if validation passed.

    return Response(status_code=status.HTTP_200_OK)


# @app.post("/hik/events")
# async def hik_events(request: Request):
#     ct = request.headers.get("content-type", "")


#     if ct.startswith("multipart/form-data"):
#         form: FormData = await request.form()
#         part = form["event_log"]
#         print("Form data received -- -- -- -- -- -- --: \n", part)

#         if isinstance(part, UploadFile):
#             event_json_bytes = await part.read()
#         else:                       
#             event_json_bytes = str(part).encode()

#         event = json.loads(event_json_bytes)
#         logger.info(f"Parsed event from multipart/form-data: {event}")

#     # ── plain JSON ──────────────────────────────────────────────
#     elif ct.startswith("application/json"):
#         event = await request.json()

#     else:
#         return Response(status_code=415)

#     print("Summary :", pretty(event))
    
#     # Broadcast the event to all connected WebSocket clients
#     try:
#         await manager.broadcast(pretty(event))
#     except Exception as e:
#         logger.error(f"Error broadcasting event: {e}")
        
#     return Response(status_code=status.HTTP_200_OK)



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