import datetime
import strawberry
import uuid
from typing import List, Optional, Union, Annotated
from uoishelpers.resolvers import createInputs

from .BaseGQLModel import BaseGQLModel, IDType
from ._GraphPermissions import (
    RoleBasedPermission, 
    OnlyForAuthentized,
    OnlyForAdmins,
    RBACPermission
)
import src.GraphTypeDefinitions
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

from src.Dataloaders import (
    getLoadersFromInfo as getLoader,
    getUserFromInfo)
from src.DBResolvers import DBResolvers

GroupGQLModel = Annotated["GroupGQLModel", strawberry.lazy(".groupGQLModel")]
UserGQLModel = Annotated["UserGQLModel", strawberry.lazy(".userGQLModel")]
RoleTypeGQLModel = Annotated["RoleTypeGQLModel", strawberry.lazy(".roleTypeGQLModel")]

@remove_constructor
@strawberry.federation.type(
    keys=["id"],
    description="""Entity representing a role of a user in a group (like user A in group B is Dean)""",
)
class RoleGQLModel(BaseGQLModel):
    @classmethod
    def getLoader(cls, info):
        return getLoader(info).RoleModel

    valid = strawberry.field(
        description="""If an user has still this role""",
        permission_classes=[
            OnlyForAuthentized
        ],
        graphql_type=bool,
        resolver=default_resolver
    )

    startdate = strawberry.field(
        description="""When an user has got this role""",
        permission_classes=[
            OnlyForAuthentized
        ],
        graphql_type=datetime.datetime,
        resolver=default_resolver
    )
    
    enddate = strawberry.field(
        description="""When an user has been removed from this role""",
        permission_classes=[
            OnlyForAuthentized
        ],
        graphql_type=datetime.datetime,
        resolver=default_resolver
    )
   
    roletype = strawberry.field(
        description="""Role type (like Dean)""",
        permission_classes=[
            OnlyForAuthentized
        ],
        graphql_type=Optional[RoleTypeGQLModel],
        resolver=default_scalar_resolver(fkey_field_name="roletype_id")
    )
    
    user = strawberry.field(
        description="""User having this role. Must be member of group?""",
        permission_classes=[
            OnlyForAuthentized
        ],
        graphql_type=Optional[UserGQLModel],
        resolver=default_scalar_resolver(fkey_field_name="user_id")
    )
   
    group = strawberry.field(
        description="""Group where user has a role name""",
        permission_classes=[
            OnlyForAuthentized
        ],
        graphql_type=Optional[GroupGQLModel],
        resolver=default_scalar_resolver(fkey_field_name="group_id")
    )
    
    RBACObjectGQLModel = Annotated["RBACObjectGQLModel", strawberry.lazy(".RBACObjectGQLModel")]
    @strawberry.field(
        description="""""",
        permission_classes=[OnlyForAuthentized])
    async def rbacobject(self, info: strawberry.types.Info) -> Optional[RBACObjectGQLModel]:
        from .RBACObjectGQLModel import RBACObjectGQLModel
        createdby = resolve_field(self=self, field_name="createdby")
        result = await RBACObjectGQLModel.resolve_reference(info, createdby)
        return result    
        
#####################################################################
#
# Special fields for query
#
#####################################################################
from .utils import createInputs
from dataclasses import dataclass
GroupInputWhereFilter = Annotated["GroupInputWhereFilter", strawberry.lazy(".groupGQLModel")]
UserInputWhereFilter = Annotated["UserInputWhereFilter", strawberry.lazy(".userGQLModel")]
RoleTypeInputWhereFilter = Annotated["RoleTypeInputWhereFilter", strawberry.lazy(".roleTypeGQLModel")]
@createInputs
@dataclass
class RoleInputWhereFilter:
    name: str
    valid: bool
    startdate: datetime.datetime
    enddate: datetime.datetime
    # from .groupGQLModel import GroupInputWhereFilter
    # from .userGQLModel import UserInputWhereFilter
    # from .roleTypeGQLModel import RoleTypeInputWhereFilter
    group: GroupInputWhereFilter
    user: UserInputWhereFilter
    roletype: RoleTypeInputWhereFilter

