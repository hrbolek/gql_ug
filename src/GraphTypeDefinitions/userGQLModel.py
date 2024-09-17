import datetime
import strawberry
import asyncio
import uuid
import typing
import dataclasses

from typing import List, Optional, Union, Annotated
import typing

import strawberry.types
from uoishelpers.resolvers import createInputs

from .BaseGQLModel import BaseGQLModel, IDType
from ._GraphPermissions import (
    RoleBasedPermission, 
    OnlyForAuthentized,
    OnlyForAdmins,
    RBACPermission
)
from ._GraphResolvers import (
    default_resolver,
    default_vector_resolver,
    default_by_id_resolver,
    default_page_resolver,
    resolve_field,
    

    encapsulateInsert,
    encapsulateUpdate,
    encapsulateDelete,

    remove_constructor

)

from src.Dataloaders import (
    getLoadersFromInfo as getLoader,
    getUserFromInfo)
from src.DBResolvers import DBResolvers


MembershipGQLModel = Annotated["MembershipGQLModel", strawberry.lazy(".membershipGQLModel")]
RoleGQLModel = Annotated["RoleGQLModel", strawberry.lazy(".roleGQLModel")]
GroupGQLModel = Annotated["GroupGQLModel", strawberry.lazy(".groupGQLModel")]

RoleInputWhereFilter = Annotated["RoleInputWhereFilter", strawberry.lazy(".roleGQLModel")]
MembershipInputWhereFilter = Annotated["MembershipInputWhereFilter", strawberry.lazy(".membershipGQLModel")]



