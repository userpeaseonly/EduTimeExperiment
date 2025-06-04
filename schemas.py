from pydantic import BaseModel, Field, ValidationError
from typing import Optional, List, Dict, Any
from datetime import datetime

# --- 1. AccessControllerEvent Model ---
# This model represents the detailed access control specific data.
class AccessControllerEvent(BaseModel):
    """
    Represents the detailed AccessControllerEvent section within the Hikvision webhook payload.
    This includes specifics like card numbers, employee IDs, and the crucial picture URL.
    """
    deviceName: Optional[str] = Field(None, description="Name of the device related to the event")
    majorEventType: int = Field(..., description="Major event type code")
    subEventType: int = Field(..., description="Sub event type code")
    netUser: Optional[str] = Field(None, description="Network user related to the event")
    remoteHostAddr: Optional[str] = Field(None, description="Remote host IP address")
    cardNo: Optional[str] = Field(None, description="Card number (e.g., for card swipe events)")
    cardType: Optional[int] = Field(None, description="Type of card used")
    whiteListNo: Optional[int] = Field(None, description="Whitelist number")
    reportChannel: Optional[int] = Field(None, description="Channel for reporting")
    cardReaderKind: Optional[int] = Field(None, description="Kind of card reader")
    cardReaderNo: Optional[int] = Field(None, description="Card reader number")
    doorNo: Optional[int] = Field(None, description="Door number involved in the event")
    verifyNo: Optional[int] = Field(None, description="Verification number")
    alarmInNo: Optional[int] = Field(None, description="Alarm input number")
    alarmOutNo: Optional[int] = Field(None, description="Alarm output number")
    caseSensorNo: Optional[int] = Field(None, description="Case sensor number")
    RS485No: Optional[int] = Field(None, description="RS485 interface number")
    multiCardGroupNo: Optional[int] = Field(None, description="Multi-card group number")
    accessChannel: Optional[int] = Field(None, description="Access channel number")
    deviceNo: Optional[int] = Field(None, description="Device number")
    distractControlNo: Optional[int] = Field(None, description="Distract control number")
    employeeNo: Optional[str] = Field(None, description="Employee number (important for FaceID events)")
    localControllerID: Optional[int] = Field(None, description="Local controller ID")
    InternetAccess: Optional[int] = Field(None, description="Internet access status")
    type: Optional[int] = Field(None, description="Generic type field")
    MACAddr: Optional[str] = Field(None, description="MAC address of the device")
    swipeCardType: Optional[int] = Field(None, description="Type of card swipe")
    serialNo: Optional[int] = Field(None, description="Serial number")
    channelControllerID: Optional[int] = Field(None, description="Channel controller ID")
    channelControllerLampID: Optional[int] = Field(None, description="Channel controller lamp ID")
    channelControllerIRAdaptorID: Optional[int] = Field(None, description="Channel controller IR adaptor ID")
    channelControllerIREmitterID: Optional[int] = Field(None, description="Channel controller IR emitter ID")
    userType: Optional[str] = Field(None, description="Type of user involved in the event")
    currentVerifyMode: Optional[str] = Field(None, description="Current verification mode")
    currentEvent: Optional[bool] = Field(None, description="Indicates if it's the current active event")
    frontSerialNo: Optional[int] = Field(None, description="Front serial number")
    attendanceStatus: Optional[str] = Field(None, description="Attendance status")
    statusValue: Optional[int] = Field(None, description="Status value")
    pictureURL: Optional[str] = Field(None, description="URL to download the associated picture (e.g., face capture)")
    picturesNumber: Optional[int] = Field(None, description="Number of pictures associated with the event")

# --- 2. EventNotificationAlert Model ---
# This model represents the main notification alert wrapper.
class EventNotificationAlert(BaseModel):
    """
    Represents the main EventNotificationAlert structure of the Hikvision webhook payload.
    This is the top-level container for general event information.
    """
    channelID: Optional[str] = Field(None, description="ID of the channel where the event occurred")
    dateTime: datetime = Field(..., description="Timestamp of the event") # Pydantic will parse this string to datetime
    activePostCount: Optional[int] = Field(None, description="Number of active posts")
    eventType: str = Field(..., description="The primary type of the event (e.g., 'AccessControllerEvent')")
    eventState: Optional[str] = Field(None, description="State of the event (e.g., 'active')")
    eventDescription: Optional[str] = Field(None, description="Human-readable description of the event")
    devIndex: Optional[str] = Field(None, description="Device index")
    channelName: Optional[str] = Field(None, description="Name of the channel")
    # Nested AccessControllerEvent model, aliased for Hikvision's PascalCase
    access_controller_event: AccessControllerEvent = Field(
        alias="AccessControllerEvent",
        description="Detailed information about the access control event"
    )

# --- 3. HikvisionWebhookPayload Model ---
# This is the outermost model representing the entire incoming JSON.
class HikvisionWebhookPayload(BaseModel):
    """
    The complete Pydantic model for the entire Hikvision webhook payload.
    This is the top-level wrapper containing the EventNotificationAlert.
    """
    event_notification_alert: EventNotificationAlert = Field(
        alias="EventNotificationAlert",
        description="Main event notification alert payload"
    )

    # Optional: Configure Pydantic behavior for this model
    model_config = {
        "extra": "ignore", # Ignore any extra fields not defined in the schema
        "populate_by_name": True # Allow creating instances using Python attribute names OR aliases
    }
