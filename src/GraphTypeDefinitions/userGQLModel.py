import datetime
import strawberry
import asyncio
import uuid
import typing
import dataclasses

from typing import List, Optional, Union, Annotated
import typing

import strawberry.types
from uoishelpers.resolvers import (
    createInputs,

    VectorResolver,
    ScalarResolver,
    PageResolver,

    InsertError,
    Insert,
    UpdateError,
    Update,
    DeleteError,
    Delete
)

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



@strawberry.federation.type(keys=["id"], description="""Entity representing a user""")
class UserGQLModel(BaseGQLModel):
    @classmethod
    def getLoader(cls, info):
        return getLoader(info).UserModel
    
    name: typing.Optional[str] = strawberry.field(
        default=None,
        description="""Full name (if in database)""",
        permission_classes=[
            OnlyForAuthentized
        ]
        )
    
    surname: typing.Optional[str] = strawberry.field(
        default=None,
        description="""Family name""",
        permission_classes=[
            OnlyForAuthentized
        ]
        )
    
    givenname: typing.Optional[str] = strawberry.field(
        default=None,
        description="""User's name (like John)""",
        permission_classes=[
            OnlyForAuthentized
        ]
        )
    
    middlename: typing.Optional[str] = strawberry.field(
        default=None,
        description="""name""",
        permission_classes=[
            OnlyForAuthentized
        ]
        )
    
    email: typing.Optional[str] = strawberry.field(
        default=None,
        description="""email""",
        permission_classes=[
            OnlyForAuthentized
        ]
        )
    
    firstname: typing.Optional[str] = strawberry.field(
        description="""User's name (like John)""",
        default=None,
        permission_classes=[
            OnlyForAuthentized
        ]
    )  

    surname: typing.Optional[str] = strawberry.field(
        description="""User's family name (like Obama)""",
        permission_classes=[
            OnlyForAuthentized
        ]
    )  

    # fullname: typing.Optional[str] = strawberry.field(
    #     description="""User's full name""",
    #     default=None,
    #     permission_classes=[
    #         OnlyForAuthentized
    #     ]
    # )  

    valid: typing.Optional[bool] = strawberry.field(
        description="""If the user is still valid""",
        permission_classes=[
            OnlyForAuthentized
        ]
    )

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

    type_id: typing.Optional[IDType] = strawberry.field(
        description="",
        permission_classes=[
            OnlyForAuthentized
        ]
    )

    @strawberry.field(
        description="""if this record is related to logged user""",
        permission_classes=[
            OnlyForAuthentized
        ])
    async def is_this_me(self, info: strawberry.types.Info) -> bool:
        user = getUserFromInfo(info)
        # selfid = self.id if self._data is None else self._data.id
        # print(f"me: {user}")
        if user is None: return None
        user_id = user.get("id", None)
        # print(f"is_this_me {type(user_id)}, {type(self.id)}", flush=True)
        # print(f"is_this_me {user_id==self.id}", flush=True)
        # return f"{self.id}" == f"{user_id}"
        return user_id==self.id
        

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
            # RoleBasedPermission("zpracovatel gdpr")
        ])
    def gdpr(self, info: strawberry.types.Info, force: typing.Optional[bool] = False) -> typing.Optional[str]:
        return "gdpr information" if force else None

    @strawberry.field(
        description="""User's name (like John Newbie)""",
        permission_classes=[
            OnlyForAuthentized
        ]
    )
    def fullname(self, info: strawberry.types.Info) -> typing.Optional[str]:
        return f"{self.name} {self.middlename} {self.surname}" if self.middlename else f"{self.name} {self.surname}" 
    

    memberships: typing.List[MembershipGQLModel] = strawberry.field(
        description="""List of mmeberships associated with the user""",
        permission_classes=[
            OnlyForAuthentized
        ],
        resolver=VectorResolver[MembershipGQLModel](fkey_field_name="user_id", whereType=MembershipInputWhereFilter)
    )

    membership: typing.List[MembershipGQLModel] = strawberry.field(
        description="""List of mmeberships associated with the user""",
        deprecation_reason="use memberships",
        permission_classes=[
            OnlyForAuthentized
        ],
        resolver=VectorResolver[MembershipGQLModel](fkey_field_name="user_id", whereType=MembershipInputWhereFilter)
    )

    roles: typing.List[RoleGQLModel] = strawberry.field(
        description="""User's roles (like Dean)""",
        permission_classes=[
            OnlyForAuthentized
        ],
        resolver=VectorResolver[RoleGQLModel](fkey_field_name="user_id", whereType=RoleInputWhereFilter)
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
        permission_classes=[
            OnlyForAuthentized
        ]
    )
    async def groups(
        self, 
        info: strawberry.types.Info, 
        limit: typing.Optional[int] = 10,
        skip: typing.Optional[int] = 0,
        order_by: typing.Optional[str] = None,
        where: typing.Optional[MembershipInputWhereFilter] = None
        ) -> typing.List["GroupGQLModel"]:
        from .membershipGQLModel import MembershipGQLModel
        from .groupGQLModel import GroupGQLModel

        membershipLoader = MembershipGQLModel.getLoader(info=info)
        extendedfilter = {"user_id": self.id}
        where = None if where is None else strawberry.asdict(where)
        memberships = await membershipLoader.page(skip=skip, limit=limit, orderby=order_by, where=where, extendedfilter=extendedfilter)

        groupLoader = GroupGQLModel.getLoader(info=info)
        future_groups = (groupLoader.load(membership.group_id) for membership in memberships)
        group_rows = await asyncio.gather(*future_groups)
        results = (GroupGQLModel.from_dataclass(row) for row in group_rows)        
        return results

    @strawberry.field(
        description="""List of groups given type, where the user is member""",
        permission_classes=[OnlyForAuthentized])
    async def member_of(
        self, info: strawberry.types.Info, grouptype_id: Optional[IDType] = None, 
    ) -> typing.List["GroupGQLModel"]:
        from .groupGQLModel import GroupGQLModel
        from .membershipGQLModel import MembershipGQLModel
        loader = MembershipGQLModel.getLoader(info)
        rows = await loader.filter_by(user_id=self.id)# , grouptype_id=grouptype_id)
        # memberships = (MembershipGQLModel.from_dataclass(row) for row in rows)
        groupLoader = GroupGQLModel.getLoader(info=info)
        futureresults = (groupLoader.load(row.group_id) for row in rows if row.valid)
        rows = await asyncio.gather(*futureresults)
        rows = filter(lambda item: item.grouptype_id == grouptype_id, rows)
        if grouptype_id:
            rows = filter(lambda item: item.grouptype_id == grouptype_id, rows)
        results = ()
        return results
    
