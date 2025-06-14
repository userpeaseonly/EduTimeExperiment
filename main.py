import os
import json
import logging
from datetime import datetime
from fastapi import FastAPI, Request, UploadFile, File, Depends
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError, TypeAdapter
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.events import HeartbeatInfo, EventNotificationAlert, EventUnion
from core import config
from utils import log_pretty_event, log_pretty_heartbeat
from operations import operations as op
from operations import crud
from db import get_async_db
from models import event as models

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
os.makedirs(config.LOGS_DIR, exist_ok=True)


@app.post("/hik/events")
async def receive_event(
    request: Request,
    Picture: UploadFile = File(None),
    db: AsyncSession = Depends(get_async_db)
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
            event = TypeAdapter(EventUnion).validate_python(event_data)
            if isinstance(event, HeartbeatInfo):
                log_pretty_heartbeat(event)
                event_in = models.Heartbeat(
                    date_time=event.date_time,
                    active_post_count=event.active_post_count,
                    event_type=event.event_type,
                    event_state=event.event_state,
                    event_description=event.event_description
                )
                crud.create_heartbeat(event_in, db)
            elif isinstance(event, EventNotificationAlert):
                log_pretty_event(event)
                event_in = models.Event(
                    date_time=event.date_time,
                    active_post_count=event.active_post_count,
                    event_type=event.event_type,
                    event_state=event.event_state,
                    event_description=event.event_description,
                    device_id=event.device_id,
                    major_event=event.access_controller_event.major_event,
                    minor_event=event.access_controller_event.minor_event,
                    serial_no=event.access_controller_event.serial_no,
                    verify_no=event.access_controller_event.verify_no,
                    person_id=event.access_controller_event.person_id,
                    person_name=event.access_controller_event.person_name,
                    purpose=event.access_controller_event.purpose,
                    zone_type=event.access_controller_event.zone_type,
                    swipe_card_type=event.access_controller_event.swipe_card_type,
                    card_no=event.access_controller_event.card_no,
                    card_type=event.access_controller_event.card_type,
                    user_type=event.access_controller_event.user_type,
                    current_verify_mode=event.access_controller_event.current_verify_mode,
                    current_event=event.access_controller_event.current_event,
                    front_serial_no=event.access_controller_event.front_serial_no,
                    attendance_status=event.access_controller_event.attendance_status,
                    pictures_number=event.access_controller_event.pictures_number,
                    mask=event.access_controller_event.mask,
                    event_metadata=event.event_metadata
                )
                crud.create_event(event_in, db)
            else:
                logger.warning("Received unknown event type.")
        except ValidationError as ve:
            logger.error("Validation failed for EventNotificationAlert.")
            logger.error(f"Validation error: {ve}")
            return JSONResponse(status_code=422, content={"error": str(ve)})

        # Save image
        op.save_image(Picture, "Picture")

        # Save raw JSON to disk
        event_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        event_filename = f"{event_id}_{event_data.get('eventType', 'Unknown')}.json"
        json_path = os.path.join(config.LOGS_DIR, event_filename)
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(event_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Event saved to file: {event_filename}")
        return {"status": "ok", "saved": event_filename}

    except Exception as e:
        logger.exception("Error handling /hik/events")
        logger.error(f"Error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})
