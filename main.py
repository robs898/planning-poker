from functools import lru_cache
from aiocache import Cache
from fastapi import FastAPI, WebSocketDisconnect
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")
template = templates.get_template("votes.html")
cache = Cache()


async def connect(websocket):
    await websocket.accept()
    active_connections = cache.get("active_connections", default=[])
    await active_connections.append(websocket)
    await cache.set("active_connections", active_connections)


async def disconnect(websocket):
    active_connections = cache.get("active_connections", default=[])
    await active_connections.remove(websocket)
    await cache.set("active_connections", active_connections)


async def broadcast(message):
    active_connections = cache.get("active_connections", default=[])
    for connection in active_connections:
        await connection.send_text(message)


@lru_cache()
async def render_html(show):
    unique_votes = set(state_dict.values())
    rainbow = len(unique_votes) == 1 & show
    return template.render(state_dict=state_dict, show=show, rainbow=rainbow)


async def reset_votes():
    active_connections = cache.get("active_connections", default=[])
    state_dict = cache.get("state_dict", default={})
    for websocket in active_connections:
        state_dict[websocket.path_params["name"]] = "?"

    await cache.set("state_dict", state_dict)


async def set_vote(name, vote):
    state_dict[name] = vote


async def add_voter(name):
    if name not in state_dict:
        set_vote(name, "?")


@app.get("/")
async def index(request):
    """Get the user's name"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/session")
async def session(request, name):
    """Handle all voting"""
    return templates.TemplateResponse(
        "session.html", {"request": request, "name": name}
    )


@app.websocket("/ws/{name}")
async def websocket_endpoint(websocket, name):
    """Handle websockets for accepting/sending voting state"""
    await connect(websocket)
    await add_voter(name)
    try:
        await broadcast(render_html())
        while True:
            data = await websocket.receive_text()
            if data == "reset":
                reset_votes()
                show = False
            elif data == "show":
                show = True
            elif data == "hide":
                show = False
            else:
                set_vote(name, data)

            await broadcast(render_html(show))
    except WebSocketDisconnect:
        disconnect(websocket)
