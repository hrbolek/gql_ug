import datetime
import strawberry
import typing
from typing import List, Optional, Union, Annotated
from uoishelpers.resolvers import (
    createInputs2,

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

from .NamedGQLModel import NamedGQLModel
RoleGQLModel = Annotated["RoleGQLModel", strawberry.lazy(".roleGQLModel")]
RoleInputWhereFilter = Annotated["RoleInputWhereFilter", strawberry.lazy(".roleGQLModel")]
# RoleCategoryGQLModel = Annotated["RoleCategoryGQLModel", strawberry.lazy(".roleCategoryGQLModel")]

@createInputs2
class RoleTypeInputWhereFilter:
    id: IDType
    path: str
    name: str
    name_en: str
    # mastertype: "RoleTypeInputWhereFilter" = strawberry.field(description="Type of this type.")
    # from .roleGQLModel import RoleInputWhereFilter
    # roles: RoleInputWhereFilter
    # from .roleCategoryGQLModel import RoleCategoryInputWhereFilter
    # category: RoleCategoryInputWhereFilter


@strawberry.federation.type(
    keys=["id"], description="""Entity representing a role type (like Dean)"""
)
class RoleTypeGQLModel(NamedGQLModel):
    @classmethod
    def getLoader(cls, info):
        return getLoader(info).RoleTypeModel

    # category_id: typing.Optional[IDType] = strawberry.field(
    #     description="",
    #     permission_classes=[
    #         OnlyForAuthentized
    #     ]
    # )

    # category: typing.Optional[RoleCategoryGQLModel] = strawberry.field(
    #     description="""Get role category of this role type""",
    #     permission_classes=[
    #         OnlyForAuthentized
    #     ],
    #     # graphql_type=Optional[RoleCategoryGQLModel],
    #     resolver=ScalarResolver[RoleCategoryGQLModel](fkey_field_name="category_id")
    # )

    path: typing.Optional[str] = strawberry.field(
        description="""Materialized path technique, not implemented""",
        permission_classes=[
            OnlyForAuthentized  
        ],
        default=None
    )

    mastertype_id: typing.Optional[IDType] = strawberry.field(
        description="""Unique identifier for the master type of this group type""",
        permission_classes=[
            OnlyForAuthentized
        ],
        default=None
    )

    mastertype: typing.Optional["RoleTypeGQLModel"] = strawberry.field(
        description="""Detailed information about the master type that this group type is associated with""",
        permission_classes=[
            OnlyForAuthentized
        ],
        resolver=ScalarResolver["RoleTypeGQLModel"](fkey_field_name="mastertype_id")
    )

    subtypes: typing.Optional[List["RoleTypeGQLModel"]] = strawberry.field(
        description="""List of subtypes associated with this group type""",
        permission_classes=[
            OnlyForAuthentized
        ],
        resolver=VectorResolver["RoleTypeGQLModel"](fkey_field_name="mastertype_id", whereType=RoleTypeInputWhereFilter)
    )
#####################################################################
#
# Special fields for query
#
#####################################################################

from uoishelpers.gqlpermissions.UserAbsoluteAccessControlExtension import UserAbsoluteAccessControlExtension
@strawberry.interface(description="Role type related queries")
class RoleTypeQueries:
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
        resolver=PageResolver[RoleTypeGQLModel](whereType=RoleTypeInputWhereFilter)
    )

#####################################################################
#
# Mutation section
#
#####################################################################
import datetime
from uoishelpers.resolvers import (TreeInputStructureMixin)
@strawberry.input(description="")
class RoleTypeInsertGQLModel(TreeInputStructureMixin):
    # category_id: IDType = None
    getLoader = RoleTypeGQLModel.getLoader
    mastertype_id: Optional[IDType] = None
    id: Optional[IDType] = None
    name: Optional[str] = None
    name_en: Optional[str] = None
    subtypes: Optional[List["RoleTypeInsertGQLModel"]] = strawberry.field(
        description="""List of subtypes associated with this role type""",
        default_factory=list,
    )
    # Private pole – bez použití strawberry.field
    path: strawberry.Private[str] = ""
    createdby_id: strawberry.Private["IDType"] = None
    rbacobject: strawberry.Private["IDType"] = None    
   
@strawberry.input(description="")
class RoleTypeUpdateGQLModel:
    id: IDType
    lastchange: datetime.datetime
    name: Optional[str] = None
    name_en: Optional[str] = None
    changedby_id: strawberry.Private[IDType] = None

@strawberry.input(description="")
class RoleTypeDeleteGQLModel:
    id: IDType
    lastchange: datetime.datetime


# @strawberry.type(description="")
# class RoleTypeResultGQLModel:
#     id: IDType = None
#     msg: str = None

#     @strawberry.field(description="""Result of role type operation""")
#     async def role_type(self, info: strawberry.types.Info) -> Union[RoleTypeGQLModel, None]:
#         result = await RoleTypeGQLModel.resolve_reference(info, self.id)
#         return result
    
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

@strawberry.interface(description="Role type related mutations")
class RoleTypeMutations:
    @strawberry.mutation(
        description="""Updates existing roleType record""",
        permission_classes=[
            OnlyForAuthentized,
            # OnlyForAdmins
            # UpdateRoleTypePermission
        ],
        extensions=[
            UserAbsoluteAccessControlExtension[UpdateError, RoleTypeGQLModel](roles=["superadmin"])
        ]
    )
    async def role_type_update(
        self, 
        info: strawberry.types.Info, 
        role_type: RoleTypeUpdateGQLModel,
        user_roles: typing.Any

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
            # OnlyForAdmins
            # InsertRoleTypePermission
        ],
        extensions=[
            UserAbsoluteAccessControlExtension[InsertError, RoleTypeGQLModel](roles=["superadmin"])
        ]
    )
    async def role_type_insert(self, 
        info: strawberry.types.Info, 
        role_type: RoleTypeInsertGQLModel,
        user_roles: typing.Any
    ) -> Union[RoleTypeGQLModel, InsertError[RoleTypeGQLModel]]:
        result = await Insert[RoleTypeGQLModel].DoItSafeWay(info=info, entity=role_type)
        return result

    @strawberry.mutation(
        description="Deletes the roleType",
        permission_classes=[
            OnlyForAuthentized,
            # OnlyForAdmins
        ],
        extensions=[
            UserAbsoluteAccessControlExtension[DeleteError, RoleTypeGQLModel](roles=["superadmin"])
        ]
    )
    async def role_type_delete(
        self, 
        info: strawberry.types.Info, 
        role_type: RoleTypeDeleteGQLModel,
        user_roles: typing.Any
    ) -> Optional[DeleteError[RoleTypeGQLModel]]:
        result = await Delete[RoleTypeGQLModel].DoItSafeWay(info=info, entity=role_type)
        return result


