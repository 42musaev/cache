from typing import List

from pydantic import BaseModel


class NodeSchema(BaseModel):
    value: str
    uuid: str
    parent_uuid: str
    disable: bool


class NodeCreateSchema(BaseModel):
    value: str
    parent_uuid: str = ""


class NodePatch(BaseModel):
    value: str


class NodeDelete(BaseModel):
    uuids: List[str]
