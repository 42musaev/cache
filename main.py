from fastapi import FastAPI

from node.api import node
from db.conf import database
from node.views import node_view

app = FastAPI()

@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

app.include_router(node, prefix='/api')
app.include_router(node_view)