@strawberry.field(
    description="",
    permission_classes=[OnlyForAuthentized])
async def role_by_user(self, info: strawberry.types.Info, user_id: IDType) -> List["RoleGQLModel"]:
    loader = RoleGQLModel.getLoader(info)
    rows = await loader.filter_by(user_id=user_id)
    return rows

role_by_id = strawberry.field(
    description="",
    permission_classes=[
        OnlyForAuthentized
    ],
    graphql_type=Optional[RoleGQLModel],
    resolver=default_by_id_resolver()
)


role_page = strawberry.field(
    description="",
    permission_classes=[
        OnlyForAuthentized
    ],
    graphql_type=List[RoleGQLModel],
    # resolver=DBResolvers.RoleModel.resolve_page(RoleGQLModel, WhereFilterModel=RoleInputWhereFilter)
    resolver=default_page_resolver(whereType=RoleInputWhereFilter)
)

from src.DBDefinitions import (
    UserModel, MembershipModel, GroupModel, RoleModel
)
from sqlalchemy import select

async def resolve_roles_on_user(self, info: strawberry.types.Info, user_id: IDType, filter_user_id: Optional[IDType] = None) -> List["RoleGQLModel"]:
    # ve vsech skupinach, kde je user clenem najdi vsechny role a ty vrat
    from .membershipGQLModel import MembershipGQLModel
    loaderm = MembershipGQLModel.getLoader(info)
    rows = await loaderm.filter_by(user_id = user_id)
    groupids = [row.group_id for row in rows]
    # print("groupids", groupids)
    stmt = (
        select(RoleModel).
        where(RoleModel.group_id.in_(groupids))
    )
    if filter_user_id is not None:
        stmt = stmt.filter(RoleModel.user_id == filter_user_id)
        # print("filtered to", filter_user_id, flush=True)
    loader = RoleGQLModel.getLoader(info)
    rows = await loader.execute_select(stmt)
    return rows

async def resolve_roles_on_group(self, info: strawberry.types.Info, group_id: IDType, filter_user_id: Optional[IDType] = None) -> List["RoleGQLModel"]:
    # najdi vsechny role pro skupinu a nadrizene skupiny
    from .groupGQLModel import GroupGQLModel
    grouploader = GroupGQLModel.getLoader(info)
    groupids = []
    cid = group_id
    while cid is not None:
        row = await grouploader.load(cid)
        if row is None: break
        groupids.append(row.id)
        cid = row.mastergroup_id
    # print("groupids", groupids)
    stmt = (
        select(RoleModel).
        where(RoleModel.group_id.in_(groupids))
    )
    if filter_user_id is not None:
        stmt = stmt.filter(RoleModel.user_id == filter_user_id)
        # print("filtered to", filter_user_id, flush=True)
    roleloader = RoleGQLModel.getLoader(info)
    rows = await roleloader.execute_select(stmt)
    return rows

roles_on_user_decsription = """
## Description

Returns all roles applicable on an user (defined by userId).
If there is a dean, role with type named "dean" will be enlisted.
"""
@strawberry.field(
    description=roles_on_user_decsription,
    permission_classes=[OnlyForAuthentized])
async def roles_on_user(self, info: strawberry.types.Info, user_id: IDType) -> List["RoleGQLModel"]:
    rows = await resolve_roles_on_user(self, info, user_id=user_id)
    return rows

roles_on_group_decsription = """
## Description

Returns all roles applicable on a group (defined by groupId).
If the group is deparment which is subgroup of faculty, role with type named "dean" will be enlisted.
"""
@strawberry.field(
    description=roles_on_group_decsription,
    permission_classes=[OnlyForAuthentized])
