from fastapi import Request, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

node_view = APIRouter(tags=["NodeView"])

templates = Jinja2Templates(directory="templates")


@node_view.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
