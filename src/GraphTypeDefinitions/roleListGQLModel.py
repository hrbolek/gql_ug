import strawberry
import asyncio
from typing import List, Annotated, Optional
from uoishelpers.resolvers import createInputs

from .BaseGQLModel import BaseGQLModel, IDType
from ._GraphResolvers import (
    remove_constructor
    )

from ._GraphPermissions import (
    RoleBasedPermission, 
    OnlyForAuthentized,
    RBACPermission
)
from src.Dataloaders import (
    getLoadersFromInfo,
    getUserFromInfo)
from src.DBResolvers import DBResolvers

RoleTypeGQLModel = Annotated["RoleTypeGQLModel", strawberry.lazy(".roleTypeGQLModel")]

@strawberry.type(description="")
class RoleTypeListGQLModel(BaseGQLModel):
    @classmethod
    def getLoader(cls, info: strawberry.types.Info):
        return getLoadersFromInfo(info).RoleTypeListModel
    
    @classmethod
    async def resolve_reference(cls, info: strawberry.types.Info, id: IDType):
        if id is not None:
            loader = cls.getLoader(info)
            if isinstance(id, str): id = IDType(id)
            rows = await loader.filter_by(list_id=id)
            row = next(rows, None)
            return None if row is None else cls(id=id) # it has not any real row in a table
        return None


    id: IDType = None

    # changedby = resolve_changedby
    # lastchange = resolve_lastchange
    # created = resolve_created
    # createdby = resolve_createdby
    # rbacobject = resolve_rbacobject

    @strawberry.field(
        description="""All roletypes associated with role type list""",
        permission_classes=[OnlyForAuthentized])
    async def roletypes(self, info: strawberry.types.Info) -> List["RoleTypeGQLModel"]:
        from .roleTypeGQLModel import RoleTypeGQLModel
        loader = RoleTypeListGQLModel.getLoader(info)
        # print("self.id", self.id, type(self.id), flush=True)
        results = await loader.filter_by(list_id=self.id)
        results = (RoleTypeGQLModel.resolve_reference(info, id=r.type_id) for r in results)
        return await asyncio.gather(*results)
    pass

# async def resolve_role_type_list_by_id(
#     self, info: strawberry.types.Info, list_id: IDType
# ) -> List["RoleTypeGQLModel"]:
#     # print("resolve_role_type_list_by_id", list_id)
#     loader = RoleTypeListGQLModel.getLoader(info)
#     roles = await loader.filter_by(list_id=list_id)
#     # print("resolve_role_type_list_by_id", list_id)
#     return roles  

@strawberry.field(
    description="""returns the list of roles types associated to id""",
    permission_classes=[OnlyForAuthentized])
async def role_type_list_by_id(
    self, info: strawberry.types.Info, id: IDType
) -> Optional["RoleTypeListGQLModel"]:
    result = await RoleTypeListGQLModel.resolve_reference(info=info, id=id)
    # roles = await resolve_role_type_list_by_id(self, info, id)
    return result

import asyncio
@strawberry.type(description="")
class RoleTypeListResult:
    id: IDType = None
    msg: str = None

    @strawberry.field(
        description="""Result of user operation""",
        permission_classes=[OnlyForAuthentized])
    async def role_typelist(self, info: strawberry.types.Info) -> Optional["RoleTypeListGQLModel"]:
        # from .roleTypeGQLModel import RoleTypeGQLModel
        
        # rows = await resolve_role_type_list_by_id(self, info, list_id=self.id)
        # result = (RoleTypeGQLModel.resolve_reference(info=info, id=r.type_id) for r in rows)
        
        # return await asyncio.gather(*result)
        return await RoleTypeListGQLModel.resolve_reference(info=info, id=self.id)

import dataclasses
@dataclasses.dataclass
class RoleTypeInsertIntoList:
    type_id: IDType = None
    list_id: IDType = None
    createdby: strawberry.Private[IDType] = None

# class InsertMembershipPermission(RBACPermission):
#     message = "User is not allowed create new membership"
#     async def has_permission(self, source, info: strawberry.types.Info, membership: "MembershipInsertGQLModel") -> bool:
#         adminRoleNames = ["administrátor"]
#         allowedRoleNames = ["garant"]
#         role = await self.resolveUserRole(info, 
#             rbacobject=membership.group_id, 
#             adminRoleNames=adminRoleNames, 
#             allowedRoleNames=allowedRoleNames)
        
#         if not role: return False
#         return True

@strawberry.field(
    description="""adds to a list of role types new item""",
    permission_classes=[OnlyForAuthentized])
async def role_type_list_add(
    self, info: strawberry.types.Info, role_type_list_id: IDType, role_type_id: IDType
) -> "RoleTypeListResult":
    list_id = IDType(role_type_list_id) if isinstance(role_type_list_id, str) else role_type_list_id
    type_id = IDType(role_type_id) if isinstance(role_type_id, str) else role_type_id
    loader = RoleTypeListGQLModel.getLoader(info)
    roles = await loader.filter_by(list_id=list_id, type_id=type_id)
    # roles = [*roles]
    
    isIn = next(roles, None)
    
    result = RoleTypeListResult(id=list_id, msg="fail")
    # print(result, flush=True)
    # print(result.id, type(result.id), flush=True)
    # result.msg = "fail" if isIn is None else "ok"
    # result.msg = "fail"
    if isIn is None:
        whatToInsert = RoleTypeInsertIntoList(type_id=type_id, list_id=list_id)
        # print("whatToInsert", whatToInsert, flush=True)
        # print("whatToInsert", whatToInsert.list_id, flush=True)
        # print("whatToInsert", whatToInsert.type_id, flush=True)
        user = getUserFromInfo(info)
        whatToInsert.createdby = user["id"]
            
        row = await loader.insert(whatToInsert)
        result.msg = "fail" if row is None else "ok"
    return result

@dataclasses.dataclass
class RoleTypeDeleteFormList:
    id: IDType = None

@strawberry.field(
    description="""Finds an user by their id""",
    permission_classes=[OnlyForAuthentized])
async def role_type_list_remove(
    self, info: strawberry.types.Info, role_type_list_id: IDType, role_type_id: IDType
) -> "RoleTypeListResult":
    list_id = IDType(role_type_list_id) if isinstance(role_type_list_id, str) else role_type_list_id
    type_id = IDType(role_type_id) if isinstance(role_type_id, str) else role_type_id
    # print(list_id, type(list_id), flush=True)
    # print(type_id, type(type_id), flush=True)
    loader = RoleTypeListGQLModel.getLoader(info)
    roles = await loader.filter_by(list_id=list_id, type_id=type_id)
    # isIn = False
    isIn = next(roles, None)
    print(isIn, isIn.id, flush=True)
    result = RoleTypeListResult(id=list_id, msg="ok")
    result.msg = "fail" if isIn is None else "ok"
    # if isIn:
    #     await loader.delete(isIn.id)
    return result
    
from .BaseGQLModel import Connection
class RoleTypeListConnection(Connection[RoleTypeListGQLModel]):
    pass
