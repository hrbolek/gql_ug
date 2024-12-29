import datetime
import strawberry
import uuid
from typing import List, Optional, Union, Annotated
from uoishelpers.resolvers import createInputs

from .BaseGQLModel import BaseGQLModel, IDType
from .NamedGQLModel import NamedGQLModel

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

)
from uoishelpers.resolvers import (
    createInputs,

    ScalarResolver,
    PageResolver,
    VectorResolver,

    Insert,
    InsertError,
    Update,
    UpdateError,
    Delete,
    DeleteError
)

from src.Dataloaders import (
    getLoadersFromInfo as getLoader,
    getUserFromInfo)
from src.DBResolvers import DBResolvers

RoleTypeGQLModel = Annotated["RoleTypeGQLModel", strawberry.lazy(".roleTypeGQLModel")]
RoleTypeInputWhereFilter = Annotated["RoleTypeInputWhereFilter", strawberry.lazy(".roleTypeGQLModel")]


@strawberry.federation.type(
    keys=["id"], description="""Entity representing a role type (like Dean)"""
)
class RoleCategoryGQLModel(NamedGQLModel):
    @classmethod
    def getLoader(cls, info):
        return getLoader(info).RoleCategoryModel
      
    role_types = strawberry.field(
        description="""List of roles with this type""",
        permission_classes=[
            OnlyForAuthentized
        ],
        graphql_type=List[RoleTypeGQLModel],
        # resolver=DBResolvers.RoleCategoryModel.types(RoleTypeGQLModel, WhereFilterModel=RoleTypeInputWhereFilter)
        resolver=default_vector_resolver(fkey_field_name="category_id", whereType=RoleTypeInputWhereFilter)
    )
   
#####################################################################
#
# Special fields for query
#
#####################################################################
from uoishelpers.resolvers import createInputs
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
    changedby_id: strawberry.Private[IDType] = None

@strawberry.input(description="Initial data structure for C operation")
class RoleCategoryInsertGQLModel:
    id: Optional[IDType] = strawberry.field(description="primary key", default_factory=uuid.uuid1)
    name: Optional[str] = None
    name_en: Optional[str] = None
    createdby_id: strawberry.Private[IDType] = None

@strawberry.input(description="Data structure for D operation")
class RoleCategoryDeleteGQLModel:
    id: IDType
    lastchange: datetime.datetime

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

) -> Union[RoleCategoryGQLModel, UpdateError[RoleCategoryGQLModel]]:
    result = await Update[RoleCategoryGQLModel].DoItSafeWay(info=info, entity=role_category)
    return result

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

) -> Union[RoleCategoryGQLModel, InsertError[RoleCategoryGQLModel]]:
    result = await Insert[RoleCategoryGQLModel].DoItSafeWay(info=info, entity=role_category)
    return result

@strawberry.mutation(
    description="Deletes the role category",
    permission_classes=[
        OnlyForAuthentized,
        OnlyForAdmins
    ])
async def role_category_delete(self, info: strawberry.types.Info, role_category: RoleCategoryDeleteGQLModel) -> Optional[DeleteError[RoleCategoryGQLModel]]:
    result = await Delete[RoleCategoryGQLModel].DoItSafeWay(info=info, entity=role_category)
    return result
