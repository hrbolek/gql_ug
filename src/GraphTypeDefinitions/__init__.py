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

from uoishelpers.schema import WhoAmIExtension

# class MyExtension(SchemaExtension):

#     # async def on_execute(self):
#     #     print("->on_execute", flush=True)
#     #     yield
#     #     print("on_execute->", flush=True)

#     async def resolve(self, _next, root, info: strawberry.Info, *args, **kwargs):
#         # print(f"MEx {info.field_name}({', '.join(key+'='+str(value) for key, value in kwargs.items())})", flush=True)
#         # print(f"MEx {info.root_value}, {info}")
#         if root is not None:
#             # print(f"MEx {self}, {type(root._data).__name__}(id={root._data.id}).{info.field_name}")
#             pass
#         else:
#             # print(f"Mex {self}, {root}.{info.field_name}")
#             pass
#         result = _next(root, info, *args, **kwargs)
#         if info.is_awaitable(result):
#             result = await result
#         # print(f"Mex {info} -> {result}")
#         return result
  

# apolloQuery = "query __ApolloGetServiceDefinition__ { _service { sdl } }"
# graphiQLQuery = "\n    query IntrospectionQuery {\n      __schema {\n        \n        queryType { name }\n        mutationType { name }\n        subscriptionType { name }\n        types {\n          ...FullType\n        }\n        directives {\n          name\n          description\n          \n          locations\n          args(includeDeprecated: true) {\n            ...InputValue\n          }\n        }\n      }\n    }\n\n    fragment FullType on __Type {\n      kind\n      name\n      description\n      \n      fields(includeDeprecated: true) {\n        name\n        description\n        args(includeDeprecated: true) {\n          ...InputValue\n        }\n        type {\n          ...TypeRef\n        }\n        isDeprecated\n        deprecationReason\n      }\n      inputFields(includeDeprecated: true) {\n        ...InputValue\n      }\n      interfaces {\n        ...TypeRef\n      }\n      enumValues(includeDeprecated: true) {\n        name\n        description\n        isDeprecated\n        deprecationReason\n      }\n      possibleTypes {\n        ...TypeRef\n      }\n    }\n\n    fragment InputValue on __InputValue {\n      name\n      description\n      type { ...TypeRef }\n      defaultValue\n      isDeprecated\n      deprecationReason\n    }\n\n    fragment TypeRef on __Type {\n      kind\n      name\n      ofType {\n        kind\n        name\n        ofType {\n          kind\n          name\n          ofType {\n            kind\n            name\n            ofType {\n              kind\n              name\n              ofType {\n                kind\n                name\n                ofType {\n                  kind\n                  name\n                  ofType {\n                    kind\n                    name\n                  }\n                }\n              }\n            }\n          }\n        }\n      }\n    }\n  "

# class OauthExtension(WhoAmIExtension):

#     async def on_execute(self):
#         query = self.execution_context.query
#         if query not in [apolloQuery, graphiQLQuery]:
#             whoami = await self.ug_query(query=myquery)
#             whoami = whoami["data"]["me"]
#         else:
#             whoami = {}
#         self.execution_context.context["user"] = whoami


schema = strawberry.federation.Schema(
    query=Query, 
    types=(RBACObjectGQLModel, IDType), 
    mutation=Mutation, 
    extensions=[]
)
readonlyschema = strawberry.federation.Schema(query=Query, types=(RBACObjectGQLModel, IDType))

# schema = strawberry.federation.Schema(query=Query, types=(RBACObjectGQLModel, IDType), mutation=Mutation, extensions=[MyExtension])
# schema.extensions.append(MyExtension)
# schema = strawberry.federation.Schema(query=Query)

class UGWhoAmIExtension(WhoAmIExtension):
    async def ug_query(self, query, variables={}):
        context = self.execution_context.context
        # print(f"ug_query context A = {context}")
        # result = await self.execution_context.schema.execute(query=query, variable_values=variables, context_value=context)
        result = await readonlyschema.execute(query=query, variable_values=variables, context_value=context)
        # print(f"ug_query context B = {context}")
        result = strawberry.asdict(result)
        # print(f"result = {result}")
        return result

    # async def on_execute(self):
    #     query = self.execution_context.query
    #     if query not in [WhoAmIExtension.apolloQuery, WhoAmIExtension.graphiQLQuery]:
    #         whoami = await self.ug_query(query=WhoAmIExtension.mequery)
    #         whoami = whoami["data"]["me"]
    #     else:
    #         whoami = {}
    #     self.execution_context.context["user"] = whoami

    #     # print("->on_execute", self.execution_context.query, flush=True)
    #     yield

    pass

schema.extensions.append(UGWhoAmIExtension)