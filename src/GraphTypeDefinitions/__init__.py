import typing
from typing import List, Union, Optional
import strawberry
import uuid
import datetime

# from contextlib import asynccontextmanager


# @asynccontextmanager
# async def withInfo(info):
#     asyncSessionMaker = info.context["asyncSessionMaker"]
#     async with asyncSessionMaker() as session:
#         try:
#             yield session
#         finally:
#             pass


# def getLoader(info):
#     return info.context["all"]


import datetime
    
###########################################################################################################################
#
# Schema je pouzito v main.py, vsimnete si parametru types, obsahuje vyjmenovane modely. Bez explicitniho vyjmenovani
# se ve schema objevi jen ty struktury, ktere si strawberry dokaze odvodit z Query. Protoze v teto konkretni implementaci
# nektere modely nejsou s Query propojene je potreba je explicitne vyjmenovat. Jinak ve federativnim schematu nebude
# dostupne rozsireni, ktere tento prvek federace implementuje.
#
###########################################################################################################################

from .query import Query
from .mutation import Mutation

from .userGQLModel import UserGQLModel # jen jako demo
from .groupGQLModel import GroupGQLModel
from .groupTypeGQLModel import GroupTypeGQLModel
from .membershipGQLModel import MembershipGQLModel
from .roleGQLModel import RoleGQLModel
from .roleCategoryGQLModel import RoleCategoryGQLModel
from .roleTypeGQLModel import RoleTypeGQLModel

from .RBACObjectGQLModel import RBACObjectGQLModel
from .BaseGQLModel import IDType


from strawberry.extensions import SchemaExtension
from starlette.requests import Request
# import inspect
import aiohttp
import os

class MyExtension(SchemaExtension):

    # async def on_execute(self):
    #     print("->on_execute", flush=True)
    #     yield
    #     print("on_execute->", flush=True)

    async def resolve(self, _next, root, info: strawberry.Info, *args, **kwargs):
        # print(f"MEx {info.field_name}({', '.join(key+'='+str(value) for key, value in kwargs.items())})", flush=True)
        # print(f"MEx {info.root_value}, {info}")
        if root is not None:
            # print(f"MEx {self}, {type(root._data).__name__}(id={root._data.id}).{info.field_name}")
            pass
        else:
            # print(f"Mex {self}, {root}.{info.field_name}")
            pass
        result = _next(root, info, *args, **kwargs)
        if info.is_awaitable(result):
            result = await result
        # print(f"Mex {info} -> {result}")
        return result
  

schema = strawberry.federation.Schema(query=Query, types=(RBACObjectGQLModel, IDType), mutation=Mutation, extensions=[])
# schema = strawberry.federation.Schema(query=Query, types=(RBACObjectGQLModel, IDType), mutation=Mutation, extensions=[MyExtension])
schema.extensions.append(MyExtension)
# schema = strawberry.federation.Schema(query=Query)
