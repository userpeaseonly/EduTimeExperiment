import os
import json
import logging
from datetime import datetime
from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError, TypeAdapter

from schemas.events import HeartbeatInfo, EventNotificationAlert, EventUnion
from core import config
from utils import log_pretty_event
from operations import operations as op

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI()
app.mount("/images", StaticFiles(directory="event_images"), name="images")

# Ensure save directory exists
os.makedirs(config.SAVE_DIR, exist_ok=True)


@app.post("/hik/events")
async def receive_event(
    request: Request,
    Picture: UploadFile = File(None),
) -> dict[str, str]:
    try:
        form = await request.form()

        # Extract JSON part from form data
        json_string = next(
            (v for k, v in form.items() if not isinstance(v, UploadFile) and "eventType" in str(v)),
            None
        )
        if not json_string:
            return JSONResponse(status_code=400, content={"error": "No valid event JSON found."})

        event_data = json.loads(json_string)

        # Parse and log event
        try:
            event = TypeAdapter(EventUnion).validate_python(**event_data)
            if isinstance(event, HeartbeatInfo):
                logger.info(event)
            elif isinstance(event, EventNotificationAlert):
                log_pretty_event(event)
        except ValidationError as ve:
            logger.error("Validation failed for EventNotificationAlert.")
            return JSONResponse(status_code=422, content={"error": str(ve)})

        # Save image
        picture_path = op.save_image(Picture, "Picture")

        # Save raw JSON to disk
        event_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        event_filename = f"{event_id}_{event_data.get('eventType', 'Unknown')}.json"
        json_path = os.path.join(config.SAVE_DIR, event_filename)
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(event_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Event saved to file: {event_filename}")
        return {"status": "ok", "saved": event_filename}

    except Exception as e:
        logger.exception("Error handling /hik/events")
        logger.error(f"Error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})
