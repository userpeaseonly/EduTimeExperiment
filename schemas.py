from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class FaceRect(BaseModel):
    height: float
    width: float
    x: float
    y: float

    model_config = ConfigDict(populate_by_name=True)


class AccessControllerEvent(BaseModel):
    device_name: Optional[str] = Field(None, alias="deviceName")
    major_event_type: int = Field(..., alias="majorEventType")
    sub_event_type: int = Field(..., alias="subEventType")
    net_user: Optional[str] = Field(None, alias="netUser")
    remote_host_addr: Optional[str] = Field(None, alias="remoteHostAddr")
    card_no: Optional[str] = Field(None, alias="cardNo")
    card_type: Optional[int] = Field(None, alias="cardType")
    white_list_no: Optional[int] = Field(None, alias="whiteListNo")
    report_channel: Optional[int] = Field(None, alias="reportChannel")
    card_reader_kind: Optional[int] = Field(None, alias="cardReaderKind")
    card_reader_no: Optional[int] = Field(None, alias="cardReaderNo")
    door_no: Optional[int] = Field(None, alias="doorNo")
    verify_no: Optional[int] = Field(None, alias="verifyNo")
    alarm_in_no: Optional[int] = Field(None, alias="alarmInNo")
    alarm_out_no: Optional[int] = Field(None, alias="alarmOutNo")
    case_sensor_no: Optional[int] = Field(None, alias="caseSensorNo")
    rs485_no: Optional[int] = Field(None, alias="RS485No")
    multi_card_group_no: Optional[int] = Field(None, alias="multiCardGroupNo")
    access_channel: Optional[int] = Field(None, alias="accessChannel")
    device_no: Optional[int] = Field(None, alias="deviceNo")
    distract_control_no: Optional[int] = Field(None, alias="distractControlNo")
    employee_no: Optional[str] = Field(None, alias="employeeNo")
    employee_no_str: Optional[str] = Field(None, alias="employeeNoString")
    local_controller_id: Optional[int] = Field(None, alias="localControllerID")
    internet_access: Optional[int] = Field(None, alias="InternetAccess")
    type_: Optional[int] = Field(None, alias="type")
    mac_addr: Optional[str] = Field(None, alias="MACAddr")
    swipe_card_type: Optional[int] = Field(None, alias="swipeCardType")
    serial_no: Optional[int] = Field(None, alias="serialNo")
    channel_controller_id: Optional[int] = Field(None, alias="channelControllerID")
    channel_controller_lamp_id: Optional[int] = Field(None, alias="channelControllerLampID")
    channel_controller_ir_adaptor_id: Optional[int] = Field(None, alias="channelControllerIRAdaptorID")
    channel_controller_ir_emitter_id: Optional[int] = Field(None, alias="channelControllerIREmitterID")
    user_type: Optional[str] = Field(None, alias="userType")
    current_verify_mode: Optional[str] = Field(None, alias="currentVerifyMode")
    current_event: Optional[bool] = Field(None, alias="currentEvent")
    front_serial_no: Optional[int] = Field(None, alias="frontSerialNo")
    attendance_status: Optional[str] = Field(None, alias="attendanceStatus")
    status_value: Optional[int] = Field(None, alias="statusValue")
    picture_url: Optional[str] = Field(None, alias="pictureURL")
    pictures_number: Optional[int] = Field(None, alias="picturesNumber")
    name: Optional[str] = Field(None, alias="name")
    label: Optional[str] = Field(None, alias="label")
    mask: Optional[str] = Field(None, alias="mask")
    pure_pwd_verify_enable: Optional[bool] = Field(None, alias="purePwdVerifyEnable")
    face_rect: Optional[FaceRect] = Field(None, alias="FaceRect")

    model_config = ConfigDict(populate_by_name=True)


class EventNotificationAlert(BaseModel):
    ip_address: Optional[str] = Field(None, alias="ipAddress")
    port_no: Optional[int] = Field(None, alias="portNo")
    protocol: Optional[str] = Field(None, alias="protocol")
    mac_address: Optional[str] = Field(None, alias="macAddress")
    channel_id: Optional[int] = Field(None, alias="channelID")
    date_time: datetime = Field(..., alias="dateTime")
    active_post_count: Optional[int] = Field(None, alias="activePostCount")
    event_type: str = Field(..., alias="eventType")
    event_state: Optional[str] = Field(None, alias="eventState")
    event_description: Optional[str] = Field(None, alias="eventDescription")
    device_id: Optional[str] = Field(None, alias="deviceID")
    access_controller_event: AccessControllerEvent = Field(..., alias="AccessControllerEvent")

    model_config = ConfigDict(populate_by_name=True)
# from pydantic import BaseModel, Field, ValidationError
# from typing import Optional, List, Dict, Any
# from datetime import datetime


# # This model represents the FaceRect data for FaceID events
# class FaceRect(BaseModel):
#     height: float
#     width: float
#     x: float
#     y: float

