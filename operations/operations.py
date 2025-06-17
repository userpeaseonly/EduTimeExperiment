import os
import logging
import aiofiles
from datetime import datetime
from fastapi import UploadFile

from core import config

logger = logging.getLogger()

def save_image_sync(file: UploadFile | None, label: str) -> str | None:
    """Save uploaded image to disk."""
    if not file:
        return None
    filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{label}.jpg"
    path = os.path.join(config.SAVE_DIR, filename)
    with open(path, "wb") as f:
        f.write(file.file.read())
    logger.info(f"Saved image: {path}")
    return path

async def save_image(file: UploadFile | None, label: str) -> str | None:
    if not file:
        return None
    filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{label}.jpg"
    path = os.path.join(config.SAVE_DIR, filename)
    
    try:
        content = await file.read()
        async with aiofiles.open(path, "wb") as f:
            await f.write(content)
        logger.info(f"Saved Image: {path}")
        return filename
    except Exception as e:
        logger.error("Failed to save image: {e}")
        return None