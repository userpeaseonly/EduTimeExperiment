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