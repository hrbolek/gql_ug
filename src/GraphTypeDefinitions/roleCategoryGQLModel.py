import datetime
import strawberry
import uuid
from typing import List, Optional, Union, Annotated
from uoishelpers.resolvers import createInputs

from .BaseGQLModel import BaseGQLModel, IDType

from ._GraphPermissions import (
    RoleBasedPermission, 
    OnlyForAuthentized,
    RBACPermission,
    OnlyForAdmins
)
from ._GraphResolvers import (

    resolve_field,
    default_resolver,
    default_vector_resolver,
    default_scalar_resolver,
    default_page_resolver,
    default_by_id_resolver,

    remove_constructor,

    encapsulateInsert,
    encapsulateUpdate,
    encapsulateDelete
)

from src.Dataloaders import (
    getLoadersFromInfo as getLoader,
    getUserFromInfo)
from src.DBResolvers import DBResolvers

RoleTypeGQLModel = Annotated["RoleTypeGQLModel", strawberry.lazy(".roleTypeGQLModel")]
RoleTypeInputWhereFilter = Annotated["RoleTypeInputWhereFilter", strawberry.lazy(".roleTypeGQLModel")]

@remove_constructor
@strawberry.federation.type(
    keys=["id"], description="""Entity representing a role type (like Dean)"""
)
class RoleCategoryGQLModel(BaseGQLModel):
    @classmethod
    def getLoader(cls, info):
        return getLoader(info).RoleCategoryModel
    
    from ._GraphResolvers import (
        resolve_name as name,
        resolve_name_en as name_en
    )
   
   
    role_types = strawberry.field(
        description="""List of roles with this type""",
        permission_classes=[
            OnlyForAuthentized
        ],
        graphql_type=List[RoleTypeGQLModel],
        # resolver=DBResolvers.RoleCategoryModel.types(RoleTypeGQLModel, WhereFilterModel=RoleTypeInputWhereFilter)
        resolver=default_vector_resolver(fkey_field_name="category_id", whereType=RoleTypeInputWhereFilter)
    )

    RBACObjectGQLModel = Annotated["RBACObjectGQLModel", strawberry.lazy(".RBACObjectGQLModel")]
    @strawberry.field(
        description="""""",
        permission_classes=[OnlyForAuthentized])
    async def rbacobject(self, info: strawberry.types.Info) -> Optional[RBACObjectGQLModel]:
        from .RBACObjectGQLModel import RBACObjectGQLModel
        createdby = resolve_field(self=self, field_name="createdby")
        result = await RBACObjectGQLModel.resolve_reference(info, createdby)
        return result        
    
#####################################################################
#
# Special fields for query
#
#####################################################################
from .utils import createInputs
from dataclasses import dataclass

@createInputs
@dataclass
class RoleCategoryInputWhereFilter:
    name: str
    name_en: str
    roletypes: RoleTypeInputWhereFilter

role_category_by_id = strawberry.field(
    description="""Finds a role category by its id""",
    permission_classes=[
        OnlyForAuthentized
    ],
    graphql_type=Optional[RoleCategoryGQLModel],
    # resolver=DBResolvers.RoleCategoryModel.resolve_by_id(RoleCategoryGQLModel)
    resolver=default_by_id_resolver()
)

role_category_page = strawberry.field(
    description="""gets role category page""",
    permission_classes=[
        OnlyForAuthentized
    ],
    graphql_type=List[RoleCategoryGQLModel],
    # resolver=DBResolvers.RoleCategoryModel.resolve_page(RoleCategoryGQLModel, WhereFilterModel=RoleCategoryInputWhereFilter)
    resolver=default_page_resolver(whereType=RoleCategoryInputWhereFilter)
)
#####################################################################
#
# Mutation section
#
#####################################################################
import datetime

@strawberry.input(description="Data structure for U operation")
class RoleCategoryUpdateGQLModel:
    id: IDType
    lastchange: datetime.datetime
    name: Optional[str] = None
    name_en: Optional[str] = None
    changedby: strawberry.Private[IDType] = None

@strawberry.input(description="Initial data structure for C operation")
class RoleCategoryInsertGQLModel:
    id: Optional[IDType] = strawberry.field(description="primary key", default_factory=uuid.uuid1)
    name: Optional[str] = None
    name_en: Optional[str] = None
    createdby: strawberry.Private[IDType] = None

@strawberry.type(description="")
class RoleCategoryResultGQLModel:
    id: IDType = None
    msg: str = None

    @strawberry.field(description="""Result of role category operation""")
    async def role_category(self, info: strawberry.types.Info) -> Union[RoleCategoryGQLModel, None]:
        result = await RoleCategoryGQLModel.resolve_reference(info, self.id)
        return result
    
# class UpdateRoleCategoryPermission(RBACPermission):
#     message = "User is not allowed create new role category"
#     async def has_permission(self, source, info: strawberry.types.Info, role_category: RoleCategoryUpdateGQLModel) -> bool:
#         adminRoleNames = ["administrátor"]
#         allowedRoleNames = []
#         role = await self.resolveUserRole(info, 
#             rbacobject=role_category.id, 
#             adminRoleNames=adminRoleNames, 
#             allowedRoleNames=allowedRoleNames)
        
#         if not role: return False
#         return True

@strawberry.mutation(
    description="""Updates a role category""",
    permission_classes=[
        OnlyForAuthentized,
        OnlyForAdmins
        # UpdateRoleCategoryPermission
    ])
async def role_category_update(self, 
    info: strawberry.types.Info, 
    role_category: RoleCategoryUpdateGQLModel

) -> RoleCategoryResultGQLModel:
    return await encapsulateUpdate(info, RoleCategoryGQLModel.getLoader(info), role_category, RoleCategoryResultGQLModel(id=role_category.id, msg="ok"))

# class InsertRoleCategoryPermission(RBACPermission):
#     message = "User is not allowed create new role category"
#     async def has_permission(self, source, info: strawberry.types.Info, role_category: RoleCategoryInsertGQLModel) -> bool:
#         adminRoleNames = ["administrátor"]
#         allowedRoleNames = []
#         role = await self.resolveUserRole(info, 
#             rbacobject=role_category.id, 
#             adminRoleNames=adminRoleNames, 
#             allowedRoleNames=allowedRoleNames)
        
#         if not role: return False
#         return True

@strawberry.mutation(
    description="""Inserts a role category""",
    permission_classes=[
        OnlyForAuthentized,
        OnlyForAdmins
    ])
async def role_category_insert(self, 
    info: strawberry.types.Info, 
    role_category: RoleCategoryInsertGQLModel

) -> RoleCategoryResultGQLModel:
    return await encapsulateInsert(info, RoleCategoryGQLModel.getLoader(info), role_category, RoleCategoryResultGQLModel(msg="ok", id=None))

@strawberry.mutation(
    description="Deletes the role category",
    permission_classes=[
        OnlyForAuthentized,
        OnlyForAdmins
    ])
async def role_category_delete(self, info: strawberry.types.Info, id: IDType) -> RoleCategoryResultGQLModel:
    return await encapsulateDelete(info, RoleCategoryGQLModel.getLoader(info), id, RoleCategoryResultGQLModel(msg="ok", id=None))

from .BaseGQLModel import Connection
class RoleCategoryConnection(Connection[RoleCategoryGQLModel]):
    pass
