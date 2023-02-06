from functools import lru_cache

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")


# class ConnectionManager:
#     def __init__(self):
#         self.active_connections: List[WebSocket] = []

#     async def connect(self, websocket: WebSocket):
#         await websocket.accept()
#         self.active_connections.append(websocket)

#     def disconnect(self, websocket: WebSocket):
#         self.active_connections.remove(websocket)

#     async def broadcast(self, message: str):
#         for connection in self.active_connections:
#             await connection.send_json(message)


# class Votes:
#     state_dict = {}
#     template = templates.get_template("votes.html")
#     show = False

#     def __init__(self):
#         self.html = self.render_html()

#     def render_html(self):
#         return self.template.render(state_dict=self.state_dict, show=self.show)

#     def set_vote(self, name, vote):
#         self.state_dict[name] = vote


# manager = ConnectionManager()
# votes = Votes()


websockets_list = []
votes_dict = {}


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
    await websocket.accept()
    websockets_list.append(websocket)
    websocket.send_text(render_votes_html)

    try:
        while True:
            data = await websocket.receive_text()
            data_split = data.split("_")
            data_type = data_split[0]
            data_value = data_split[1]
            if data_type == "vote":
                votes_dict[name] = data_value
            elif data_type == "message":
                if data_value == "reset":
                    
            if message == "show":
                state_dict["issue"] = data["issue"]
            elif data.get("vote"):
                state_dict["votes"][name] = data["vote"]
            elif data.get("reset"):
                state_dict["votes"] = {}
                state_dict["show"] = False
            elif data.get("show"):
                state_dict["show"] = True

            print(data)
            print(state_dict)
            for ws in websockets_list:
                await ws.send_text(state_dict)
    except WebSocketDisconnect:
        websockets_list.remove(websocket)


@lru_cache()
async def render_votes_html(votes_dict, show):
    template = templates.get_template("votes.html")
    await template.render(votes_dict=votes_dict, show=show)
