import dataclasses
import datetime
import typing
import strawberry
import uuid
import asyncio
from typing import List, Optional, Union, Annotated
from uoishelpers.resolvers import (
    createInputs,

    ScalarResolver,
    VectorResolver,
    PageResolver,

    # Insert,
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


@strawberry.federation.type(
    keys=["id"],
    description="""Entity representing a role of a user in a group (like user A in group B is Dean)""",
)
class RoleGQLModel(BaseGQLModel):
    @classmethod
    def getLoader(cls, info):
        return getLoader(info).RoleModel

    @classmethod
    def from_dataclass(cls, db_row):
        db_row_dict = dataclasses.asdict(db_row)
        db_row_dict["valid"] = db_row.valid
        instance = cls(**db_row_dict)
        return instance

    valid: typing.Optional[bool] = strawberry.field(
        description="""If an user has still this role""",
        permission_classes=[
            OnlyForAuthentized
        ],
    )

    startdate: typing.Optional[datetime.datetime] = strawberry.field(
        description="""When an user has got this role""",
        permission_classes=[
            OnlyForAuthentized
        ]
    )
    
    enddate: typing.Optional[datetime.datetime] = strawberry.field(
        description="""When an user has been removed from this role""",
        permission_classes=[
            OnlyForAuthentized
        ]
    )

    roletype_id: typing.Optional[IDType] = strawberry.field(
        description="id of role type",
        permission_classes=[
            OnlyForAuthentized
        ]        
    )

    user_id: typing.Optional[IDType] = strawberry.field(
        description="id of user who plays this role type",
        permission_classes=[
            OnlyForAuthentized
        ]        
    )

    group_id: typing.Optional[IDType] = strawberry.field(
        description="id of group which role type belongs to",
        permission_classes=[
            OnlyForAuthentized
        ]        
    )   

    roletype: typing.Optional[RoleTypeGQLModel] = strawberry.field(
        description="""Role type (like Dean)""",
        permission_classes=[
            OnlyForAuthentized
        ],
        resolver=ScalarResolver[RoleTypeGQLModel](fkey_field_name="roletype_id")
    )
    
    user: typing.Optional[UserGQLModel] = strawberry.field(
        description="""User having this role. Must be member of group?""",
        permission_classes=[
            OnlyForAuthentized
        ],
        resolver=ScalarResolver[UserGQLModel](fkey_field_name="user_id")
    )
   
    group: typing.Optional[GroupGQLModel] = strawberry.field(
        description="""Group where user has a role name""",
        permission_classes=[
            OnlyForAuthentized
        ],
        resolver=ScalarResolver[GroupGQLModel](fkey_field_name="group_id")
    )
    
        
#####################################################################
#
# Special fields for query
#
#####################################################################
from uoishelpers.resolvers import createInputs
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
    resolver=RoleGQLModel.load_with_loader
)


role_page = strawberry.field(
    description="",
    permission_classes=[
        OnlyForAuthentized
    ],
    graphql_type=List[RoleGQLModel],
    # resolver=DBResolvers.RoleModel.resolve_page(RoleGQLModel, WhereFilterModel=RoleInputWhereFilter)
    resolver=PageResolver[RoleGQLModel](whereType=RoleInputWhereFilter)
)

from src.DBDefinitions import (
    UserModel, MembershipModel, GroupModel, RoleModel
)
from sqlalchemy import select

async def resolve_roles_on_user(self, info: strawberry.types.Info, user_id: IDType, filter_user_id: Optional[IDType] = None) -> List["RoleGQLModel"]:
    # ve vsech skupinach, kde je user clenem najdi vsechny role a ty vrat
    if filter_user_id is not None:
        return await resolve_roles_on_user_with_user(self, info=info, user_id=user_id,filter_user_id=filter_user_id)
    
    from .membershipGQLModel import MembershipGQLModel
    loaderm = MembershipGQLModel.getLoader(info)
    rows = await loaderm.filter_by(user_id = user_id)
    groupids = [row.group_id for row in rows]
    # print("groupids", groupids)
    stmt = (
        select(RoleModel).
        where(RoleModel.group_id.in_(groupids))
    )
    # if filter_user_id is not None:
    #     stmt = stmt.filter(RoleModel.user_id == filter_user_id)
        # print("filtered to", filter_user_id, flush=True)
    loader = RoleGQLModel.getLoader(info)
    rows = await loader.execute_select(stmt)
    return rows

async def resolve_roles_on_user_with_user(self, info: strawberry.types.Info, user_id: IDType, filter_user_id: IDType) -> List["RoleGQLModel"]:
    loaderr = RoleGQLModel.getLoader(info=info)
    stmtr = loaderr.getSelectStatement()
    modelr = loaderr.getModel()
    stmtr = stmtr.filter_by(user_id=filter_user_id).join(modelr.memberships).where(modelr.user_id==user_id)
    rows = await loaderr.execute_select(stmtr)
    return rows