async def roles_on_group(self, info: strawberry.types.Info, group_id: IDType) -> List["RoleGQLModel"]:
    rows = await resolve_roles_on_group(self, info=info, group_id=group_id)
    return rows

#####################################################################
#
# Mutation section
#
#####################################################################
import datetime

@strawberry.input(description="")
class RoleUpdateGQLModel:
    id: IDType
    lastchange: datetime.datetime
    valid: Optional[bool] = None
    startdate: Optional[datetime.datetime] = None
    enddate: Optional[datetime.datetime] = None
    changedby: strawberry.Private[IDType] = None

@strawberry.input(description="")
class RoleInsertGQLModel:
    user_id: IDType
    group_id: IDType
    roletype_id: IDType
    id: Optional[IDType] = strawberry.field(description="primary key", default_factory=uuid.uuid1)
    valid: Optional[bool] = True
    startdate: Optional[datetime.datetime] = strawberry.field(description="start datetime of role", default_factory=datetime.datetime.now)
    enddate: Optional[datetime.datetime] = None
    createdby: strawberry.Private[IDType] = None
    rbacobject: strawberry.Private[IDType] = None

@strawberry.type(description="")
class RoleResultGQLModel:
    id: Optional[IDType] = None
    msg: str = None

    @strawberry.field(description="""Result of user operation""")
    async def role(self, info: strawberry.types.Info) -> Optional[RoleGQLModel]:
        result = await RoleGQLModel.resolve_reference(info, self.id)
        return result
    
class UpdateRolePermission(RBACPermission):
    message = "User is not allowed to update the role"
    async def has_permission(self, source, info: strawberry.types.Info, role: RoleUpdateGQLModel) -> bool:
        adminRoleNames = ["administrátor"]
        allowedRoleNames = ["garant"]
        loader = RoleGQLModel.getLoader(info)
        rolerow = await loader.load(role.id)
        _role = await self.resolveUserRole(info, 
            rbacobject=rolerow.group_id, 
            adminRoleNames=adminRoleNames, 
            allowedRoleNames=allowedRoleNames)
        
        if not _role: return False
        return True

@strawberry.mutation(
    description="""Updates a role""",
    permission_classes=[
        OnlyForAuthentized,
        UpdateRolePermission
    ])
async def role_update(self, 
    info: strawberry.types.Info, 
    role: RoleUpdateGQLModel
) -> RoleResultGQLModel:
    return await encapsulateUpdate(info, RoleGQLModel.getLoader(info), role, RoleResultGQLModel(msg="ok", id=role.id))

class InsertRolePermission(RBACPermission):
    message = "User is not allowed create new role"
    async def has_permission(self, source, info: strawberry.types.Info, role: RoleInsertGQLModel) -> bool:
        adminRoleNames = ["administrátor"]
        allowedRoleNames = ["garant"]
        _role = await self.resolveUserRole(info, 
            rbacobject=role.group_id, 
            adminRoleNames=adminRoleNames, 
            allowedRoleNames=allowedRoleNames)
        
        if not _role: return False
        return True

@strawberry.mutation(
    description="""Inserts a role""",
    permission_classes=[
        OnlyForAuthentized,
        InsertRolePermission
    ])
async def role_insert(self, 
    info: strawberry.types.Info, 
    role: RoleInsertGQLModel
) -> RoleResultGQLModel:
    role.rbacobject = role.group_id
    return await encapsulateInsert(info, RoleGQLModel.getLoader(info), role, RoleResultGQLModel(msg="ok", id=None))
    
@strawberry.mutation(
    description="Deletes the role",
    permission_classes=[
        OnlyForAuthentized,
        OnlyForAdmins
    ])
async def role_delete(self, info: strawberry.types.Info, id: IDType) -> RoleResultGQLModel:
    return await encapsulateDelete(info, RoleGQLModel.getLoader(info), id, RoleResultGQLModel(msg="ok", id=None))

from .BaseGQLModel import Connection
class RoleConnection(Connection[RoleGQLModel]):
    pass
