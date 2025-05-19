# pip install fastapi uvicorn python-multipart python-hikvision-event
from fastapi import FastAPI, Request, Response, status
import xml.etree.ElementTree as ET

app = FastAPI()

@app.post("/hik/events", status_code=status.HTTP_204_NO_CONTENT)
async def hik_events(request: Request):
    # the device sends XML by default
    raw_xml = await request.body()
    print(f"Received {len(raw_xml)} bytes")
    print(raw_xml.decode("utf-8"))

    try:
        # pull a couple fields (employeeNo & attendanceStatus are enough for PoC)
        root = ET.fromstring(raw_xml) if raw_xml else None
        if root is None:
            return Response(status_code=400)
        emp_no  = root.findtext(".//employeeNo")
        status  = root.findtext(".//attendanceStatus")
        dt      = root.findtext("dateTime")
        
    except ET.ParseError as e:
        print(f"XML Parse Error: {e}")
        return Response(status_code=400)


    print(f"{dt}  {emp_no}  {status}")   # <-- replace with DB insert / queue

    # MUST reply quickly (<=2 s) or device retries
    return Response(status_code=204)
