import datetime
import strawberry
import uuid
from typing import List, Optional, Union, Annotated
from .BaseGQLModel import BaseGQLModel, IDType
from ._GraphPermissions import RoleBasedPermission, OnlyForAuthentized
from ._GraphResolvers import (
    resolve_id,
    resolve_name,
    resolve_name_en,
    resolve_changedby,
    resolve_created,
    resolve_lastchange,
    resolve_createdby
)

from src.Dataloaders import (
    getLoadersFromInfo as getLoader,
    getUserFromInfo)

RoleTypeGQLModel = Annotated["RoleTypeGQLModel", strawberry.lazy(".roleTypeGQLModel")]

@strawberry.federation.type(
    keys=["id"], description="""Entity representing a role type (like Dean)"""
)
class RoleCategoryGQLModel(BaseGQLModel):
    @classmethod
    def getLoader(cls, info):
        return getLoader(info).rolecategories
    
    id = resolve_id
    name = resolve_name
    name_en = resolve_name_en
    changedby = resolve_changedby
    created = resolve_created
    lastchange = resolve_lastchange
    createdby = resolve_createdby

    @strawberry.field(
        description="""List of roles with this type""",
    permission_classes=[OnlyForAuthentized(isList=True)])
    async def role_types(self, info: strawberry.types.Info) -> List["RoleTypeGQLModel"]:
        # result = await resolveRoleForRoleType(session,  self.id)
        loader = getLoader(info).roletypes
        rows = await loader.filter_by(category_id=self.id)
        return rows
    
    RBACObjectGQLModel = Annotated["RBACObjectGQLModel", strawberry.lazy(".RBACObjectGQLModel")]
    @strawberry.field(
        description="""""",
        permission_classes=[OnlyForAuthentized()])
    async def rbacobject(self, info: strawberry.types.Info) -> Optional[RBACObjectGQLModel]:
        from .RBACObjectGQLModel import RBACObjectGQLModel
        result = None if self.createdby is None else await RBACObjectGQLModel.resolve_reference(info, self.createdby)
        return result        
#####################################################################
#
# Special fields for query
#
#####################################################################
@strawberry.field(
    description="""Finds a role type by its id""",
    permission_classes=[OnlyForAuthentized()])
async def role_category_by_id(
    self, info: strawberry.types.Info, id: IDType
) -> Union[RoleCategoryGQLModel, None]:
    result = await RoleCategoryGQLModel.resolve_reference(info,  id)
    return result

@strawberry.field(
    description="""gets role category page""",
    permission_classes=[OnlyForAuthentized(isList=True)])
async def role_category_page(
    self, info: strawberry.types.Info, skip: Optional[int] = 0, limit: Optional[int] = 10
) -> List[RoleCategoryGQLModel]:
    loader = getLoader(info).rolecategories
    result = await loader.page(skip, limit)
    return result

#####################################################################
#
# Mutation section
#
#####################################################################
import datetime

@strawberry.input
class RoleCategoryUpdateGQLModel:
    id: IDType
    lastchange: datetime.datetime
    name: Optional[str] = None
    name_en: Optional[str] = None
    changedby: strawberry.Private[uuid.UUID] = None

@strawberry.input
class RoleCategoryInsertGQLModel:
    id: Optional[uuid.UUID] = None
    name: Optional[str] = None
    name_en: Optional[str] = None
    createdby: strawberry.Private[uuid.UUID] = None

@strawberry.type
class RoleCategoryResultGQLModel:
    id: IDType = None
    msg: str = None

    @strawberry.field(description="""Result of role category operation""")
    async def role_category(self, info: strawberry.types.Info) -> Union[RoleCategoryGQLModel, None]:
        result = await RoleCategoryGQLModel.resolve_reference(info, self.id)
        return result
    
@strawberry.mutation(
    description="""Updates a role category""",
    permission_classes=[OnlyForAuthentized()])
async def role_category_update(self, 
    info: strawberry.types.Info, 
    role_category: RoleCategoryUpdateGQLModel

) -> RoleCategoryResultGQLModel:
    user = getUserFromInfo(info)
    role_category.changedby = user["id"]

    loader = getLoader(info).rolecategories
    row = await loader.update(role_category)

    result = RoleCategoryResultGQLModel()
    result.id = role_category.id
    result.msg = result.msg = "fail" if row is None else "ok"
    
    return result

@strawberry.mutation(
    description="""Inserts a role category""",
    permission_classes=[OnlyForAuthentized()])
async def role_category_insert(self, 
    info: strawberry.types.Info, 
    role_category: RoleCategoryInsertGQLModel

) -> RoleCategoryResultGQLModel:
    user = getUserFromInfo(info)
    role_category.createdby = user["id"]
    
    loader = getLoader(info).rolecategories
    row = await loader.insert(role_category)

    result = RoleCategoryResultGQLModel()
    result.msg = "ok"
    result.id = row.id
    
    return result