# # This model represents the detailed AccessControllerEvent section
# class AccessControllerEvent(BaseModel):
#     """
#     Represents the detailed AccessControllerEvent section within the Hikvision webhook payload.
#     Combines fields from both example structures.
#     """
#     deviceName: Optional[str] = Field(None, description="Name of the device related to the event")
#     majorEventType: int = Field(..., description="Major event type code")
#     subEventType: int = Field(..., description="Sub event type code")
#     netUser: Optional[str] = Field(None, description="Network user related to the event")
#     remoteHostAddr: Optional[str] = Field(None, description="Remote host IP address")
#     cardNo: Optional[str] = Field(None, description="Card number (e.g., for card swipe events)")
#     cardType: Optional[int] = Field(None, description="Type of card used")
#     whiteListNo: Optional[int] = Field(None, description="Whitelist number")
#     reportChannel: Optional[int] = Field(None, description="Channel for reporting")
#     cardReaderKind: Optional[int] = Field(None, description="Kind of card reader")
#     cardReaderNo: Optional[int] = Field(None, description="Card reader number")
#     doorNo: Optional[int] = Field(None, description="Door number involved in the event")
#     verifyNo: Optional[int] = Field(None, description="Verification number")
#     alarmInNo: Optional[int] = Field(None, description="Alarm input number")
#     alarmOutNo: Optional[int] = Field(None, description="Alarm output number")
#     caseSensorNo: Optional[int] = Field(None, description="Case sensor number")
#     RS485No: Optional[int] = Field(None, description="RS485 interface number")
#     multiCardGroupNo: Optional[int] = Field(None, description="Multi-card group number")
#     accessChannel: Optional[int] = Field(None, description="Access channel number")
#     deviceNo: Optional[int] = Field(None, description="Device number")
#     distractControlNo: Optional[int] = Field(None, description="Distract control number")
#     employeeNo: Optional[str] = Field(None, description="Employee number")
#     employeeNoString: Optional[str] = Field(None, description="Employee number as a string (found in example2)")
#     localControllerID: Optional[int] = Field(None, description="Local controller ID")
#     InternetAccess: Optional[int] = Field(None, description="Internet access status")
#     type: Optional[int] = Field(None, description="Generic type field")
#     MACAddr: Optional[str] = Field(None, description="MAC address of the device")
#     swipeCardType: Optional[int] = Field(None, description="Type of card swipe")
#     serialNo: Optional[int] = Field(None, description="Serial number")
#     channelControllerID: Optional[int] = Field(None, description="Channel controller ID")
#     channelControllerLampID: Optional[int] = Field(None, description="Channel controller lamp ID")
#     channelControllerIRAdaptorID: Optional[int] = Field(None, description="Channel controller IR emitter ID")
#     channelControllerIREmitterID: Optional[int] = Field(None, description="Channel controller IR emitter ID")
#     userType: Optional[str] = Field(None, description="Type of user involved in the event")
#     currentVerifyMode: Optional[str] = Field(None, description="Current verification mode")
#     currentEvent: Optional[bool] = Field(None, description="Indicates if it's the current active event")
#     frontSerialNo: Optional[int] = Field(None, description="Front serial number")
#     attendanceStatus: Optional[str] = Field(None, description="Attendance status")
#     statusValue: Optional[int] = Field(None, description="Status value")
#     pictureURL: Optional[str] = Field(None, description="URL to download the associated picture (e.g., face capture)")
#     picturesNumber: Optional[int] = Field(None, description="Number of pictures associated with the event")
#     name: Optional[str] = Field(None, description="Name of the person (found in example2)")
#     label: Optional[str] = Field(None, description="Event label (found in examples)")
#     mask: Optional[str] = Field(None, description="Mask detection status (e.g., 'no', 'unknown')")
#     purePwdVerifyEnable: Optional[bool] = Field(None, description="Pure password verification enabled status")
#     face_rect: Optional[FaceRect] = Field(None, alias="FaceRect", description="Bounding box for detected face (FaceID events)")

# # This model represents the top-level EventNotificationAlert
# class EventNotificationAlert(BaseModel):
#     """
#     Represents the main EventNotificationAlert structure of the Hikvision webhook payload.
#     This is the top-level container for general event information.
#     """
#     ipAddress: Optional[str] = Field(None, description="IP address of the device")
#     portNo: Optional[int] = Field(None, description="Port number of the device")
#     protocol: Optional[str] = Field(None, description="Protocol used by the device")
#     macAddress: Optional[str] = Field(None, description="MAC address of the device")
#     channelID: Optional[int] = Field(None, description="ID of the channel where the event occurred")
#     dateTime: datetime = Field(..., description="Timestamp of the event") # Pydantic will parse this string to datetime
#     activePostCount: Optional[int] = Field(None, description="Number of active posts")
#     eventType: str = Field(..., description="The primary type of the event (e.g., 'AccessControllerEvent')")
#     eventState: Optional[str] = Field(None, description="State of the event (e.g., 'active')")
#     eventDescription: Optional[str] = Field(None, description="Human-readable description of the event")
#     deviceID: Optional[str] = Field(None, description="ID of the device where the event occurred")
#     # Nested AccessControllerEvent model, aliased for Hikvision's PascalCase
#     access_controller_event: AccessControllerEvent = Field(
#         alias="AccessControllerEvent",
#         description="Detailed information about the access control event"
#     )