#####################################################################
#
# Special fields for query
#
#####################################################################

from uoishelpers.resolvers import createInputs
from dataclasses import dataclass
#MembershipInputWhereFilter = Annotated["MembershipInputWhereFilter", strawberry.lazy(".membershipGQLModel")]

user_by_id = strawberry.field(
    description="",
    permission_classes=[
        OnlyForAuthentized
    ],
    graphql_type=Optional[UserGQLModel],
    resolver=UserGQLModel.load_with_loader
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
    resolver=PageResolver[UserGQLModel](whereType=UserInputWhereFilter)
    )

@strawberry.field(
    description="""This is logged user""",
    permission_classes=[OnlyForAuthentized])
async def me(self,
    info: strawberry.types.Info) -> Optional[UserGQLModel]:
    result = None
    user = getUserFromInfo(info)
    # print(f"?me>: {user}")
    if user is None: return None
    user_id = user.get("id", None)
    if user_id is None: return None
    # user_id = IDType(user_id)
    result = await UserGQLModel.resolve_reference(info=info, id=user_id)
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
    changedby_id: strawberry.Private[IDType] = None

@strawberry.input(description="Describes initial values for C operation on UserGQLModel")
class UserInsertGQLModel:
    id: Optional[IDType] = strawberry.field(description="primary key", default_factory=uuid.uuid1)
    name: Optional[str] = None
    surname: Optional[str] = None
    email: Optional[str] = None
    valid: Optional[bool] = None
    createdby_id: strawberry.Private[IDType] = None

@strawberry.input(description="Describes D operation on UserGQLModel")
class UserDeleteGQLModel:
    id: Optional[IDType] = strawberry.field(description="primary key", default_factory=uuid.uuid1)
    lastchange: datetime.datetime  # razitko

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
async def user_update(self, info: strawberry.types.Info, user: UserUpdateGQLModel) -> typing.Union[UserGQLModel, UpdateError[UserGQLModel]]:
    return await Update[UserGQLModel].DoItSafeWay(info=info, entity=user)
    # return await encapsulateUpdate(info, UserGQLModel.getLoader(info), user, UserResultGQLModel(msg="ok", id=user.id))

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
async def user_insert(self, info: strawberry.types.Info, user: UserInsertGQLModel) -> typing.Union[UserGQLModel, InsertError[UserGQLModel]]:
    return await Insert[UserGQLModel].DoItSafeWay(info=info, entity=user)
    # return await encapsulateInsert(info, UserGQLModel.getLoader(info), user, UserResultGQLModel(msg="ok", id=None))

@strawberry.mutation(
    description="Deletes the user",
    permission_classes=[
        OnlyForAuthentized,
        OnlyForAdmins
    ])
async def user_delete(self, info: strawberry.types.Info, user: UserDeleteGQLModel) -> typing.Optional[DeleteError[UserGQLModel]]:
    return await Delete[UserGQLModel].DoItSafeWay(info=info, entity=user)
    # return await encapsulateDelete(info, UserGQLModel.getLoader(info), id, UserResultGQLModel(msg="ok", id=None))

