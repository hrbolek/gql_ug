import datetime
import strawberry
import typing
from typing import List, Optional, Union, Annotated
from uoishelpers.resolvers import (
    createInputs,

    ScalarResolver
)


from .BaseGQLModel import BaseGQLModel, IDType
from ._GraphPermissions import (
    RoleBasedPermission, 
    OnlyForAuthentized,
    OnlyForAdmins,
    RBACPermission
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

from .NamedGQLModel import NamedGQLModel
RoleGQLModel = Annotated["RoleGQLModel", strawberry.lazy(".roleGQLModel")]
RoleInputWhereFilter = Annotated["RoleInputWhereFilter", strawberry.lazy(".roleGQLModel")]
RoleCategoryGQLModel = Annotated["RoleCategoryGQLModel", strawberry.lazy(".roleCategoryGQLModel")]


@strawberry.federation.type(
    keys=["id"], description="""Entity representing a role type (like Dean)"""
)
class RoleTypeGQLModel(NamedGQLModel):
    @classmethod
    def getLoader(cls, info):
        return getLoader(info).RoleTypeModel

    category_id: typing.Optional[IDType] = strawberry.field(
        description="",
        permission_classes=[
            OnlyForAuthentized
        ]
    )

    category: typing.Optional[RoleCategoryGQLModel] = strawberry.field(
        description="""Get role category of this role type""",
        permission_classes=[
            OnlyForAuthentized
        ],
        # graphql_type=Optional[RoleCategoryGQLModel],
        resolver=ScalarResolver[RoleCategoryGQLModel](fkey_field_name="category_id")
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
class RoleTypeInputWhereFilter:
    id: IDType
    name: str
    from .roleGQLModel import RoleInputWhereFilter
    roles: RoleInputWhereFilter

role_type_by_id = strawberry.field(
    description="""Finds a role type by its id""",
    permission_classes=[
        OnlyForAuthentized
    ],
    graphql_type=Optional[RoleTypeGQLModel],
    resolver=default_by_id_resolver()
)

role_type_page = strawberry.field(
    description="""Finds all role types paged""",
    permission_classes=[
        # OnlyForAuthentized
    ],
    graphql_type=List[RoleTypeGQLModel],
    # resolver=DBResolvers.RoleTypeModel.resolve_page(RoleTypeGQLModel, WhereFilterModel=RoleTypeInputWhereFilter)
    resolver=default_page_resolver(whereType=RoleTypeInputWhereFilter)
)

#####################################################################
#
# Mutation section
#
#####################################################################
import datetime
@strawberry.input(description="")
class RoleTypeUpdateGQLModel:
    id: IDType
    lastchange: datetime.datetime
    name: Optional[str] = None
    name_en: Optional[str] = None
    changedby_id: strawberry.Private[IDType] = None

@strawberry.input(description="")
class RoleTypeInsertGQLModel:
    category_id: IDType = None
    id: Optional[IDType] = None
    name: Optional[str] = None
    name_en: Optional[str] = None
    createdby_id: strawberry.Private[IDType] = None
   
@strawberry.input(description="")
class RoleTypeDeleteGQLModel:
    id: IDType
    lastchange: datetime.datetime


@strawberry.type(description="")
class RoleTypeResultGQLModel:
    id: IDType = None
    msg: str = None

    @strawberry.field(description="""Result of role type operation""")
    async def role_type(self, info: strawberry.types.Info) -> Union[RoleTypeGQLModel, None]:
        result = await RoleTypeGQLModel.resolve_reference(info, self.id)
        return result
    
# class UpdateRoleTypePermission(RBACPermission):
#     message = "User is not allowed create new membership"
#     async def has_permission(self, source, info: strawberry.types.Info, role_type: RoleTypeUpdateGQLModel) -> bool:
#         adminRoleNames = ["administrátor"]
#         allowedRoleNames = []
#         role = await self.resolveUserRole(info, 
#             rbacobject=role_type.id, 
#             adminRoleNames=adminRoleNames, 
#             allowedRoleNames=allowedRoleNames)
        
#         if not role: return False
#         return True

@strawberry.mutation(
    description="""Updates existing roleType record""",
    permission_classes=[
        OnlyForAuthentized,
        OnlyForAdmins
        # UpdateRoleTypePermission
    ])
async def role_type_update(self, 
    info: strawberry.types.Info, 
    role_type: RoleTypeUpdateGQLModel

) -> Union[RoleTypeGQLModel, UpdateError[RoleTypeGQLModel]]:
    result = await Update[RoleTypeGQLModel].DoItSafeWay(info=info, entity=role_type)
    return result

# class InsertRoleTypePermission(RBACPermission):
#     message = "User is not allowed create new membership"
#     async def has_permission(self, source, info: strawberry.types.Info, role_type: RoleTypeInsertGQLModel) -> bool:
#         adminRoleNames = ["administrátor"]
#         allowedRoleNames = []
#         role = await self.resolveUserRole(info, 
#             rbacobject=role_type.id, 
#             adminRoleNames=adminRoleNames, 
#             allowedRoleNames=allowedRoleNames)
        
#         if not role: return False
#         return True

@strawberry.mutation(
    description="""Inserts a new roleType record""",
    permission_classes=[
        OnlyForAuthentized,
        OnlyForAdmins
        # InsertRoleTypePermission
    ])
async def role_type_insert(self, 
    info: strawberry.types.Info, 
    role_type: RoleTypeInsertGQLModel

) -> Union[RoleTypeGQLModel, InsertError[RoleTypeGQLModel]]:
    result = await Insert[RoleTypeGQLModel].DoItSafeWay(info=info, entity=role_type)
    return result

@strawberry.mutation(
    description="Deletes the roleType",
    permission_classes=[
        OnlyForAuthentized,
        OnlyForAdmins
    ])
async def role_type_delete(self, info: strawberry.types.Info, role_type: RoleTypeDeleteGQLModel) -> Optional[DeleteError[RoleTypeGQLModel]]:
    result = await Delete[RoleTypeGQLModel].DoItSafeWay(info=info, entity=role_type)
    return result


