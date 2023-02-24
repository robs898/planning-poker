import time

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")
active_websockets = {}
state_dict = {}
heartbeat_dict = {}
votes_template = templates.get_template("votes.html")


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/favicon.ico")
async def favicon():
    return


@app.get("/session")
async def session(request: Request, name: str):
    return templates.TemplateResponse(
        "session.html", {"request": request, "name": name}
    )


@app.websocket("/ws/{name}")
async def websocket_endpoint(websocket: WebSocket, name: str):
    await websocket.accept()
    global active_websockets
    active_websockets[name] = websocket
    global state_dict
    if name not in state_dict:
        state_dict[name] = "?"

    try:
        global show
        show = False
        await broadcast(render_html(state_dict, show))
        while True:
            data = await websocket.receive_text()
            if data == "reset":
                state_dict = {k: "?" for k in state_dict}
                show = False
            elif data == "show":
                show = True
            elif data == "hide":
                show = False
            elif data == "ping":
                global heartbeat_dict
                heartbeat_dict[name] = time.time()
            else:
                state_dict[name] = data

            await broadcast(render_html(state_dict, show))
    except WebSocketDisconnect:
        del active_websockets[name]


def render_html(state_dict, show):
    check_heartbeats()
    rainbow = False
    if state_dict and list(state_dict.values())[0] != "?":
        unique_votes = set(state_dict.values())
        rainbow = len(unique_votes) == 1 and show

    return votes_template.render(
        state_dict=state_dict, show=show, rainbow=rainbow
    )


async def broadcast(message: str):
    for _, websocket in active_websockets.items():
        await websocket.send_text(message)


def check_heartbeats():
    global heartbeat_dict
    failed_hearbeats_list = []
    for name, heartbeat in heartbeat_dict.items():
        heartbeat_age = time.time() - heartbeat
        if heartbeat_age > 2:
            failed_hearbeats_list.append(name)

    for name in failed_hearbeats_list:
        global state_dict
        del state_dict[name]
        del heartbeat_dict[name]
