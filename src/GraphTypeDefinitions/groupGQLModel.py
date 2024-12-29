import datetime
import dataclasses
import strawberry
import uuid
import logging
import asyncio
import typing

from typing import List, Optional, Union, Annotated, Type

import strawberry.types
from .BaseGQLModel import BaseGQLModel, IDType
from .NamedGQLModel import NamedGQLModel
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

from ._GraphPermissions import (
    RBACPermission,
    RoleBasedPermission, 
    OnlyForAuthentized,
    OnlyForAdmins,
    # InsertRBACPermission,
    # AlwaysFailPermission
    )

from src.Dataloaders import (
    getLoadersFromInfo as getLoader,
    getUserFromInfo)
from src.DBResolvers import DBResolvers

GroupTypeGQLModel = Annotated["GroupTypeGQLModel", strawberry.lazy(".groupTypeGQLModel")]
MembershipGQLModel = Annotated["MembershipGQLModel", strawberry.lazy(".membershipGQLModel")]
MembershipInputWhereFilter = Annotated["MembershipInputWhereFilter", strawberry.lazy(".membershipGQLModel")]
RoleGQLModel = Annotated["RoleGQLModel", strawberry.lazy(".roleGQLModel")]
RoleInputWhereFilter = Annotated["RoleInputWhereFilter", strawberry.lazy(".roleGQLModel")]
GroupTypeInputWhereFilter = Annotated["GroupTypeInputWhereFilter", strawberry.lazy(".groupTypeGQLModel")]


from uoishelpers.resolvers import createInputs
from dataclasses import dataclass
# MembershipInputWhereFilter = Annotated["MembershipInputWhereFilter", strawberry.lazy(".membershipGQLModel")]
@createInputs
@dataclass
class GroupInputWhereFilter:
    id: IDType
    name: str
    name_en: str
    valid: bool
    startdate: datetime.datetime
    enddate: datetime.datetime
    grouptype: GroupTypeInputWhereFilter
    roles: RoleInputWhereFilter
    mastergroup_id: IDType

GroupGQLModel_description = """
## Description

Group is entity with members. 
It can have also mastergroup.
Mastergroup can be only one.
Groups are organized in tree structures.
There also can be defined roles on the group.
"""

