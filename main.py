from fastapi import FastAPI, Request, Response, status, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError
from schemas.events import EventNotificationAlert 
from starlette.datastructures import UploadFile, FormData
from sqlalchemy.ext.asyncio import AsyncSession
import json, textwrap, logging

from db import get_async_db
from utils import pretty

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


app = FastAPI()


app.mount("/images", StaticFiles(directory="event_images"), name="images")


import os
from datetime import datetime
from fastapi import File, UploadFile
from fastapi.responses import JSONResponse

# Directory to save uploaded images
SAVE_DIR = "event_images"
os.makedirs(SAVE_DIR, exist_ok=True)


@app.post("/hik/events")
async def receive_event(
    request: Request,
    Picture: UploadFile = File(None),
    VisibleLight: UploadFile = File(None),
    Thermal: UploadFile = File(None),
):
    try:
        form = await request.form()
        
        # Find the JSON part from the unnamed part
        json_string = None
        for key in form.keys():
            if not isinstance(form[key], UploadFile) and "eventType" in str(form[key]):
                json_string = form[key]
                break
        
        if not json_string:
            return JSONResponse(status_code=400, content={"error": "No valid JSON data found"})

        # Parse the event data
        event_data = json.loads(json_string)
        print("🔔 Received Event:")
        print(json.dumps(event_data, indent=2))

        # Save image files
        def save_file(file: UploadFile, name: str):
            if file:
                filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{name}"
                file_path = os.path.join(SAVE_DIR, filename)
                with open(file_path, "wb") as f:
                    f.write(file.file.read())
                print(f"📸 Saved {name} -> {file_path}")

        save_file(Picture, "Picture.jpg")
        save_file(VisibleLight, "VisibleLight.jpg")
        save_file(Thermal, "Thermal.jpg")

        return {"status": "received", "event": event_data.get("eventType", "unknown")}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


# @app.post("/hik/events")
# async def hik_events(request: Request, db: AsyncSession = Depends(get_async_db)):
#     content_type = request.headers.get("content-type", "")
#     raw_length = int(request.headers.get("content-length", 0))
#     logger.info(f"Received {raw_length} bytes • Content-Type: {content_type}")

#     event_payload_dict: dict = {}

#     if content_type.startswith("multipart/form-data"):
#         try:
#             form: FormData = await request.form()
#             event_part = form.get("event_log")

#             if event_part is None:
#                 logger.error("Missing 'event_log' part in multipart/form-data.")
#                 raise HTTPException(status_code=400, detail="Missing 'event_log' part")

#             if isinstance(event_part, UploadFile):
#                 event_json_bytes = await event_part.read()
#             else:
#                 event_json_bytes = str(event_part).encode('utf-8')

#             event_payload_dict = json.loads(event_json_bytes)
#             logger.info("Successfully parsed multipart/form-data.")
#             logger.debug(f"Form data received (parsed dict): {event_payload_dict}")

#         except json.JSONDecodeError as e:
#             logger.error(f"JSON decoding error in multipart/form-data: {e}")
#             raise HTTPException(status_code=400, detail="Invalid JSON in 'event_log' part")
#         except Exception as e:
#             logger.error(f"Error processing multipart/form-data: {e}")
#             raise HTTPException(status_code=400, detail="Failed to process multipart data")

#     elif content_type.startswith("application/json"):
#         try:
#             event_payload_dict = await request.json()
#             logger.info("Successfully parsed application/json.")
#         except json.JSONDecodeError as e:
#             logger.error(f"JSON decoding error in application/json: {e}")
#             raise HTTPException(status_code=400, detail="Invalid JSON payload")
#         except Exception as e:
#             logger.error(f"Error processing application/json: {e}")
#             raise HTTPException(status_code=400, detail="Failed to process JSON data")
#     else:
#         logger.warning(f"Unsupported content type: {content_type}")
#         raise HTTPException(status_code=415, detail=f"Unsupported Media Type: {content_type}")

#     try:
#         validated_event = EventNotificationAlert.model_validate(event_payload_dict)
#         logger.info("Event payload validated successfully with Pydantic.")

#         raw_json_str = json.dumps(event_payload_dict, indent=2)
#         logger.info(f"\nRaw JSON:\n{textwrap.indent(raw_json_str, '  ')}")

#         summary_str = pretty(validated_event)
#         logger.info(f"Summary: {summary_str}")
        
#     except ValidationError as e:
#         logger.error(f"Pydantic validation error: {e.errors()}")
#         raise HTTPException(status_code=422, detail=f"Validation Error: {e.errors()}")
#     except Exception as e:
#         logger.error(f"Unexpected error during event processing or broadcasting: {e}")
#         raise HTTPException(status_code=500, detail="Internal Server Error")

#     return Response(status_code=status.HTTP_200_OK)

