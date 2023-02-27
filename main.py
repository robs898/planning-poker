import time
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")
votes_template = templates.get_template("votes.html")


class AppState:
    active_websockets = {}
    state_dict = {}
    heartbeat_dict = {}
    show = False

    def check_heartbeats(self):
        failed_hearbeats_list = []
        for name, heartbeat in self.heartbeat_dict.items():
            heartbeat_age = time.time() - heartbeat
            if heartbeat_age > 2:
                failed_hearbeats_list.append(name)

        for name in failed_hearbeats_list:
            del self.state_dict[name]
            del self.heartbeat_dict[name]

    def render_votes_html(self):
        rainbow = False
        votes_list = list(self.state_dict.values())
        if len(votes_list) > 1 and votes_list[0] != "?":
            unique_votes = set(votes_list)
            rainbow = len(unique_votes) == 1 and self.show

        return votes_template.render(
            state_dict=self.state_dict, show=self.show, rainbow=rainbow
        )

    async def broadcast(self, message):
        for _, websocket in self.active_websockets.items():
            await websocket.send_text(message)

    async def broadcast_votes_html(self):
        votes_html = self.render_votes_html()
        await self.broadcast(votes_html)


app_state = AppState()


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
    app_state.active_websockets[name] = websocket
    app_state.heartbeat_dict[name] = time.time()
    app_state.state_dict[name] = "?"
    await app_state.broadcast_votes_html()
    try:
        while True:
            data = await websocket.receive_text()
            if data == "reset":
                app_state.state_dict = {k: "?" for k in app_state.state_dict}
                app_state.show = False
            elif data == "show":
                app_state.show = True
            elif data == "hide":
                app_state.show = False
            elif data == "ping":
                app_state.heartbeat_dict[name] = time.time()
                app_state.check_heartbeats()
            else:
                app_state.state_dict[name] = data

            await app_state.broadcast_votes_html()
    except WebSocketDisconnect:
        del app_state.active_websockets[name]