@strawberry.federation.type(keys=["id"], description="""Entity representing a group""")
class GroupGQLModel(NamedGQLModel):
    @classmethod
    def getLoader(cls, info):
        return getLoader(info).GroupModel

    @classmethod
    def from_dataclass(cls, db_row):
        db_row_dict = dataclasses.asdict(db_row)
        db_row_dict["valid"] = db_row.valid
        instance = cls(**db_row_dict)
        return instance

    email: typing.Optional[str] = strawberry.field(
        description="""Group's email""",
        permission_classes=[OnlyForAuthentized]
        )
    
    abbreviation: typing.Optional[str] = strawberry.field(
        description="""Group's name abbreviation""",
        permission_classes=[OnlyForAuthentized]
        )
    
    valid: typing.Optional[bool] = strawberry.field(
        description="""Group's validity (still exists?)""",
        permission_classes=[
            OnlyForAuthentized
        ]
        )
    # @strawberry.field(
    #     description="""Group's validity (still exists?)""",
    #     permission_classes=[
    #         OnlyForAuthentized
    #     ]
    # )
    # async def valid(self) -> typing.Optional[bool]:
    #     return self.valid

    startdate: typing.Optional[datetime.datetime] = strawberry.field(
        description="",
        permission_classes=[
            OnlyForAuthentized
        ]
    )

    enddate: typing.Optional[datetime.datetime] = strawberry.field(
        description="",
        permission_classes=[
            OnlyForAuthentized
        ]
    )

    grouptype_id: typing.Optional[IDType] = strawberry.field(
        description="""Group's type id (like Department)""",
        permission_classes=[
            OnlyForAuthentized
        ],
    )

    grouptype: typing.Optional["GroupTypeGQLModel"] = strawberry.field(
        description="""Group's type (like Department)""",
        permission_classes=[
            OnlyForAuthentized
        ],
        # graphql_type=GroupTypeGQLModel,
        # resolver=default_scalar_resolver(fkey_field_name="type_id", gql_type=Type[GroupTypeGQLModel]) #DBResolvers.GroupModel.grouptype(GroupTypeGQLModel)
        resolver=ScalarResolver[GroupTypeGQLModel](fkey_field_name="type_id") #DBResolvers.GroupModel.grouptype(GroupTypeGQLModel)
    )

    type: typing.Optional[GroupTypeGQLModel] = strawberry.field(
        description="""Group's type (like Department)""",
        permission_classes=[
            OnlyForAuthentized
        ],
        graphql_type=Optional[GroupTypeGQLModel],
        # resolver=default_scalar_resolver(fkey_field_name="type_id", gql_type=Type[GroupTypeGQLModel]) #DBResolvers.GroupModel.grouptype(GroupTypeGQLModel)
        resolver=ScalarResolver[GroupTypeGQLModel](fkey_field_name="grouptype_id") #DBResolvers.GroupModel.grouptype(GroupTypeGQLModel)
    )

    grouptype_id: typing.Optional[IDType] = strawberry.field(
        description="""Group's type id""",
        permission_classes=[
            OnlyForAuthentized
        ],
        graphql_type=Optional[IDType],
        # resolver=default_resolver
    )

    # @strawberry.field(
    #     description="""Directly commanded groups""",
    #     permission_classes=[
    #         OnlyForAuthentized
    #     ])
    # async def subgroups(
    #     self, info: strawberry.types.Info,
    #     where: Optional["GroupInputWhereFilter"] = None, 
    #     skip: Optional[int] = 0, limit: Optional[int] = 100
    # ) -> List["GroupGQLModel"]:
    #     wheredict = None if where is None else strawberry.asdict(where)
    #     extendedfilter = {"mastergroup_id": self.id}
    #     loader = GroupGQLModel.getLoader(info)
    #     return await loader.page(skip=skip, limit=limit, orderby="name", where=wheredict, extendedfilter=extendedfilter)

    subgroups: typing.List["GroupGQLModel"] = strawberry.field(
        description="""Directly commanded groups""",
        permission_classes=[
            OnlyForAuthentized
        ],
        # graphql_type=List["GroupGQLModel"],
        resolver=VectorResolver["GroupGQLModel"](fkey_field_name="mastergroup_id", whereType=GroupInputWhereFilter)
    )
    

    # @strawberry.field(
    #     description="""Directly commanded groups""",
    #     permission_classes=[
    #         OnlyForAuthentized
    #     ])
    # async def _subgroups(
    #     self, info: strawberry.types.Info,
    #     where: Optional["GroupInputWhereFilter"] = None, 
    #     after: Optional[str] = 0, 
    #     first: Optional[int] = 100,
    #     orderby: Optional[str] = "id"
    # ) -> Connection["GroupGQLModel"]:
    #     extendedfilter = {"mastergroup_id": self.id()}
    #     print(f"extendedfilter {extendedfilter}")
    #     items = GroupConnection(skip=after, limit=first, where=where, orderby=orderby, extendedfilter=extendedfilter)
    #     # results = [GroupGQLModel(item) for item in items]
    #     return items

    # @strawberry.field(
    #     description="""Commanding group""",
    #     permission_classes=[
    #         OnlyForAuthentized
    #     ])
    # async def mastergroup(
    #     self, info: strawberry.types.Info
    # ) -> Optional["GroupGQLModel"]:
    #     result = await GroupGQLModel.resolve_reference(info, id=self.mastergroup_id)
    #     return result

    mastergroup_id: typing.Optional[IDType] = strawberry.field(
        description="""master id""",
        permission_classes=[
            OnlyForAuthentized
        ],
    )

    mastergroup: typing.Optional["GroupGQLModel"] = strawberry.field(
        description="""Commanding group""",
        permission_classes=[
            OnlyForAuthentized
        ],
        # graphql_type=Optional["GroupGQLModel"],
        # resolver=default_scalar_resolver(fkey_field_name="mastergroup_id", gql_type=Type["GroupGQLModel"])
        resolver=ScalarResolver["GroupGQLModel"](fkey_field_name="mastergroup_id")
    )

    @strawberry.field(
        description="""Commanding groups ordered from highest to lowest""",
        permission_classes=[
            OnlyForAuthentized
        ]
        )
    async def mastergroups(self, info: strawberry.types.Info) -> typing.List["GroupGQLModel"]:
        path = self.path 
        ids = [] if path is None else path.split('/')[:-1]
        print(f"path {path}", flush=True)
        print(f"ids {ids}", flush=True)
        futures = [GroupGQLModel.load_with_loader(info=info, id=id) for id in ids]
        result = await asyncio.gather(*futures)
        return result


    path: typing.Optional[str] = strawberry.field(
        description="""""",
        permission_classes=[
            OnlyForAuthentized
        ]
        )


    # @strawberry.field(
    #     description="""List of users who are member of the group""",
    #     permission_classes=[
    #         OnlyForAuthentized
    #     ])
    # async def memberships(
    #     self, info: strawberry.types.Info, where: Optional[MembershipInputWhereFilter] = None, skip: Optional[int] = 0, limit: Optional[int] = 1000
    # ) -> List["MembershipGQLModel"]:
    #     from .membershipGQLModel import MembershipGQLModel
    #     # result = await resolveMembershipForGroup(session,  self.id, skip, limit)
    #     # async with withInfo(info) as session:
    #     #     result = await resolveMembershipForGroup(session, self.id, skip, limit)
    #     #     return result
    #     wheredict = None if where is None else strawberry.asdict(where)
    #     extendedfilter = {"group_id": self.id}
    #     loader = MembershipGQLModel.getLoader(info)
    #     #print(self.id)
    #     result = await loader.page(skip=skip, limit=limit, where=wheredict, extendedfilter=extendedfilter)
    #     return result

    memberships: typing.List[MembershipGQLModel] = strawberry.field(
        description="""List of users who are member of the group""",
        permission_classes=[
            OnlyForAuthentized
        ],
        # graphql_type=List[MembershipGQLModel],
        # resolver=DBResolvers.GroupModel.memberships(MembershipGQLModel, WhereFilterModel=MembershipInputWhereFilter)
        resolver=VectorResolver[MembershipGQLModel](fkey_field_name="group_id", whereType=MembershipInputWhereFilter)
    )
    
    # @strawberry.field(description="Relay definition of memberships")
    # async def _memberships(
    #         self, 
    #         # after: Optional[str]=0, 
    #         after: Annotated[Optional[str], strawberry.argument(description="")]="0", 
    #         first: Optional[int]=10, 
    #         orderby: Optional[str] = "id", 
    #         where: Optional[GroupInputWhereFilter] = None
    #     ) -> Connection[MembershipGQLModel]:
    #     from .membershipGQLModel import MembershipConnection
    #     group_id = self.id if self._data is None else self._data.id
    #     extendedfilter = {"group_id": group_id}
    #     return MembershipConnection(skip=after, limit=first, where=where, orderby=orderby, extendedfilter=extendedfilter)   
     
    roles: typing.List[RoleGQLModel] = strawberry.field(
        description="""List of roles in the group""",
        permission_classes=[
            OnlyForAuthentized
        ],
        # graphql_type=List[RoleGQLModel],
        # resolver=DBResolvers.GroupModel.roles(RoleGQLModel, WhereFilterModel=RoleInputWhereFilter)
        resolver=VectorResolver[RoleGQLModel](fkey_field_name="group_id", whereType=RoleInputWhereFilter)
    )

    @strawberry.field(description="")
    async def roles_on(self, info: strawberry.types.Info) -> typing.List[RoleGQLModel]:
        from .roleGQLModel import RoleGQLModel
        loader = RoleGQLModel.getLoader(info=info)
        path = self.path # works as materialized path ;)
        ids = [] if path is None else path.split('/')
        futures = (loader.filter_by(group_id=IDType(id)) for id in ids)
        dbrows = await asyncio.gather(*futures)
        result = [RoleGQLModel.from_dataclass(row) for row in dbrows if row.valid]
        return result

