import json
import uuid
from uuid import UUID
from typing import List

from fastapi import APIRouter
from starlette.responses import JSONResponse

from cache.conf import redis_cache
from db.conf import Base, engine
from db.utils import get_dump_data
from node.crud import NodeCrud
from node.models import Node
from node.schema import NodeCreateSchema, NodeSchema, NodePatch

node = APIRouter(tags=["NodeApi"])


@node.on_event('startup')
async def starup_event():
    await redis_cache.init_cache()


@node.on_event('shutdown')
async def shutdown_event():
    redis_cache.close()
    await redis_cache.close()


@node.get('/db/node', response_model=List[NodeSchema], status_code=200)
async def node_db_get():
    node_crud = NodeCrud(Node)
    objs = await node_crud.get_all_node()
    return objs


@node.post('/db/node', response_model=NodeSchema, status_code=201)
async def node_db_create(node: NodeCreateSchema):
    node_crud = NodeCrud(Node)
    data = node.dict()
    obj = await node_crud.create_node(data=data)
    return JSONResponse(
        content=obj,
        status_code=201
    )


@node.post('/db/node/{uuid}/copy', status_code=201)
async def node_add_cache(uuid: UUID):
    node_crud = NodeCrud(Node)
    obj = await node_crud.get_by_uuid(str(uuid))
    if obj == 404:
        return JSONResponse(
            content={"detail": "object not found"},
            status_code=404
        )
    node_obj = dict(obj)
    await redis_cache.set(node_obj['uuid'], json.dumps(node_obj))
    return JSONResponse(
        content={"detail": "object added to cache"},
        status_code=201
    )


@node.post('/db/reset', status_code=200)
async def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    node_crud = NodeCrud(Node)
    data = get_dump_data('db/json_dumps.json')
    await node_crud.create_init_data(data)
    return {"detail": "database reset"}


@node.get('/cache/node', status_code=200)
async def get_cache():
    return await redis_cache.get_all_dicts()


@node.post('/cache/node')
async def node_create_cache(node: NodeCreateSchema):
    data = node.dict()
    node_data = {
        "value": data['value'],
        "uuid": str(uuid.uuid4()),
        "parent_uuid": data['parent_uuid'],
        "disable": False
    }
    await redis_cache.set(node_data['uuid'], json.dumps(node_data))
    return node_data


@node.patch('/cache/node/{uuid}')
async def node_patch_cache(uuid: UUID, node: NodePatch):
    json_dict = await redis_cache.get(str(uuid))
    node_object = await redis_cache.json_to_dict(json_dict)
    if not node_object:
        return JSONResponse(
            content={"detail": "object not found"},
            status_code=404
        )
    node_object['value'] = node.value
    await redis_cache.set(str(uuid), json.dumps(node_object))
    return node_object


@node.delete('/cache/node/{uuid}')
async def node_delete_cache(uuid: UUID):
    json_object = await redis_cache.get(str(uuid))
    node_dict = await redis_cache.json_to_dict(json_object)
    node_dict['disable'] = True
    await redis_cache.set(node_dict['uuid'], json.dumps(node_dict))
    return JSONResponse(content=node_dict, status_code=200)


@node.post('/cache/sync-db', status_code=200)
async def cache_sync_db():
    list_dicts = await redis_cache.get_all_dicts()
    node_crud = NodeCrud(Node)
    await node_crud.create_many_row(list_dicts)
    return JSONResponse(
        content={"detail": "database synced"},
        status_code=200
    )