async def resolve_roles_on_group_with_user(self, info: strawberry.types.Info, group_id: IDType, filter_user_id: IDType) -> List["RoleGQLModel"]:
    from .groupGQLModel import GroupGQLModel
    loaderg = GroupGQLModel.getLoader(info=info)
    # modelg = loaderg.getModel()
    # print(f"loading group {group_id}")
    group = await loaderg.load(group_id)
    # print(f"got group {group}")
    if group is None:
        return []
    path = group.path
    ids = path.split("/")
    ids = [IDType(id) for id in ids]
    loaderr = RoleGQLModel.getLoader(info=info)
    stmtr = loaderr.getSelectStatement()
    modelr = loaderr.getModel()
    stmtr = stmtr.filter_by(user_id=filter_user_id).where(modelr.group_id.in_(ids))
    rows = await loaderr.execute_select(stmtr)
    return rows

async def resolve_roles_on_group(self, info: strawberry.types.Info, group_id: IDType, filter_user_id: Optional[IDType] = None) -> List["RoleGQLModel"]:
    # najdi vsechny role pro skupinu a nadrizene skupiny
    if filter_user_id is not None:
        return await resolve_roles_on_group_with_user(self, info=info, group_id=group_id, filter_user_id=filter_user_id)
    
    from .groupGQLModel import GroupGQLModel
    grouploader = GroupGQLModel.getLoader(info)
    # TODO refactor with the help of materialized path
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
    changedby_id: strawberry.Private[IDType] = None

@strawberry.input(description="")
class RoleInsertGQLModel:
    user_id: IDType
    group_id: IDType
    roletype_id: IDType
    id: Optional[IDType] = strawberry.field(description="primary key", default_factory=uuid.uuid1)
    valid: Optional[bool] = True
    startdate: Optional[datetime.datetime] = strawberry.field(description="start datetime of role", default_factory=datetime.datetime.now)
    enddate: Optional[datetime.datetime] = None
    createdby_id: strawberry.Private[IDType] = None
    rbacobject: strawberry.Private[IDType] = None

@strawberry.input(description="")
class RoleDeleteGQLModel:
    id: IDType
    lastchange: datetime.datetime

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
) -> typing.Union[RoleGQLModel, UpdateError[RoleGQLModel]]:
    return await Update[RoleGQLModel].DoItSafeWay(info=info, entity=role)
    # return await encapsulateUpdate(info, RoleGQLModel.getLoader(info), role, RoleResultGQLModel(msg="ok", id=role.id))

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
) -> typing.Union[RoleGQLModel, InsertError[RoleGQLModel]]:
    role.rbacobject = role.group_id
    return await Insert[RoleGQLModel].DoItSafeWay(info=info, entity=role)
    
@strawberry.mutation(
    description="Deletes the role",
    permission_classes=[
        OnlyForAuthentized,
        OnlyForAdmins
    ])
async def role_delete(self, info: strawberry.types.Info, role: RoleDeleteGQLModel) -> typing.Optional[DeleteError[RoleGQLModel]]:
    return await Delete[RoleGQLModel].DoItSafeWay(info=info, entity=role)

@strawberry.type(description="")
class RBACItem:
    rbac_id: IDType
    roles: List[RoleGQLModel]

async def resolve_rbac_with_user(self, info: strawberry.types.Info, rbac_id: IDType, user_id: IDType):
    from .roleGQLModel import resolve_roles_on_user, resolve_roles_on_group
    awaitableresult0 = resolve_roles_on_user(None, info, user_id=rbac_id, filter_user_id=user_id)
    awaitableresult1 = resolve_roles_on_group(None, info, group_id=rbac_id, filter_user_id=user_id)
    result0, result1 = await asyncio.gather(awaitableresult0, awaitableresult1)
    roles = [*result0, *result1]
    return roles

@strawberry.field(description="")
async def resolveRBACs(self, info: strawberry.types.Info, rbac_ids: List[IDType], user_id: typing.Optional[IDType] = None) -> List[RBACItem]:
    from .roleGQLModel import RoleGQLModel
    # resolvedroles = await asyncio.gather(RBACObjectGQLModel.resolve_reference(info=info, id=id) for id in rbac_ids)
    if user_id is None:
        user = getUserFromInfo(info=info)
        user_id = user["id"]
        user_id = IDType(user_id) if isinstance(user_id, str) else user_id
    # print("resolveRBACs", [type(id) for id in rbac_ids], flush=True)
    _rbac_ids = [rbac_id if isinstance(rbac_id, IDType) else IDType(rbac_id) for rbac_id in rbac_ids]
    # print("resolveRBACs", [type(id) for id in _rbac_ids])
    futures = (resolve_rbac_with_user(self, info=info, rbac_id=rbac_id, user_id=user_id) for rbac_id in _rbac_ids)
    resolvedroles = await asyncio.gather(*futures)
    index = {
        role.id: role
        for rolelist in resolvedroles
        for role in rolelist
    }
    # print("resolveRBACs", resolvedroles, flush=True)
    result = [
        RBACItem(rbac_id=rbac_id, roles=[RoleGQLModel.from_dataclass(role) for role in index.values()]) 
        for rbac_id, roles in zip(rbac_ids, resolvedroles)]

    return result