#####################################################################
#
# Special fields for query
#
#####################################################################

# @createInputs
# @dataclass
# class GroupInputWhereFilter:
#     name: str
#     name_en: str
#     valid: bool
#     startdate: datetime.datetime
#     enddate: datetime.datetime
#     grouptype: GroupTypeInputWhereFilter
#     roles: RoleInputWhereFilter

# @strawberry.field(
#     description="""Returns a list of groups (paged)""",
#     permission_classes=[
#         OnlyForAuthentized
#     ])
# @asPage
# async def group_page(
#     self, info: strawberry.types.Info, skip: int = 0, limit: int = 10,
#     where: Optional[GroupInputWhereFilter] = None,
#     orderby: Optional[str] = None,
#     desc: Optional[bool] = None
# ) -> List[GroupGQLModel]:
#     return GroupGQLModel.getLoader(info)

group_page: typing.List[GroupGQLModel] = strawberry.field(
    description="""Returns a list of groups (paged)""",
    permission_classes=[
        OnlyForAuthentized
    ],
    graphql_type=List[GroupGQLModel],
    resolver=PageResolver[GroupGQLModel](whereType=GroupInputWhereFilter)
    # resolver=DBResolvers.GroupModel.resolve_page(GroupGQLModel, WhereFilterModel=GroupInputWhereFilter)
)

