from typing import List

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


class Votes:
    state_dict = {}
    template = templates.get_template("votes.html")
    show = False

    def __init__(self):
        self.html = self.render_html()

    def render_html(self):
        return self.template.render(state_dict=self.state_dict, show=self.show)

    def set_vote(self, name, vote):
        self.state_dict[name] = vote


manager = ConnectionManager()
votes = Votes()


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/session")
async def session(request: Request, name: str):
    return templates.TemplateResponse(
        "session.html", {"request": request, "name": name}
    )


@app.websocket("/ws/{name}")
async def websocket_endpoint(websocket: WebSocket, name: str):
    await manager.connect(websocket)
    await websocket.send_text(votes.render_html())
    try:
        while True:
            data = await websocket.receive_text()
            if data == "reset":
                votes.state_dict = {}
                votes.show = False
            elif data == "show":
                votes.show = True
            elif data == "hide":
                votes.show = False
            else:
                votes.set_vote(name, data)

            await manager.broadcast(votes.render_html())
    except WebSocketDisconnect:
        manager.disconnect(websocket)
