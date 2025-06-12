from schemas.events import EventNotificationAlert

def pretty(e: EventNotificationAlert) -> str:
    """
    Extracts and formats key information from the EventNotificationAlert model for logging.
    """
    ace = e.access_controller_event
    summary_parts = [
        f"[{e.date_time.isoformat()}]",
        f"DevID={e.device_id or 'N/A'}",
        f"Type={e.event_type}",
        f"Major={ace.major_event_type}",
        f"Sub={ace.sub_event_type}",
        f"Mode={ace.current_verify_mode or 'N/A'}"
    ]
    if ace.employee_no:
        summary_parts.append(f"EmpNo={ace.employee_no}")
    if ace.name:
        summary_parts.append(f"Name='{ace.name}'")
    if ace.card_no:
        summary_parts.append(f"CardNo={ace.card_no}")
    if ace.picture_url:
        summary_parts.append(f"PicURL='{ace.picture_url}'")

    return " ".join(summary_parts)
