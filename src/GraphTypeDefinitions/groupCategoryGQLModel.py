import datetime
import strawberry
import uuid
from typing import List, Optional, Union, Annotated
import typing
import strawberry.types
from uoishelpers.resolvers import createInputs

from .BaseGQLModel import BaseGQLModel, IDType
from ._GraphPermissions import (
    RoleBasedPermission, 
    OnlyForAuthentized,
    RBACPermission,
    OnlyForAdmins
)
from ._GraphResolvers import (
    encapsulateInsert,
    encapsulateUpdate,
    encapsulateDelete,

    remove_constructor,

    default_scalar_resolver,
    default_vector_resolver,
    default_page_resolver
)

from src.Dataloaders import (
    getLoadersFromInfo as getLoader,
    getUserFromInfo)
from src.DBResolvers import DBResolvers

GroupTypeGQLModel = Annotated["GroupTypeGQLModel", strawberry.lazy(".groupTypeGQLModel")]
GroupTypeInputWhereFilter = Annotated["GroupTypeInputWhereFilter", strawberry.lazy(".groupTypeGQLModel")]
RBACObjectGQLModel = Annotated["RBACObjectGQLModel", strawberry.lazy(".RBACObjectGQLModel")]

from .utils import createInputs
from dataclasses import dataclass

@createInputs
@dataclass
class GroupCategoryInputWhereFilter:
    id: IDType
    name: str

@remove_constructor
@strawberry.federation.type(
    keys=["id"], description="""Entity representing a group category (like Academic structures)"""
)
class GroupCategoryGQLModel(BaseGQLModel):
    @classmethod
    def getLoader(cls, info):
        return getLoader(info).GroupCategoryModel

    from ._GraphResolvers import (
        resolve_name as name,
        resolve_name_en as name_en,
        resolve_rbacobject as rbacobject
    )

    types = strawberry.field(
        description="",
        permission_classes=[
            OnlyForAuthentized
        ],
        graphql_type=typing.List[GroupTypeGQLModel],
        resolver=default_vector_resolver(fkey_field_name="category_id", whereType=GroupTypeInputWhereFilter)
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
    resolver=default_page_resolver(whereType=GroupCategoryInputWhereFilter)
)

@strawberry.field(
    description="""Finds a group category by its id""",
    permission_classes=[
        OnlyForAuthentized
    ])
async def group_category_by_id(self, info: strawberry.types.Info, id: IDType) -> typing.Optional[GroupCategoryGQLModel]:
    return await GroupCategoryGQLModel.resolve_reference(info=info, id=id)

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
    changedby: strawberry.Private[IDType] = None

@strawberry.input(description="")
class GroupCategoryInsertGQLModel:
    id: Optional[IDType] = None
    name: Optional[str] = None
    name_en: Optional[str] = None
    createdby: strawberry.Private[IDType] = None

@strawberry.type(description="")
class GroupCategoryResultGQLModel:
    id: IDType = None
    msg: str = None

    @strawberry.field(description="""Result of groupcategory operation""")
    async def category(self, info: strawberry.types.Info) -> Union[GroupCategoryGQLModel, None]:
        result = await GroupCategoryGQLModel.resolve_reference(info, self.id)
        return result
    
@strawberry.mutation(
    description="""Allows an update of group category""",
    permission_classes=[
        OnlyForAuthentized,
        OnlyForAdmins
    ])
async def group_category_update(self, info: strawberry.types.Info, group_category: GroupCategoryUpdateGQLModel) -> GroupCategoryResultGQLModel:
    return await encapsulateUpdate(info, GroupCategoryGQLModel.getLoader(info), group_category, GroupCategoryResultGQLModel(id=group_category.id, msg="ok"))

@strawberry.mutation(
    description="""Inserts a group category""",
    permission_classes=[
        OnlyForAuthentized,
        OnlyForAdmins
    ])
async def group_category_insert(self, info: strawberry.types.Info, group_category: GroupCategoryInsertGQLModel) -> GroupCategoryResultGQLModel:
    return await encapsulateInsert(info, GroupCategoryGQLModel.getLoader(info), group_category, GroupCategoryResultGQLModel(id=None, msg="ok"))

@strawberry.mutation(
    description="Deletes the group category",
    permission_classes=[
        OnlyForAuthentized,
        OnlyForAdmins
    ])
async def group_category_delete(self, info: strawberry.types.Info, id: IDType) -> GroupCategoryResultGQLModel:
    return await encapsulateDelete(info, GroupCategoryGQLModel.getLoader(info), id, GroupCategoryResultGQLModel(msg="ok", id=None))


from .BaseGQLModel import Connection, List as BaseList
class GroupCategoryConnection(Connection[GroupCategoryGQLModel]):
    pass

