from fastapi import FastAPI, Request, Response, status
from fastapi.responses import PlainTextResponse
from starlette.datastructures import UploadFile
from typing import Dict, Any
import json
import textwrap

app = FastAPI()

def pretty(event: Dict[str, Any]) -> str:
    """Return a human-readable one-liner from the JSON."""
    ts   = event.get("dateTime")
    dev  = event.get("deviceID")
    et   = event.get("eventType")
    ac   = event.get("AccessControllerEvent", {})
    major= ac.get("majorEventType")
    sub  = ac.get("subEventType")
    mode = ac.get("currentVerifyMode")
    return f"[{ts}] {dev} {et}  major={major}  sub={sub}  mode={mode}"

@app.post("/hik/events")
async def hik_events(request: Request):
    content_type = request.headers.get("content-type", "")
    body = await request.body()
    print(f"Received {len(body)} bytes, CT={content_type}")

    # ── 1. MULTIPART ─────────────────────────────────────────────
    if content_type.startswith("multipart/form-data"):
        # Let Starlette parse it
        form = await request.form()
        part: UploadFile = form["event_log"]
        event_json = await part.read()
        event = json.loads(event_json)
    # ── 2. PLAIN JSON ────────────────────────────────────────────
    elif content_type.startswith("application/json"):
        event = await request.json()
    else:
        return Response(status_code=415)

    # ── 3. Pretty output ─────────────────────────────────────────
    print("\nRaw JSON:\n", textwrap.indent(json.dumps(event, indent=2), "  "))
    print("Summary :", pretty(event))

    # TODO: store in DB / queue here …

    return Response(status_code=status.HTTP_204_NO_CONTENT)
