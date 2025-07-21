import datetime
import strawberry
from dataclasses import dataclass

from typing import List, Optional, Union, Annotated
import typing
import strawberry.types
from uoishelpers.resolvers import createInputs

from ..BaseGQLModel import BaseGQLModel, IDType
from ..NamedGQLModel import NamedGQLModel
from .._GraphPermissions import (
    RoleBasedPermission, 
    OnlyForAuthentized,
    RBACPermission,
    OnlyForAdmins
)
from uoishelpers.resolvers import (
    getLoadersFromInfo,

    ScalarResolver,
    VectorResolver,
    PageResolver,

    Insert,
    InsertError,
    Update,
    UpdateError,
    Delete,
    DeleteError
)
from uoishelpers.gqlpermissions import (
    SimpleDeletePermission,
    SimpleInsertPermission,
    SimpleUpdatePermission
)

GroupTypeGQLModel = Annotated["GroupTypeGQLModel", strawberry.lazy(".groupTypeGQLModel")]
GroupTypeInputWhereFilter = Annotated["GroupTypeInputWhereFilter", strawberry.lazy(".groupTypeGQLModel")]


@createInputs
@dataclass
class GroupCategoryInputWhereFilter:
    id: IDType
    name: str

@strawberry.federation.type(
    keys=["id"], description="""Entity representing a group category (like Academic structures)"""
)
class GroupCategoryGQLModel(NamedGQLModel):
    @classmethod
    def getLoader(cls, info):
        return getLoadersFromInfo(info).GroupCategoryModel

    types: typing.List[GroupTypeGQLModel] = strawberry.field(
        description="",
        permission_classes=[
            OnlyForAuthentized
        ],
        # graphql_type=typing.List[GroupTypeGQLModel],
        resolver=VectorResolver[GroupTypeGQLModel](fkey_field_name="category_id", whereType=GroupTypeInputWhereFilter)
    )

#####################################################################
#
# Special fields for query
#
#####################################################################


# @strawberry.field(
#     description="""Returns a list of groups types (paged)""",
#     permission_classes=[OnlyForAuthentized])
# async def group_type_page(
#     self, info: strawberry.types.Info, skip: int = 0, limit: int = 20,
#     where: Optional[GroupCategoryInputWhereFilter] = None
# ) -> List[GroupCategoryGQLModel]:
#     wheredict = None if where is None else strawberry.asdict(where)
#     loader = getLoader(info).groupcategorys
#     result = await loader.page(skip, limit, where=wheredict)
#     return result

# from ._GraphResolvers import asPage

# @strawberry.field(
#     description="""Returns a list of groups categories (paged)""",
#     permission_classes=[OnlyForAuthentized])
# @asPage
# async def group_category_page(
#     self, info: strawberry.types.Info, skip: int = 0, limit: int = 20,
#     where: Optional[GroupCategoryInputWhereFilter] = None
# ) -> List[GroupCategoryGQLModel]:
#     loader = GroupCategoryGQLModel.getLoader(info)
#     return loader


# group_category_page = strawberry.field(
#     description="""Returns a list of groups categories (paged)""",
#     permission_classes=[
#         OnlyForAuthentized
#     ],
#     resolver=DBResolvers.GroupCategoryModel.resolve_page(GroupCategoryGQLModel, GroupCategoryInputWhereFilter)
# )

# @strawberry.field(
#         description="Returns a list of groups categories (paged)",
#         permission_classes=[
#             OnlyForAuthentized
#         ],
#     )
# async def group_category_page(
#         self, 
#         info: strawberry.Info,
#         # after: Optional[str]=0, 
#         skip: Annotated[Optional[str], strawberry.argument(description="")]=0, 
#         limit: Optional[int]=10, 
#         orderby: Optional[str] = "id", 
#         where: Optional[GroupCategoryInputWhereFilter] = None
#     ) -> typing.List[GroupCategoryGQLModel]:
#     executor = GroupCategoryList()
#     return await executor(info=info, skip=skip, limit=limit, orderby=orderby, where=where)

group_category_page = strawberry.field(
    description="Returns a list of groups categories (paged)",
    permission_classes=[
        OnlyForAuthentized
    ],
    graphql_type=typing.List[GroupCategoryGQLModel],
    resolver=PageResolver[GroupCategoryGQLModel](whereType=GroupCategoryInputWhereFilter)
)

group_category_by_id = strawberry.field(
    description="""Finds a group category by its id""",
    permission_classes=[
        OnlyForAuthentized
    ],
    graphql_type=typing.Optional[GroupCategoryGQLModel],
    resolver=GroupCategoryGQLModel.load_with_loader
    )

#####################################################################
#
# Mutation section
#
#####################################################################
import datetime

@strawberry.input(description="")
class GroupCategoryUpdateGQLModel:
    id: IDType
    lastchange: datetime.datetime
    name: Optional[str] = None
    name_en: Optional[str] = None
    changedby_id: strawberry.Private[IDType] = None

@strawberry.input(description="")
class GroupCategoryInsertGQLModel:
    id: Optional[IDType] = None
    name: Optional[str] = None
    name_en: Optional[str] = None
    createdby_id: strawberry.Private[IDType] = None

@strawberry.input(description="")
class GroupCategoryDeleteGQLModel:
    id: IDType
    lastchange: datetime.datetime
   
@strawberry.mutation(
    description="""Allows an update of group category""",
    permission_classes=[
        OnlyForAuthentized,
        SimpleUpdatePermission[GroupCategoryGQLModel](roles=["administrátor"])
    ])
async def group_category_update(self, info: strawberry.types.Info, group_category: GroupCategoryUpdateGQLModel) -> typing.Union[GroupCategoryGQLModel, UpdateError[GroupCategoryGQLModel]]:
    return await Update[GroupCategoryGQLModel].DoItSafeWay(info=info, entity=group_category)

@strawberry.mutation(
    description="""Inserts a group category""",
    permission_classes=[
        OnlyForAuthentized,
        SimpleInsertPermission[GroupCategoryGQLModel](roles=["administrátor"])
    ])
async def group_category_insert(self, info: strawberry.types.Info, group_category: GroupCategoryInsertGQLModel) -> typing.Union[GroupCategoryGQLModel, InsertError[GroupCategoryGQLModel]]:
    return await Insert[GroupCategoryGQLModel].DoItSafeWay(info=info, entity=group_category)

@strawberry.mutation(
    description="Deletes the group category",
    permission_classes=[
        OnlyForAuthentized,
        SimpleDeletePermission[GroupCategoryGQLModel](roles=["administrátor"])
    ])
async def group_category_delete(self, info: strawberry.types.Info, group_category: GroupCategoryDeleteGQLModel) -> typing.Optional[DeleteError[GroupCategoryGQLModel]]:
    return await Delete[GroupCategoryGQLModel].DoItSafeWay(info=info, entity=group_category)