# @strawberry.field(description="")
# async def group_page(self, info: strawberry.types.Info,
#     skip: Optional[int] = 0, limit: Optional[int] = 10,
#     where: Optional[GroupInputWhereFilter] = None,
#     orderby: Optional[str] = None,
#     desc: Optional[bool] = None
# ) -> List[GroupGQLModel]:
#     wheredict = None if where is None else strawberry.asdict(where)
#     loader = GroupGQLModel.getLoader(info)
#     items = await loader.page(where=wheredict, skip=skip, limit=limit, orderby=orderby, desc=desc)
#     results = [GroupGQLModel(item) for item in items]
#     return results
    # ids = (item.id for item in items)
    # awaitables = (GroupGQLModel.resolve_reference(info=info, id=id) for id in ids)
    # return await asyncio.gather(*awaitables)
    # return items

# @strawberry.field(
#     description="""Finds a group by its id""",
#     permission_classes=[
#         OnlyForAuthentized
#     ])
# async def group_by_id(
#     self, info: strawberry.types.Info, id: IDType
# ) -> Union[GroupGQLModel, None]:
#     result = await GroupGQLModel.resolve_reference(info=info, id=id)
#     return result


group_by_id: typing.Optional[GroupGQLModel] = strawberry.field(
    description="""Finds a group by its id""",
    permission_classes=[
        OnlyForAuthentized
    ],
    graphql_type=Optional[GroupGQLModel],
    resolver=GroupGQLModel.load_with_loader
    # resolver=DBResolvers.GroupModel.resolve_by_id(GroupGQLModel)
)

# @strawberry.field(
#     description="""Finds an user by letters in name and surname, letters should be atleast three""",
#     deprecation_reason='replaced by `query($letters: String!){groupPage(where: {name: {_like: $letters}}) { id name }}`',
#     permission_classes=[
#         OnlyForAuthentized
#     ]
# )
# async def group_by_letters(
#     self,
#     info: strawberry.types.Info,
#     validity: Union[bool, None] = None,
#     letters: str = "",
# ) -> List[GroupGQLModel]:
#     # result = await resolveGroupsByThreeLetters(session,  validity, letters)
#     loader = GroupGQLModel.getLoader(info)

#     if len(letters) < 3:
#         return []
#     stmt = loader.getSelectStatement()
#     model = loader.getModel()
#     stmt = stmt.where(model.name.like(f"%{letters}%"))
#     if validity is not None:
#         stmt = stmt.filter_by(valid=True)

#     result = await loader.execute_select(stmt)
#     return result

# @strawberry.field(description="""Random university""")
# async def randomUniversity(
#     self, name: str, info: strawberry.types.Info
# ) -> GroupGQLModel:
#     async with withInfo(info) as session:
#         # newId = await randomDataStructure(session,  name)
#         newId = await randomDataStructure(session, name)
#         print("random university id", newId)
#         # result = await resolveGroupById(session,  newId)
#         result = await resolveGroupById(session, newId)
#         print("db response", result.name)
#         return result

#####################################################################
#
# Mutation section
#
#####################################################################
import datetime

@strawberry.input(description="")
class GroupUpdateGQLModel:
    id: IDType
    lastchange: datetime.datetime
    name: Optional[str] = None
    name_en: Optional[str] = None
    grouptype_id: Optional[IDType] = None
    mastergroup_id: Optional[IDType] = None
    valid: Optional[bool] = None
    abbreviation: Optional[str] = None
    email: Optional[str] = None
    changedby_id: strawberry.Private[IDType] = None


