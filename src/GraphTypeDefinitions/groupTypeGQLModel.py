import datetime
import strawberry
import uuid
from typing import List, Optional, Union, Annotated, ForwardRef
import typing
from uoishelpers.resolvers import createInputs2

from .BaseGQLModel import BaseGQLModel, IDType
from .NamedGQLModel import NamedGQLModel

from ._GraphPermissions import (
    RoleBasedPermission, 
    OnlyForAuthentized,
    RBACPermission,
    OnlyForAdmins
)
from ._GraphResolvers import (
    remove_constructor,
    
    default_scalar_resolver,
    default_by_id_resolver,

    resolve_field,

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



from src.Dataloaders import getLoadersFromInfo
from src.DBResolvers import DBResolvers


# GroupTypeGQLModelResolvers = DBResolvers.GroupTypeModel(ForwardRef("GroupTypeGQLModel"))

@createInputs2
class GroupTypeInputWhereFilter:
    id: IDType
    name: str
    name_en: str
    # category_id: IDType
    # from .membershipGQLModel import MembershipInputWhereFilter
    # memberships: MembershipInputWhereFilter

@strawberry.federation.type(
    keys=["id"], description="""Entity representing a group type (like Faculty)"""
)
class GroupTypeGQLModel(NamedGQLModel):
    @classmethod
    def getLoader(cls, info):
        # return getLoader(info).grouptypes
        return getLoadersFromInfo(info).GroupTypeModel
        
    # category_id: typing.Optional[IDType] = strawberry.field(
    #     description="Unique identifier for the category associated with this group type",
    #     permission_classes=[
    #         OnlyForAuthentized
    #     ]
    # )

    # category: typing.Optional[GroupCategoryGQLModel] = strawberry.field(
    #     description="""Detailed information about the category that this group type is associated with""",
    #     permission_classes=[
    #         OnlyForAuthentized
    #     ],
    #     resolver=default_scalar_resolver(fkey_field_name="category_id")
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

    mastertype: typing.Optional["GroupTypeGQLModel"] = strawberry.field(
        description="""Detailed information about the master type that this group type is associated with""",
        permission_classes=[
            OnlyForAuthentized
        ],
        resolver=ScalarResolver["GroupTypeGQLModel"](fkey_field_name="mastertype_id")
    )

    subtypes: typing.Optional[List["GroupTypeGQLModel"]] = strawberry.field(
        description="""List of subtypes associated with this group type""",
        permission_classes=[
            OnlyForAuthentized
        ],
        resolver=VectorResolver["GroupTypeGQLModel"](fkey_field_name="mastertype_id", whereType=GroupTypeInputWhereFilter)
    )
#####################################################################
#
# Special fields for query
#
#####################################################################
from dataclasses import dataclass
# MembershipInputWhereFilter = Annotated["MembershipInputWhereFilter", strawberry.lazy(".membershipGQLModel")]

# from ._GraphResolvers import asPage

@strawberry.interface(description="group type related queries")
class GroupTypeQueries:
    group_type_page = strawberry.field(
        description="""Returns a list of groups types (paged)""",
        permission_classes=[
            OnlyForAuthentized
        ],
        graphql_type=typing.List[GroupTypeGQLModel],
        resolver=PageResolver[GroupTypeGQLModel](whereType=GroupTypeInputWhereFilter)
    )

    group_type_by_id = strawberry.field(
        description="""Finds a group type by its id""",
        permission_classes=[
            OnlyForAuthentized
        ],
        graphql_type=typing.Optional[GroupTypeGQLModel],
        resolver=default_by_id_resolver()
    )

#####################################################################
#
# Mutation section
#
#####################################################################
import datetime
from uoishelpers.resolvers import InputModelMixin, TreeInputStructureMixin

@strawberry.input(description="")
class GroupTypeInsertGQLModel(TreeInputStructureMixin):
    getLoader = GroupTypeGQLModel.getLoader
    id: Optional[IDType] = None
    name: Optional[str] = None
    name_en: Optional[str] = None
    mastertype_id: Optional[IDType] = strawberry.field(description="", default=None)
    subtypes: Optional[List["GroupTypeInsertGQLModel"]] = strawberry.field(
        description="""List of subtypes associated with this group type""", 
        default_factory=list
    )

    # Private pole – bez použití strawberry.field
    path: strawberry.Private[str] = ""
    createdby_id: strawberry.Private["IDType"] = None
    rbacobject: strawberry.Private["IDType"] = None    


@strawberry.input(description="")
class GroupTypeUpdateGQLModel:
    id: IDType
    lastchange: datetime.datetime
    mastertype_id: Optional[IDType] = strawberry.field(description="", default=strawberry.UNSET)
    name: Optional[str] = strawberry.field(description="", default=strawberry.UNSET)
    name_en: Optional[str] = strawberry.field(description="", default=strawberry.UNSET)
    changedby_id: strawberry.Private[IDType] = strawberry.UNSET

@strawberry.input(description="")
class GroupTypeDeleteGQLModel:
    id: IDType
    lastchange: datetime.datetime

# @strawberry.type(description="")
# class GroupTypeResultGQLModel:
#     id: IDType = None
#     msg: str = None

#     @strawberry.field(description="""Result of grouptype operation""")
#     async def group_type(self, info: strawberry.types.Info) -> Union[GroupTypeGQLModel, None]:
#         result = await GroupTypeGQLModel.resolve_reference(info, self.id)
#         return result
    
from uoishelpers.gqlpermissions.UserAbsoluteAccessControlExtension import UserAbsoluteAccessControlExtension

@strawberry.interface(description="Group type related mutations")
class GroupTypeMutations:
    @strawberry.mutation(
        description="""Allows a update of group type""",
        permission_classes=[
            OnlyForAuthentized,
            # OnlyForAdmins
        ],
        extensions=[
            UserAbsoluteAccessControlExtension[UpdateError, GroupTypeUpdateGQLModel](roles=["superadmin"])
        ]
    )
    async def group_type_update(
        self, 
        info: strawberry.types.Info, 
        group_type: GroupTypeUpdateGQLModel,
        user_roles: typing.Any
    ) -> Union[GroupTypeGQLModel, UpdateError[GroupTypeGQLModel]]:
        result = await Update[GroupTypeGQLModel].DoItSafeWay(info=info, entity=group_type)
        return result

    @strawberry.mutation(
        description="""Inserts a group type""",
        permission_classes=[
            OnlyForAuthentized,
            # OnlyForAdmins
        ],
        extensions=[
            UserAbsoluteAccessControlExtension[InsertError, GroupTypeUpdateGQLModel](roles=["superadmin"])
        ]
    )
    async def group_type_insert(
        self, 
        info: strawberry.types.Info, 
        group_type: GroupTypeInsertGQLModel,
        user_roles: typing.Any
    ) -> Union[GroupTypeGQLModel, InsertError[GroupTypeGQLModel]]:
        result = await Insert[GroupTypeGQLModel].DoItSafeWay(info=info, entity=group_type)
        return result

    @strawberry.mutation(
        description="Deletes the group type",
        permission_classes=[
            OnlyForAuthentized,
            # OnlyForAdmins
        ],
        extensions=[
            UserAbsoluteAccessControlExtension[DeleteError, GroupTypeUpdateGQLModel](roles=["superadmin"])
        ]
    )
    async def group_type_delete(
        self, 
        info: strawberry.types.Info, 
        group_type: GroupTypeDeleteGQLModel,
        user_roles: typing.Any
    ) -> Optional[DeleteError[GroupTypeGQLModel]]:
        result = await Delete[GroupTypeGQLModel].DoItSafeWay(info=info, entity=group_type)
        return result

