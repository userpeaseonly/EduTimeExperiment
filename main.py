import os
from datetime import datetime
from fastapi import FastAPI, Request, Response, status, HTTPException, Depends, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
import json, textwrap, logging

from schemas.events import EventNotificationAlert 

from core import config
from db import get_async_db
from utils import pretty



# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


app = FastAPI()

app.mount("/images", StaticFiles(directory="event_images"), name="images")

os.makedirs(config.SAVE_DIR, exist_ok=True)



@app.post("/hik/events")
async def receive_event(
    request: Request,
    Picture: UploadFile = File(None),
):
    try:
        form = await request.form()

        # Find the JSON part
        json_string = next(
            (v for k, v in form.items() if not isinstance(v, UploadFile) and "eventType" in str(v)),
            None
        )

        if not json_string:
            return JSONResponse(status_code=400, content={"error": "No valid event JSON found."})

        event_data = json.loads(json_string)
        print("-------------------------------------------")
        print(event_data)
        print("-------------------------------------------")

        # Log the core fields if present
        logger.info(f"Received {event_data.get('eventType')} event from channel {event_data.get('channelID')}")

        # Save images if present
        def save_image(file: UploadFile, label: str):
            if file:
                filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{label}.jpg"
                path = os.path.join(config.SAVE_DIR, filename)
                with open(path, "wb") as f:
                    f.write(file.file.read())
                logger.info(f"Saved image: {path}")
                return path
            return None

        picture_path = save_image(Picture, "Picture")

        # Optionally attach image paths to event data
        event_data["_savedImages"] = {
            "Picture": picture_path,
        }

        # Save raw event to JSON file (or DB later)
        event_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        event_filename = f"{event_id}_{event_data.get('eventType', 'Unknown')}.json"
        with open(os.path.join(config.SAVE_DIR, event_filename), "w", encoding="utf-8") as f:
            json.dump(event_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Event saved: {event_filename}")

        return {"status": "ok", "saved": event_filename}

    except Exception as e:
        logger.exception("Error handling /hik/events")
        return JSONResponse(status_code=500, content={"error": str(e)})



