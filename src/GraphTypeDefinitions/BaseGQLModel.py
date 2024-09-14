import strawberry
import uuid
import datetime
import typing
import asyncio

# IDType = strawberry.ID
IDType = uuid.UUID

class BaseGQLModel(strawberry.relay.Node):
    @classmethod
    def getLoader(cls, info):
        pass

    @classmethod
    async def resolve_reference(cls, info: strawberry.types.Info, id: IDType):
        if id is not None:
            loader = cls.getLoader(info)
            if isinstance(id, str): id = uuid.UUID(id)
            result = await loader.load(id)
            if result is not None:
                result.__strawberry_definition__ = cls.__strawberry_definition__  # little hack :)
            return result
        return None

    @classmethod
    async def resolve_nodes(
        cls,
        *,
        info: strawberry.Info,
        node_ids: typing.Iterable[str],
        required: bool = False,
    ):
        awaitables = [cls.resolve_reference(info=info, id=node_id) for node_id in node_ids]
        results = await asyncio.gather(*awaitables, return_exceptions=False)
        return results
        
    @classmethod
    async def resolve_node(
        cls,
        node_id: str,
        *,
        info: strawberry.Info,
        required: bool,
    ):
        result = await cls.resolve_reference(info=info, id=node_id)
        return result