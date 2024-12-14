import datetime
import strawberry
import uuid
from typing import List, Optional, Union, Annotated, ForwardRef
import typing
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
    remove_constructor,
    
    default_page_resolver,
    default_scalar_resolver,
    default_vector_resolver,
    default_by_id_resolver,

    resolve_field,

    encapsulateInsert,
    encapsulateUpdate,
    encapsulateDelete
)

from src.Dataloaders import getLoadersFromInfo
from src.DBResolvers import DBResolvers

GroupCategoryGQLModel = Annotated["GroupCategoryGQLModel", strawberry.lazy(".groupCategoryGQLModel")]

# GroupTypeGQLModelResolvers = DBResolvers.GroupTypeModel(ForwardRef("GroupTypeGQLModel"))


@strawberry.federation.type(
    keys=["id"], description="""Entity representing a group type (like Faculty)"""
)
class GroupTypeGQLModel(NamedGQLModel):
    @classmethod
    def getLoader(cls, info):
        # return getLoader(info).grouptypes
        return getLoadersFromInfo(info).GroupTypeModel
        
    category_id: typing.Optional[IDType] = strawberry.field(
        description="Unique identifier for the category associated with this group type",
        permission_classes=[
            OnlyForAuthentized
        ]
    )

    category = strawberry.field(
        description="""Detailed information about the category that this group type is associated with""",
        permission_classes=[
            OnlyForAuthentized
        ],
        graphql_type=GroupCategoryGQLModel,
        resolver=default_scalar_resolver(fkey_field_name="category_id")
    )


#####################################################################
#
# Special fields for query
#
#####################################################################
from uoishelpers.resolvers import createInputs
from dataclasses import dataclass
# MembershipInputWhereFilter = Annotated["MembershipInputWhereFilter", strawberry.lazy(".membershipGQLModel")]
@createInputs
@dataclass
class GroupTypeInputWhereFilter:
    id: IDType
    name: str
    category_id: IDType
    # from .membershipGQLModel import MembershipInputWhereFilter
    # memberships: MembershipInputWhereFilter

# from ._GraphResolvers import asPage


group_type_page = strawberry.field(
    description="""Returns a list of groups types (paged)""",
    permission_classes=[
        OnlyForAuthentized
    ],
    graphql_type=typing.List[GroupTypeGQLModel],
    resolver=default_page_resolver(whereType=GroupTypeInputWhereFilter)
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

@strawberry.input(description="")
class GroupTypeUpdateGQLModel:
    id: IDType
    lastchange: datetime.datetime
    name: Optional[str] = None
    name_en: Optional[str] = None
    changedby_id: strawberry.Private[IDType] = None

@strawberry.input(description="")
class GroupTypeInsertGQLModel:
    id: Optional[IDType] = None
    name: Optional[str] = None
    name_en: Optional[str] = None
    createdby_id: strawberry.Private[IDType] = None

@strawberry.type(description="")
class GroupTypeResultGQLModel:
    id: IDType = None
    msg: str = None

    @strawberry.field(description="""Result of grouptype operation""")
    async def group_type(self, info: strawberry.types.Info) -> Union[GroupTypeGQLModel, None]:
        result = await GroupTypeGQLModel.resolve_reference(info, self.id)
        return result
    
@strawberry.mutation(
    description="""Allows a update of group type""",
    permission_classes=[
        OnlyForAuthentized,
        OnlyForAdmins
    ])
async def group_type_update(self, info: strawberry.types.Info, group_type: GroupTypeUpdateGQLModel) -> GroupTypeResultGQLModel:
    return await encapsulateUpdate(info, GroupTypeGQLModel.getLoader(info), group_type, GroupTypeResultGQLModel(id=group_type.id, msg="ok"))

@strawberry.mutation(
    description="""Inserts a group type""",
    permission_classes=[
        OnlyForAuthentized,
        OnlyForAdmins
    ])
async def group_type_insert(self, info: strawberry.types.Info, group_type: GroupTypeInsertGQLModel) -> GroupTypeResultGQLModel:
    return await encapsulateInsert(info, GroupTypeGQLModel.getLoader(info), group_type, GroupTypeResultGQLModel(id=None, msg="ok"))

@strawberry.mutation(
    description="Deletes the group type",
    permission_classes=[
        OnlyForAuthentized,
        OnlyForAdmins
    ])
async def group_type_delete(self, info: strawberry.types.Info, id: IDType) -> GroupTypeResultGQLModel:
    return await encapsulateDelete(info, GroupTypeGQLModel.getLoader(info), id, GroupTypeResultGQLModel(msg="ok", id=None))

