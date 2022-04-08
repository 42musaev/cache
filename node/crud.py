import uuid
from asyncpg import UniqueViolationError
from sqlalchemy import insert, select, delete
from sqlalchemy.dialects.postgresql import insert as insert_pgsql

from db.conf import database


class NodeCrud:

    def __init__(self, model):
        self.model = model

    async def create_node(self, data):

        insert_data = {
            'value': data['value'],
            'uuid': str(uuid.uuid4()),
            'parent_uuid': data['parent_uuid'],
            'disable': False
        }
        query = insert(self.model).values(**insert_data)
        try:
            await database.fetch_val(query)
            return insert_data
        except UniqueViolationError:
            return {
                "value": insert_data['value'],
                "detail": "already exists"
            }

    async def create_many_row(self, data):
        query = insert_pgsql(self.model).values(data)
        query = query.on_conflict_do_update(
            index_elements=[self.model.uuid],
            set_={
                'uuid': self.model.uuid,
                'value': query.excluded.value,
                'disable': query.excluded.disable
            }
        )
        await database.execute(query)

    async def delete_all_node(self):
        query = delete(self.model)
        obj = await database.execute(query)
        return obj

    async def delete_node_by_uuid(self, uuid):
        query = delete(self.model).where(self.model.uuid == str(uuid))
        obj = await database.execute(query)
        return obj

    async def get_by_uuid(self, uuid: str):
        query = select(
            self.model.value,
            self.model.uuid,
            self.model.parent_uuid,
            self.model.disable
        ).where(self.model.uuid == uuid)
        obj = await database.fetch_one(query)
        if obj:
            return obj
        return 404

    async def get_all_node(self):
        query = \
            select(
                self.model.value,
                self.model.uuid,
                self.model.parent_uuid,
                self.model.disable
            )
        obj = await database.fetch_all(query)
        return obj

    async def create_init_data(self, init_data):
        query = insert(self.model).values(init_data)
        obj = await database.execute(query)
        return obj
