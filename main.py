from fastapi import FastAPI, Request, Response, status
from starlette.datastructures import UploadFile, FormData
import json, textwrap

app = FastAPI()

def pretty(e: dict) -> str:
    ac  = e.get("AccessControllerEvent", {})
    return (
        f"[{e.get('dateTime')}] {e.get('deviceID')} {e.get('eventType')}"
        f"  major={ac.get('majorEventType')}  sub={ac.get('subEventType')}"
        f"  mode={ac.get('currentVerifyMode')}"
    )

@app.post("/hik/events")
async def hik_events(request: Request):
    ct = request.headers.get("content-type", "")
    raw_len = int(request.headers.get("content-length", 0))
    print(f"Received {raw_len} bytes • {ct}")

    # ── multipart ───────────────────────────────────────────────
    if ct.startswith("multipart/form-data"):
        form: FormData = await request.form()
        part = form["event_log"]

        if isinstance(part, UploadFile):
            event_json_bytes = await part.read()
        else:                         # Already plain str
            event_json_bytes = str(part).encode()

        event = json.loads(event_json_bytes)

    # ── plain JSON ──────────────────────────────────────────────
    elif ct.startswith("application/json"):
        event = await request.json()

    else:
        return Response(status_code=415)

    # ── log nicely ──────────────────────────────────────────────
    print("\nRaw JSON:\n", textwrap.indent(json.dumps(event, indent=2), "  "))
    print("Summary :", pretty(event))

    return Response(status_code=status.HTTP_204_NO_CONTENT)
