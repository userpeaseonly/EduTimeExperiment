import os
import json
import logging
from datetime import datetime
from fastapi import FastAPI, Request, UploadFile, File, Depends, status
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError, TypeAdapter
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.events import HeartbeatInfo, EventNotificationAlert, EventUnion
from core import config
from utils import log_pretty_event, log_pretty_heartbeat
from operations import crud, operations
from db import get_async_db
from models import event as models
from contextlib import asynccontextmanager

from middleware import ASGIRawLoggerMiddleware

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up the FastAPI application.")
    yield
    logger.info("Shutting down the FastAPI application.")

app = FastAPI(lifespan=lifespan)

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
        
        # Save image
        path_name = await operations.save_image(Picture, "Picture")
        logger.info(f"Image saved at: {path_name}")

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
                await crud.create_heartbeat(event_in, db)
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
                    purpose=models.PersonPurpose.ATTENDANCE if event.access_controller_event.person_name else models.PersonPurpose.INFORMATION,
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
                    picture_url=path_name
                )
                await crud.create_event(event_in, db)
            else:
                logger.warning("Received unknown event type.")
        except ValidationError as ve:
            logger.error(f"Validation error: {ve}")
            return JSONResponse(content={"error": str(ve)}, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


        return JSONResponse(content={"status": "ok"}, status_code=status.HTTP_200_OK)

    except Exception as e:
        logger.exception("Error handling /hik/events")
        logger.error(f"Error: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
