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
from node.schema import (
    NodeCreateSchema,
    NodeSchema,
    NodePatch,
    NodeDelete
)

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
    node_dicts = await node_crud.get_all_node()
    return node_dicts


@node.post('/db/node/{uuid}/copy', status_code=201)
async def node_add_cache(uuid: UUID):
    node_crud = NodeCrud(Node)
    node_object = await node_crud.get_by_uuid(str(uuid))
    if node_object == 404:
        return JSONResponse(
            content={"detail": "object not found"},
            status_code=404
        )
    node_dict = dict(node_object)
    disable = node_dict.pop('disable')

    await redis_cache.hset(
        key=node_dict['uuid'],
        mapping={
            "value": json.dumps(node_dict),
            "disable": str(disable),
        }
    )
    return JSONResponse({"detail": "object copy to cache"}, status_code=201)


#
#
@node.post('/db/reset', status_code=200)
async def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    node_crud = NodeCrud(Node)
    data = get_dump_data('db/json_dumps.json')
    await node_crud.create_init_data(data)
    return JSONResponse({"detail": "database reset"}, status_code=200)


@node.get('/cache/node', status_code=200)
async def get_cache():
    node_dicts = await redis_cache.get_all_node()
    return JSONResponse(node_dicts, status_code=200)


@node.post('/cache/node', status_code=201)
async def node_create_cache(node: NodeCreateSchema):
    data = node.dict()
    node_data = {
        "value": data['value'],
        "uuid": str(uuid.uuid4()),
        "parent_uuid": data['parent_uuid'],
    }
    await redis_cache.hset(
        key=node_data['uuid'],
        mapping={
            "value": json.dumps(node_data),
            "disable": str(False),
        }
    )
    return JSONResponse(node_data, status_code=201)


@node.patch('/cache/node/{uuid}', status_code=200)
async def node_patch_cache(uuid: UUID, node: NodePatch):
    node_dict = await redis_cache.hget_dict(str(uuid), "value")
    node_dict['value'] = node.value

    await redis_cache.hset(
        key=str(uuid),
        mapping={
            "value": json.dumps(node_dict),
        }
    )
    return JSONResponse(node_dict, status_code=200)


@node.delete('/cache/node/{uuid}', status_code=200)
async def node_delete_cache(uuids: NodeDelete):
    for uuid in uuids.uuids:
        await redis_cache.hset(
            key=str(uuid),
            mapping={
                "disable": str(True),
            }

        )
    return JSONResponse(
        {"detail": "objects deleted"},
        status_code=200
    )


@node.post('/cache/sync-db', status_code=200)
async def cache_sync_db():
    list_dicts = await redis_cache.get_all_node()
    node_crud = NodeCrud(Node)
    await node_crud.create_many_row(list_dicts)
    return JSONResponse(
        content={"detail": "database synced"},
        status_code=200
    )