@remove_constructor
@strawberry.federation.type(keys=["id"], description="""Entity representing a user""")
class UserGQLModel(BaseGQLModel):
    @classmethod
    def getLoader(cls, info):
        return getLoader(info).UserModel
    
    # id = strawberry.field(
    #     description="""Unique identifier""",
    #     permission_classes=[
    #         OnlyForAuthentized
    #     ],
    #     graphql_type=IDType,
    #     resolver=default_resolver
    # )  

    # lastchange = strawberry.field(
    #     description="""Timestamp""",
    #     permission_classes=[
    #         OnlyForAuthentized
    #     ],
    #     graphql_type=datetime.datetime,
    #     resolver=default_resolver
    # )  

    # created = strawberry.field(
    #     description="""Timestamp""",
    #     permission_classes=[
    #         OnlyForAuthentized
    #     ],
    #     graphql_type=datetime.datetime,
    #     resolver=default_resolver
    # )  

    # changedby = resolve_changedby
    # created = resolve_created
    # lastchange = resolve_lastchange
    # createdby = resolve_createdby
    
    from ._GraphResolvers import (
        resolve_name as name,
        resolve_rbacobject as rbacobject,
    )
    # name = strawberry.field(
    #     description="""User's name (like John)""",
    #     permission_classes=[
    #         OnlyForAuthentized
    #     ],
    #     graphql_type=str,
    #     resolver=default_resolver
    # )  

    firstname = strawberry.field(
        description="""User's name (like John)""",
        permission_classes=[
            OnlyForAuthentized
        ],
        graphql_type=Optional[str],
        resolver=default_resolver
    )  

    surname = strawberry.field(
        description="""User's family name (like Obama)""",
        permission_classes=[
            OnlyForAuthentized
        ],
        graphql_type=Optional[str],
        resolver=default_resolver
    )  

    fullname = strawberry.field(
        description="""User's full name""",
        permission_classes=[
            OnlyForAuthentized
        ],
        graphql_type=Optional[str],
        resolver=default_resolver
    )  

    email = strawberry.field(
        description="""User's email""",
        permission_classes=[
            OnlyForAuthentized
        ],
        graphql_type=Optional[str],
        resolver=default_resolver
    )

    valid = strawberry.field(
        description="""If the user is still valid""",
        permission_classes=[
            OnlyForAuthentized
        ],
        resolver=default_resolver
    )


    @strawberry.field(
        description="""if this record is related to logged user""",
        permission_classes=[
            OnlyForAuthentized
        ])
    async def is_this_me(self, info: strawberry.types.Info) -> bool:
        user = getUserFromInfo(info)
        selfid = self.id if self._data is None else self._data.id
        # print(f"me: {user}")
        if user is None: return None
        user_id = user.get("id", None)
        # print(f"is_this_me {type(user_id)}, {type(self.id)}", flush=True)
        # print(f"is_this_me {user_id==self.id}", flush=True)
        # return f"{self.id}" == f"{user_id}"
        return user_id==selfid
        

    @strawberry.field(
        description="""active roles to this user""",
        permission_classes=[
            OnlyForAuthentized
        ])
    async def roles_on(self, info: strawberry.types.Info) -> typing.List["RoleGQLModel"]:
        from .roleGQLModel import resolve_roles_on_user, RoleGQLModel
        user = getUserFromInfo(info)
        user_id = user.get("id", None)
        result = await resolve_roles_on_user(self, info=info, user_id=user_id)
        result = (RoleGQLModel(r) for r in result)
        return result
        
    @strawberry.field(
        description="""gdpr check""",
        permission_classes=[
            OnlyForAuthentized,
            RoleBasedPermission("zpracovatel gdpr")
        ])
    def gdpr(self, info: strawberry.types.Info, force: typing.Optional[bool] = False) -> typing.Optional[str]:
        return "gdpr information" if force else None

    # fullname = strawberry.field(
    #     description="""User's name (like John Newbie)""",
    #     permission_classes=[
    #         OnlyForAuthentized
    #     ],
    #     resolver=DBResolvers.UserModel.fullname
    # )  

    

    memberships = strawberry.field(
        description="""List of mmeberships associated with the user""",
        permission_classes=[
            OnlyForAuthentized
        ],
        graphql_type=typing.List[MembershipGQLModel],
        # resolver=DBResolvers.UserModel.memberships(MembershipGQLModel, WhereFilterModel=MembershipInputWhereFilter)
        resolver=default_vector_resolver(fkey_field_name="user_id", whereType=MembershipInputWhereFilter)
    )

    # @strawberry.field(description="")
    # async def _memberships(self, ins) -> MembershipConnection:
    #     pass

    membership = strawberry.field(
        description="""List of mmeberships associated with the user""",
        deprecation_reason="use memberships",
        permission_classes=[
            OnlyForAuthentized
        ],
        graphql_type=typing.List[MembershipGQLModel],
        # resolver=DBResolvers.UserModel.memberships(MembershipGQLModel, WhereFilterModel=MembershipInputWhereFilter)
        resolver=default_vector_resolver(fkey_field_name="user_id", whereType=MembershipInputWhereFilter)

    )

    roles = strawberry.field(
        description="""User's roles (like Dean)""",
        permission_classes=[
            OnlyForAuthentized
        ],
        graphql_type=List[RoleGQLModel],
        # resolver=DBResolvers.UserModel.roles(RoleGQLModel, WhereFilterModel=RoleInputWhereFilter)
        resolver=default_page_resolver(whereType=RoleInputWhereFilter)
    )



    # @strawberry.field(
    #     description="""GDPRInfo for permision test""", 
    #     permission_classes=[OnlyForAuthentized, UserGDPRPermission])
    # def GDPRInfo(self, info: strawberry.types.Info) -> Union[str, None]:
    #     actinguser = getUser(info)
    #     print(actinguser)
    #     return "GDPRInfo"


    @strawberry.field(
        description="""List of groups given type, where the user is member""",
        permission_classes=[OnlyForAuthentized])
    async def member_of(
        self, info: strawberry.types.Info, grouptype_id: Optional[IDType] = None, 
    ) -> typing.List["GroupGQLModel"]:
        from .groupGQLModel import GroupGQLModel
        from .membershipGQLModel import MembershipGQLModel
        loader = MembershipGQLModel.getLoader(info)
        selfid = resolve_field(self=self, field_name="id")
        rows = await loader.filter_by(user_id=selfid)# , grouptype_id=grouptype_id)
        results = (GroupGQLModel.resolve_reference(info, row.group_id) for row in rows)
        results = await asyncio.gather(*results)
        if grouptype_id:
            results = filter(lambda item: item.grouptype_id == grouptype_id, results)
        return results
    
    # RBACObjectGQLModel = Annotated["RBACObjectGQLModel", strawberry.lazy(".RBACObjectGQLModel")]
    # @strawberry.field(
    #     description="""Who made last change""",
    #     permission_classes=[OnlyForAuthentized])
    # async def rbacobject(self, info: strawberry.types.Info) -> Optional[RBACObjectGQLModel]:
    #     from .RBACObjectGQLModel import RBACObjectGQLModel
    #     result = None if self.id is None else await RBACObjectGQLModel.resolve_reference(info, self.id)
    #     return result    

#####################################################################
#
# Special fields for query
#
#####################################################################

from .utils import createInputs
from dataclasses import dataclass
#MembershipInputWhereFilter = Annotated["MembershipInputWhereFilter", strawberry.lazy(".membershipGQLModel")]

user_by_id = strawberry.field(
    description="",
    permission_classes=[
        OnlyForAuthentized
    ],
    graphql_type=Optional[UserGQLModel],
    # resolver=DBResolvers.UserModel.resolve_by_id(UserGQLModel)
    resolver=default_by_id_resolver()
)

@createInputs
@dataclass
class UserInputWhereFilter:
    id: IDType
    name: str
    surname: str
    email: str
    fullname: str
    valid: bool
    from .membershipGQLModel import MembershipInputWhereFilter
    memberships: MembershipInputWhereFilter
    from .roleGQLModel import RoleInputWhereFilter
    roles: RoleInputWhereFilter

# from ._GraphResolvers import createRootResolver_by_page, asPage

user_page = strawberry.field(
    description="returns list of users",
    permission_classes=[
        OnlyForAuthentized
    ],
    graphql_type=List[UserGQLModel],
    # resolver=DBResolvers.UserModel.resolve_page(UserGQLModel, WhereFilterModel=UserInputWhereFilter)
    resolver=default_page_resolver(whereType=UserInputWhereFilter)
    )