@strawberry.input(description="")
class GroupInsertGQLModel:
    name: str
    grouptype_id: IDType
    id: Optional[IDType] = strawberry.field(description="primary key", default_factory=uuid.uuid4)
    name_en: Optional[str] = None
    mastergroup_id: Optional[IDType] = None
    valid: Optional[bool] = None
    abbreviation: Optional[str] = None
    email: Optional[str] = None
    path: strawberry.Private[str] = None
    createdby_id: strawberry.Private[IDType] = None
    rbacobject: strawberry.Private[IDType] = None

@strawberry.input(description="")
class GroupDeleteGQLModel:
    id: IDType
    lastchange: datetime.datetime

# @strawberry.type(description="represents the result of CUD op on GroupGQLModel")
# class GroupResultGQLModel:
#     id: IDType = None
#     msg: str = None

#     @strawberry.field(description="""Result of group operation""")
#     async def group(self, info: strawberry.types.Info) -> Union[GroupGQLModel, None]:
#         # print("GroupResultGQLModel", "group", self.id, flush=True)
#         result = await GroupGQLModel.resolve_reference(info, self.id)
#         # print("GroupResultGQLModel", result.id, result.name, flush=True)
#         return result


class UpdateGroupPermission(RBACPermission):
    message = "User is not allowed to create a new group"
    async def has_permission(self, source, info: strawberry.types.Info, group: GroupInsertGQLModel) -> bool:
        adminRoleNames = ["administrátor"]
        allowedRoleNames = ["garant"]
        role = await self.resolveUserRole(info, 
            rbacobject=group.id, 
            adminRoleNames=adminRoleNames, 
            allowedRoleNames=allowedRoleNames)
        
        if not role: return False
        roleTypeName = role["type"]["name"]
        if roleTypeName in allowedRoleNames:
            if group.mastergroup_id:
                raise self.error_class(f"{roleTypeName} cannot change mastergroup_id")
            if group.grouptype_id:
                raise self.error_class(f"{roleTypeName} cannot change grouptype_id")
        return True

@strawberry.mutation(
    description="""Allows a update of group, also it allows to change the mastergroup of the group""",
    permission_classes=[
        OnlyForAuthentized,
        UpdateGroupPermission
    ])
async def group_update(self, info: strawberry.types.Info, group: GroupUpdateGQLModel) -> Union[GroupGQLModel, UpdateError[GroupGQLModel]]:
    result = await Update[GroupGQLModel].DoItSafeWay(info=info, entity=group)
    return result

class InsertGroupPermission(RBACPermission):
    message = "User is not allowed to create a new group"
    async def has_permission(self, source, info: strawberry.types.Info, group: GroupInsertGQLModel) -> bool:
        adminRoleNames = ["administrátor"]
        allowedRolesNames = ["garant"]
        result = await self.resolveUserRole(info, 
            rbacobject=group.mastergroup_id, 
            adminRoleNames=adminRoleNames, 
            allowedRoleNames=allowedRolesNames)
        if result is None:
            user = getUserFromInfo(info)
            logging.info(f"user {user} has no right to insert new group {group}")
            print(f"user {user} has no right to insert new group {group}")
        # else:
        #     user = getUserFromInfo(info)
        #     print(f"user {user} has full right to insert new group {group}")
        #     pass
        return result

@strawberry.mutation(
    description="""Allows to insert a group""",
    permission_classes=[
        OnlyForAuthentized,
        InsertGroupPermission
    ])
async def group_insert(self, info: strawberry.types.Info, group: GroupInsertGQLModel) -> Union[GroupGQLModel, InsertError[GroupGQLModel]]:
    group.rbacobject = group.id
    if group.mastergroup_id is not None:
        loader = GroupGQLModel.getLoader(info=info)
        master = await loader.load(group.mastergroup_id)
    group.path = f"{group.id}" if group.mastergroup_id is None else f"{master.path}/{group.id}"
    result = await Insert[GroupGQLModel].DoItSafeWay(info=info, entity=group)
    return result


@strawberry.mutation(
    description="Deletes the group",
    permission_classes=[
        OnlyForAuthentized,
        OnlyForAdmins
    ])
async def group_delete(self, info: strawberry.types.Info, group: GroupDeleteGQLModel) -> Optional[DeleteError[GroupGQLModel]]:
    result = await Delete[GroupGQLModel].DoItSafeWay(info=info, entity=group)
    return result

