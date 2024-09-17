import strawberry
import uuid
import datetime
import typing
import asyncio

from abc import abstractmethod
import strawberry.types

# IDType = strawberry.ID
IDType = uuid.UUID

@strawberry.interface(description="")
class Node:
    @strawberry.field(description="")
    async def id() -> IDType:
        return None

@strawberry.type(description="")
class BaseGQLModel(Node):
    @abstractmethod
    # @classmethod
    def getLoader(cls, info):
        pass

    @classmethod
    async def resolve_reference(cls, info: strawberry.types.Info, id: IDType):
        if id is not None:
            
            loader = cls.getLoader(info)
            if isinstance(id, str): id = uuid.UUID(id)
            print(f"loading {cls}(id={id})")
            result = await loader.load(id)
            return None if result is None else cls(result)
            # if result is not None:
            #     result.__strawberry_definition__ = cls.__strawberry_definition__  # little hack :)
            # return 
        return None

    def __init__(self, data):
        # print(f"{type(self).__name__}.__init__({data.id})")
        self._data = data
    
    def __repr__(self):
        return f"{type(self).__name__}({self._data.id})"
    
    from ._GraphResolvers import (
        resolve_id as id,
        resolve_createdby as createdby,
        resolve_created as created,
        resolve_lastchange as lastchange,
        resolve_changedby as changedby
    )


    # @classmethod
    # async def resolve_nodes(
    #     cls,
    #     *,
    #     info: strawberry.Info,
    #     node_ids: typing.Iterable[str],
    #     required: bool = False,
    # ):
    #     awaitables = [cls.resolve_reference(info=info, id=node_id) for node_id in node_ids]
    #     results = await asyncio.gather(*awaitables, return_exceptions=False)
    #     return results
        
    # @classmethod
    # async def resolve_node(
    #     cls,
    #     node_id: str,
    #     *,
    #     info: strawberry.Info,
    #     required: bool,
    # ):
    #     result = await cls.resolve_reference(info=info, id=node_id)
    #     return result

#
# see https://relay.dev/graphql/connections.htm
#
@strawberry.type(description="")
class PageInfo():
    def __init__(self, after: int=0, first: int=0, orderby: str="id", where: dict=None, extendedfilter: dict=None, gqltype=None, load_data=None):       
        assert load_data is not None, f"missing load_data"
        self.after = after
        self.before = None
        self.first = first
        self.last = None
        self.orderby = orderby
        self.where = where
        self.type = gqltype
        self.extendedfilter = extendedfilter
        self.load_data = load_data
    
    @strawberry.field(description="")
    def after(self) -> typing.Optional[str]:
        return self.after
    
    @strawberry.field(description="")
    def before(self) -> typing.Optional[str]:
        return self.before
    
    @strawberry.field(description="")
    def first(self) -> typing.Optional[int]:
        return self.first
    
    @strawberry.field(description="")
    def last(self) -> typing.Optional[int]:
        return self.last
    
    @strawberry.field(description="")
    async def has_next_page(self, info: strawberry.types.Info) -> bool:
        data = await self.load_data(info=info)
        # print([item.email for item in data], self.first)
        return len(data) > self.first
    
from functools import cached_property, cache

ConnectionType = typing.TypeVar("GQLType", bound="BaseGQLModel")

@strawberry.type(description="")
class Connection_Edge(typing.Generic[ConnectionType]):
    def __init__(self, dbrow: ConnectionType):
        self.data = dbrow
        pass

    @strawberry.field()
    async def cursor(self, info: strawberry.Info) -> str:
        value = self._cursor
        if callable(value):
            value = value()
        return f"{value}"

    @strawberry.field()
    async def node(self, info: strawberry.Info) -> ConnectionType:
        return self

def addcursor(index, item):
    item._cursor = index
    return item

@strawberry.type(description="")
class Connection(typing.Generic[ConnectionType]):
    @cached_property
    def _ConnectionType(self):
        cls = type(self)
        ob0 = cls.__orig_bases__[0]
        bt = ob0.__args__[0]
        # print(f"_ConnectionType {cls}, {ob0}, {bt}")
        return bt

    async def load_data(self, info: strawberry.types.Info):
        if self.result is None:
            connectionType = self._ConnectionType
            loader = connectionType.getLoader(info=info)
            _page_info = self._page_info
            skip = _page_info.after
            limit = _page_info.first
            where = _page_info.where
            orderby = _page_info.orderby
            extendedfilter = _page_info.extendedfilter
            # print(f"used  {extendedfilter}")       
            results = await loader.page(skip=skip, limit=limit+1, orderby=orderby, where=where, extendedfilter=extendedfilter)
            # awaitables = (connectionType.resolve_reference(info=info, id=result.id) for result in results)
            # awaited = await asyncio.gather(*awaitables)
            self.result = [addcursor(index+skip+1, connectionType(result)) for index, result in enumerate(results)]
            # print(f"loaded {self.result}")       
        return self.result 

    def __init__(self, skip: int=0, limit: int=0, orderby=None, where: dict=None, extendedfilter: dict=None):
        self.result = None
        self._page_info = PageInfo(
            after=(int(skip) if isinstance(skip, str) else skip),
            first=limit,
            where=(None if where is None else strawberry.asdict(where)),
            orderby=orderby,
            extendedfilter=extendedfilter,
            gqltype=self._ConnectionType,
            load_data=self.load_data
        )
        pass

    @strawberry.field(description="")
    def page_info(self) -> PageInfo:
        return self._page_info
    
    @strawberry.field(description="")
    async def edges(self, info: strawberry.Info) -> typing.List[Connection_Edge[ConnectionType]]:
        items = await self.load_data(info=info)
        # gqltype = self._ConnectionType
        # results = [gqltype(item) for item in items]
        if len(items) > self._page_info.first:
            return items[:-1]
        else:
            return items


ListType = typing.TypeVar("ListType", bound="BaseGQLModel")
class List(typing.Generic[ListType]):
    @cached_property
    def _ListType(self):
        cls = type(self)
        ob0 = cls.__orig_bases__[0]
        bt = ob0.__args__[0]
        # print(f"_ConnectionType {cls}, {ob0}, {bt}")
        return bt
    
    async def __call__(self, info: strawberry.Info, skip: int=0, limit: int=10, orderby=None, where: dict=None, extendedfilter: dict=None) -> typing.List[ListType]:
        listType = self._ListType
        loader = listType.getLoader(info=info)
        where = None if where is None else strawberry.asdict(where)
        results = await loader.page(skip=skip, limit=limit, orderby=orderby, where=where, extendedfilter=extendedfilter)
        # awaitables = (connectionType.resolve_reference(info=info, id=result.id) for result in results)
        # awaited = await asyncio.gather(*awaitables)
        return (listType(result) for result in results)
        

# class Page(typing.Generic[ListType]):
#     @cached_property
#     def _ListType(self):
#         cls = type(self)
#         ob0 = cls.__orig_bases__[0]
#         bt = ob0.__args__[0]
#         # print(f"_ConnectionType {cls}, {ob0}, {bt}")
#         return bt
    
#     async def __call__(self, info: strawberry.Info, skip: int=0, limit: int=10, orderby=None, where: dict=None) -> typing.List[ListType]:
#         listType = self._ListType
#         loader = listType.getLoader(info=info)
#         where = None if where is None else strawberry.asdict(where)
#         results = await loader.page(skip=skip, limit=limit, orderby=orderby, where=where)
#         # awaitables = (connectionType.resolve_reference(info=info, id=result.id) for result in results)
#         # awaited = await asyncio.gather(*awaitables)
#         return (listType(result) for result in results)    