import logging
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.pretty import Pretty
from schemas.events import EventNotificationAlert, AccessControllerEvent

console = Console()

def log_pretty_event(event: EventNotificationAlert) -> None:
    """Pretty print and log an EventNotificationAlert."""
    
    # Prepare header
    header_text = Text(f"📡 Event Type: {event.event_type}", style="bold cyan")
    header_text.append(f" | 📅 Time: {event.date_time}", style="dim")

    # Create core metadata block
    core_data = {
        "Device ID": event.device_id,
        "Event State": event.event_state,
        "Description": event.event_description,
        "Post Count": event.active_post_count,
        "Date Time": event.date_time
    }

    # Prepare inner AccessControllerEvent data if available
    # ace = getattr(event, "access_controller_event", None)
    ace = event.access_controller_event if event.access_controller_event else None
    if ace:
        ace_data = {
            "Major Event": ace.major_event,
            "Minor Event": ace.minor_event,
            "Employee No": ace.person_id,
            "Employee Name": ace.person_name,
            "Verify Mode": ace.current_verify_mode,
            "Attendance Status": ace.attendance_status,
            "User Type": ace.user_type,
            "Card No": ace.card_no,
            "Swipe Type": ace.swipe_card_type,
            "Mask": ace.mask,
            "Pictures": ace.pictures_number,
        }

        # Merge into core data for display
        core_data.update({f"[AC] {k}": v for k, v in ace_data.items() if v is not None})

    # Use rich Panel to output
    console.print(Panel(Pretty(core_data, expand_all=True), title=header_text))

    # Additionally log to standard logger if needed
    logging.info(f"[Event] {event.event_type} from {event.device_id} at {event.date_time}")
