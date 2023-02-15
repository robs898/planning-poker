from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")


class ConnectionManager:
    """Handle websocket connections"""

    def __init__(self):
        self.active_connections = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


class Votes:
    """Handle the state of votes"""

    state_dict = {}
    template = templates.get_template("votes.html")
    show = False

    def __init__(self):
        self.html = self.render_html()

    def render_html(self):
        rainbow = False
        if self.state_dict:
            if list(self.state_dict.values())[0] != "?":
                unique_votes = set(self.state_dict.values())
                rainbow = len(unique_votes) == 1 & self.show

        return self.template.render(
            state_dict=self.state_dict, show=self.show, rainbow=rainbow
        )

    def reset_votes(self, websockets):
        """Set all votes to ?"""
        self.state_dict = {}
        for websocket in websockets:
            self.state_dict[websocket.path_params["name"]] = "?"

    def set_vote(self, name, vote):
        self.state_dict[name] = vote

    def add_voter(self, name):
        if name not in self.state_dict:
            self.set_vote(name, "?")


manager = ConnectionManager()
votes = Votes()


@app.get("/")
async def index(request: Request):
    """Get the user's name"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/favicon.ico")
async def favicon(request: Request):
    """To stop the failed GETs in console"""
    return


@app.get("/session")
async def session(request: Request, name: str):
    """Handle all voting"""
    return templates.TemplateResponse(
        "session.html", {"request": request, "name": name}
    )


@app.websocket("/ws/{name}")
async def websocket_endpoint(websocket: WebSocket, name: str):
    """Handle websockets for accepting/sending voting state"""
    await manager.connect(websocket)
    votes.add_voter(name)
    votes.show = False
    try:
        await manager.broadcast(votes.render_html())
        while True:
            data = await websocket.receive_text()
            if data == "reset":
                votes.reset_votes(manager.active_connections)
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