@strawberry.field(
    description="""This is logged user""",
    permission_classes=[OnlyForAuthentized])
async def me(self,
    info: strawberry.types.Info) -> Optional[UserGQLModel]:
    result = None
    user = getUserFromInfo(info)
    print(f"me: {user}")
    if user is None: return None
    user_id = user.get("id", None)
    if user_id is None: return None
    # user_id = IDType(user_id)
    result = await UserGQLModel.resolve_reference(info, user_id)
    return result


#####################################################################
#
# Mutation section
#
#####################################################################
import datetime

@strawberry.input(description="Describes values for U operation on UserGQLModel")
class UserUpdateGQLModel:
    id: IDType
    lastchange: datetime.datetime  # razitko
    name: Optional[str] = None
    surname: Optional[str] = None
    email: Optional[str] = None
    valid: Optional[bool] = None
    changedby: strawberry.Private[IDType] = None

@strawberry.input(description="Describes initial values for C operation on UserGQLModel")
class UserInsertGQLModel:
    id: Optional[IDType] = strawberry.field(description="primary key", default_factory=uuid.uuid1)
    name: Optional[str] = None
    surname: Optional[str] = None
    email: Optional[str] = None
    valid: Optional[bool] = None
    createdby: strawberry.Private[IDType] = None

@strawberry.type
class UserResultGQLModel:
    id: IDType = None
    msg: str = None

    @strawberry.field(description="""Result of user operation""")
    async def user(self, info: strawberry.types.Info) -> Union[UserGQLModel, None]:
        result = await UserGQLModel.resolve_reference(info, self.id)
        return result

class UpdateUserPermission(RBACPermission):
    message = "User is not allowed to update the user"
    async def has_permission(self, source, info: strawberry.types.Info, user: UserUpdateGQLModel) -> bool:
        adminRoleNames = ["administrátor", "personalista"]
        allowedRoleNames = []
        role = await self.resolveUserRole(info, 
            rbacobject=user.id, 
            adminRoleNames=adminRoleNames, 
            allowedRoleNames=allowedRoleNames)
        
        if not role: return False
        return True

@strawberry.mutation(
    description="",
    permission_classes=[
        OnlyForAuthentized,
        UpdateUserPermission
    ])
async def user_update(self, info: strawberry.types.Info, user: UserUpdateGQLModel) -> UserResultGQLModel:
    return await encapsulateUpdate(info, UserGQLModel.getLoader(info), user, UserResultGQLModel(msg="ok", id=user.id))

class InsertUserPermission(RBACPermission):
    message = "User is not allowed to create an user"
    async def has_permission(self, source, info: strawberry.types.Info, user: UserInsertGQLModel) -> bool:
        adminRoleNames = ["administrátor", "personalista"]
        allowedRoleNames = []
        role = await self.resolveUserRole(info, 
            rbacobject=user.id, 
            adminRoleNames=adminRoleNames, 
            allowedRoleNames=allowedRoleNames)
        
        if not role: return False
        return True

@strawberry.mutation(
    description="",
    permission_classes=[
        OnlyForAuthentized,
        InsertUserPermission                
    ])
async def user_insert(self, info: strawberry.types.Info, user: UserInsertGQLModel) -> UserResultGQLModel:
    return await encapsulateInsert(info, UserGQLModel.getLoader(info), user, UserResultGQLModel(msg="ok", id=None))

@strawberry.mutation(
    description="Deletes the user",
    permission_classes=[
        OnlyForAuthentized,
        OnlyForAdmins
    ])
async def user_delete(self, info: strawberry.types.Info, id: IDType) -> UserResultGQLModel:
    return await encapsulateDelete(info, UserGQLModel.getLoader(info), id, UserResultGQLModel(msg="ok", id=None))

#
# Relay
#

from .BaseGQLModel import Connection, List as BaseList
class UserConnection(Connection[UserGQLModel]):
    pass

class UserList(BaseList[UserGQLModel]):
    pass

@strawberry.field(
        description="Relay definition of users",
        permission_classes=[
            OnlyForAuthentized
        ],
    )
async def users(
        self, 
        # after: Optional[str]=0, 
        after: Annotated[Optional[str], strawberry.argument(description="")]="0", 
        first: Optional[int]=10, 
        orderby: Optional[str] = "id", 
        where: Optional[UserInputWhereFilter] = None
    ) -> Connection[UserGQLModel]:
    return UserConnection(skip=after, limit=first, where=where, orderby=orderby)    

# @strawberry.field(
#         description="users in page",
#         permission_classes=[
#             OnlyForAuthentized
#         ],
#     )
# async def user_page2(
#         self, 
#         info: strawberry.Info,
#         # after: Optional[str]=0, 
#         skip: Annotated[Optional[str], strawberry.argument(description="")]=0, 
#         limit: Optional[int]=10, 
#         orderby: Optional[str] = "id", 
#         where: Optional[UserInputWhereFilter] = None
#     ) -> typing.List[UserGQLModel]:
#     executor = UserList()
#     return await executor(info=info, skip=skip, limit=limit, orderby=orderby, where=where)