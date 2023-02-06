import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.templating import Jinja2Templates
from starlette.websockets import WebSocket, WebSocketDisconnect

templates = Jinja2Templates(directory="templates")


app = Starlette()
websockets_list = []


@app.route("/")
async def homepage(request: Request):
    """Ask for the user's name"""
    template = "index.html"
    context = {"request": request}
    return templates.TemplateResponse(template, context)


@app.route("/session")
async def session(request: Request, name: str):
    """Main page for voting"""
    template = "session.html"
    context = {"request": request, "name": name}
    return templates.TemplateResponse(template, context)


@app.websocket_route("/ws/{name:str}")
async def websocket_endpoint(websocket: WebSocket, name: str):
    """Handles all websocket requests"""
    await websocket.accept()
    websockets_list.append(websocket)
    # websocket.send_text(render_votes_html)

    try:
        while True:
            data = await websocket.receive_text()
            for websocket in websockets_list:
                print(websocket.__dict__)

            # votes_dict = {

            # }
            # if data == "reset":

            # elif data == "show":
            #     show = True
            # else:
            #     votes_dict[name] = data

            # data_split = data.split("_")
            # data_type = data_split[0]
            # data_value = data_split[1]
            # if data_type == "vote":
            #     votes_dict[name] = data_value
            # elif data_type == "message":
            #     if data_value == "reset":

            # if message == "show":
            #     state_dict["issue"] = data["issue"]
            # elif data.get("vote"):
            #     state_dict["votes"][name] = data["vote"]
            # elif data.get("reset"):
            #     state_dict["votes"] = {}
            #     state_dict["show"] = False
            # elif data.get("show"):
            #     state_dict["show"] = True

            # print(data)
            # print(votes_dict)
            # for ws in websockets_list:
            #     await ws.send_text(state_dict)
    except WebSocketDisconnect:
        websockets_list.remove(websocket)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8888)
