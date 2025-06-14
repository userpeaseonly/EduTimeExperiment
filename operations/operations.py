import os
import logging
from datetime import datetime
from fastapi import UploadFile

from main import logger
from core import config


def save_image(file: UploadFile | None, label: str) -> str | None:
    """Save uploaded image to disk."""
    if not file:
        return None
    filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{label}.jpg"
    path = os.path.join(config.SAVE_DIR, filename)
    with open(path, "wb") as f:
        f.write(file.file.read())
    logger.info(f"Saved image: {path}")
    return path
