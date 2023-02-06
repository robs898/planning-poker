from functools import lru_cache

import uvicorn
from starlette.applications import Starlette
from starlette.templating import Jinja2Templates
from starlette.websockets import WebSocketDisconnect

templates = Jinja2Templates(directory="templates")
app = Starlette()
websockets_list = []
votes_dict = {}
votes_show = False
votes_template = templates.get_template("votes.html")


@lru_cache
async def reset_votes(self):
    self.votes_dict = {
        x.scope["path_params"]["name"]: "" for x in self.websockets_list
    }


@lru_cache
async def render_votes_html(votes_dict, votes_show):
    template = templates.get_template("votes.html")
    return template.render(votes_dict=votes_dict, votes_show=votes_show)


@lru_cache
async def broadcast_votes_html(votes_html):
    for ws in websockets_list:
        await ws.send_text(votes_html)


@app.route("/")
async def homepage(request):
    """Ask for the user's name"""
    template = "index.html"
    context = {"request": request}
    return templates.TemplateResponse(template, context)


@app.route("/session")
async def session(request):
    """Main page for voting"""
    template = "session.html"
    context = {"request": request, "name": request.query_params["name"]}
    return templates.TemplateResponse(template, context)


@app.websocket_route("/ws")
async def websocket_endpoint(websocket):
    """Handles all websocket requests"""
    await websocket.accept()
    websockets_list.append(websocket)
    name = websocket.query_params["name"]
    votes_dict[name] = ""

    try:
        while True:
            data = await websocket.receive_text()
            if data == "reset":
                reset_votes()
            elif data == "show":
                votes_show = True
            elif data == "hide":
                votes_show = False
            else:
                votes_dict[name] = data

            await broadcast_votes_html(
                render_votes_html(votes_dict, votes_show)
            )
    except WebSocketDisconnect:
        websockets_list.remove(websocket)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8888)
