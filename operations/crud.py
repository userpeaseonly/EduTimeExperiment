import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.event import Event, Heartbeat
from schemas import events
from typing import Optional

async def create_event(event: Event, db: AsyncSession) -> Event:
    """
    Create a new event in the database.
    
    :param event: The event to create.
    :param db: The database session.
    :return: The created event.
    """
    db.add(event)
    await db.commit()
    await db.refresh(event)
    return event


async def create_heartbeat(
    heartbeat: Heartbeat, db: AsyncSession
) -> Heartbeat:
    """
    Create a new heartbeat event in the database.

    :param heartbeat: The heartbeat event to create.
    :param db: The database session.
    :return: The created heartbeat event.
    """
    db.add(heartbeat)
    await db.commit()
    await db.refresh(heartbeat)
    return heartbeat
