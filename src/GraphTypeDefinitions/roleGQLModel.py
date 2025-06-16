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
from src.Dataloaders import (
    getLoadersFromInfo as getLoader,
    getUserFromInfo)
from src.DBResolvers import DBResolvers

GroupGQLModel = Annotated["GroupGQLModel", strawberry.lazy(".groupGQLModel")]
UserGQLModel = Annotated["UserGQLModel", strawberry.lazy(".userGQLModel")]
RoleTypeGQLModel = Annotated["RoleTypeGQLModel", strawberry.lazy(".roleTypeGQLModel")]

@strawberry.federation.type(
    keys=["id"],
    description="""## Description
Entity representing a role of a user in a group (e.g. user A in group B is Dean)
Entita reprezentující roli uživatele ve skupině (např. uživatel A ve skupině B je Dekan)

## Details
Includes role validity, deputy status, start and end dates, and identifiers linking to role type, user, and group. Provides resolvers to fetch detailed information for role type, user, and group.
Obsahuje informace o platnosti role, statusu zástupce, datu nástupu a ukončení, a identifikátory pro typ role, uživatele a skupinu. Obsahuje resolvery pro načítání podrobných informací.

## Permissions
Accessible only to authenticated users.
Přístup je omezen pouze na autentizované uživatele.
"""
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
        description="""If the user still holds this role
Jestli uživatel tuto roli stále zastává""",
        permission_classes=[OnlyForAuthentized],
    )

    deputy: typing.Optional[bool] = strawberry.field(
        description="""Indicates if this role is assigned as deputy
Ukazuje, zda je tato role přiřazena jako zástupce""",
        permission_classes=[OnlyForAuthentized],
    )

    startdate: typing.Optional[datetime.datetime] = strawberry.field(
        description="""The date when the user assumed this role
Datum, kdy uživatel tuto roli převzal""",
        permission_classes=[OnlyForAuthentized],
    )

    enddate: typing.Optional[datetime.datetime] = strawberry.field(
        description="""The date when the user was removed from this role
Datum, kdy byl uživatel odebrán z této role""",
        permission_classes=[OnlyForAuthentized],
    )

    roletype_id: typing.Optional[IDType] = strawberry.field(
        description="""Identifier of the role type
Identifikátor typu role""",
        permission_classes=[OnlyForAuthentized],
    )

    user_id: typing.Optional[IDType] = strawberry.field(
        description="""Identifier of the user who holds this role
Identifikátor uživatele, který tuto roli zastává""",
        permission_classes=[OnlyForAuthentized],
    )

    group_id: typing.Optional[IDType] = strawberry.field(
        description="""Identifier of the group to which this role belongs
Identifikátor skupiny, ke které tato role patří""",
        permission_classes=[OnlyForAuthentized],
    )

    roletype: typing.Optional[RoleTypeGQLModel] = strawberry.field(
        description="""Role type detail (e.g. Dean)
Detail typu role (např. Dekan)""",
        permission_classes=[OnlyForAuthentized],
        resolver=ScalarResolver[RoleTypeGQLModel](fkey_field_name="roletype_id")
    )

    user: typing.Optional[UserGQLModel] = strawberry.field(
        description="""User associated with this role
Uživatel spojený s touto rolí""",
        permission_classes=[OnlyForAuthentized],
        resolver=ScalarResolver[UserGQLModel](fkey_field_name="user_id")
    )

    group: typing.Optional[GroupGQLModel] = strawberry.field(
        description="""Group in which the role is assigned
Skupina, ve které je role přiřazena""",
        permission_classes=[OnlyForAuthentized],
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
    description="""## Description
Fetches roles assigned to a user by their identifier.
Načte role přiřazené uživateli dle jeho identifikátoru.

## Details
Utilizes a data loader to filter and return a list of roles for the specified user.
Využívá loader pro filtrování a vrácení seznamu rolí pro zadaného uživatele.

## Permissions
Accessible only to authenticated users.
Přístup pouze pro autentizované uživatele.
""",
    permission_classes=[OnlyForAuthentized]
)
async def role_by_user(self, info: strawberry.types.Info, user_id: IDType) -> List["RoleGQLModel"]:
    loader = RoleGQLModel.getLoader(info)
    rows = await loader.filter_by(user_id=user_id)
    return (RoleGQLModel.from_dataclass(row) for row in rows)

role_by_id = strawberry.field(
    description="""## Description
Fetches a role by its unique identifier.
Načte roli podle jejího unikátního identifikátoru.

## Details
Utilizes a data loader to efficiently retrieve role details.
Využívá loader pro efektivní načtení detailů role.

## Permissions
Accessible only to authenticated users.
Přístup pouze pro autentizované uživatele.
""",
    permission_classes=[OnlyForAuthentized],
    graphql_type=Optional[RoleGQLModel],
    resolver=RoleGQLModel.load_with_loader
)

role_page = strawberry.field(
    description="""## Description
Fetches a paginated list of roles.
Načte stránkovaný seznam rolí.

## Details
Returns a list of roles based on filtering criteria defined in RoleInputWhereFilter. Supports pagination, sorting, and advanced filtering options.
Vrací seznam rolí na základě filtračních kritérií definovaných ve třídě RoleInputWhereFilter. Podporuje stránkování, řazení a pokročilé filtrovací možnosti.

## Permissions
Accessible only to authenticated users.
Přístup pouze pro autentizované uživatele.
""",
    permission_classes=[OnlyForAuthentized],
    graphql_type=List[RoleGQLModel],
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
    membershiprows = await loaderm.filter_by(user_id = user_id)
    groupids = [row.group_id for row in membershiprows]

    from .groupGQLModel import GroupGQLModel
    group_loader = GroupGQLModel.getLoader(info)
    groupfutures = (group_loader.load(gid) for gid in groupids)
    grouprows = await asyncio.gather(*groupfutures)

    grouppaths = [row.path for row in grouprows if row.path]
    groupids2 = set(groupids)
    for path in grouppaths:
        for id_str in path.split('/'):
            try:
                groupids2.add(IDType(id_str))
            except ValueError:
                # neplatné UUID, přeskočit nebo logovat
                pass

    # print("groupids", groupids)
    stmt = (
        select(RoleModel).
        where(RoleModel.group_id.in_(groupids2))
    )
    # if filter_user_id is not None:
    #     stmt = stmt.filter(RoleModel.user_id == filter_user_id)
        # print("filtered to", filter_user_id, flush=True)
    roleloader = RoleGQLModel.getLoader(info)
    rolerows = await roleloader.execute_select(stmt)
    return rolerows

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
roles_on_user_description = """## Description
Returns all roles applicable on a user (defined by userId).
Vrací všechny role vztahující se k uživateli (definovanému pomocí userId).

## Details
If there is a dean role, the role with type "dean" will be included.
Pokud existuje role děkana, role s typem "dean" bude zahrnuta.

## Permissions
Accessible only to authenticated users.
Přístup pouze pro autentizované uživatele.
"""

@strawberry.field(
    description=roles_on_user_description,
    permission_classes=[OnlyForAuthentized]
)
async def roles_on_user(self, info: strawberry.types.Info, user_id: IDType) -> List["RoleGQLModel"]:
    rows = await resolve_roles_on_user(self, info, user_id=user_id)
    return (RoleGQLModel.from_dataclass(row) for row in rows)

roles_on_group_description = """## Description
Returns all roles applicable on a group (defined by groupId).
Vrací všechny role vztahující se ke skupině (definované pomocí groupId).

## Details
If the group is a department and a subgroup of a faculty, the role with type "dean" will be included.
Pokud je skupina oddělením a podskupinou fakulty, role s typem "dean" bude zahrnuta.

## Permissions
Accessible only to authenticated users.
Přístup pouze pro autentizované uživatele.
"""

@strawberry.field(
    description=roles_on_group_description,
    permission_classes=[OnlyForAuthentized]
)
async def roles_on_group(self, info: strawberry.types.Info, group_id: IDType) -> List["RoleGQLModel"]:
    rows = await resolve_roles_on_group(self, info=info, group_id=group_id)
    return (RoleGQLModel.from_dataclass(row) for row in rows)


#####################################################################
#
# Mutation section
#
#####################################################################
import datetime
from uoishelpers.resolvers import InputModelMixin
@strawberry.input(description="""## Description
Update input for Role entity.
Vstup pro aktualizaci entity Role.

## Details
Provides input for updating a Role with necessary identifiers and timestamps. Optional fields allow modification of role validity and duration.
Poskytuje vstup pro aktualizaci role s potřebnými identifikátory a časovým razítkem. Volitelná pole umožňují změnu platnosti role a její doby trvání.
""")
class RoleUpdateGQLModel:
    id: IDType = strawberry.field(description="Unique identifier\nUnikátní identifikátor")
    lastchange: datetime.datetime = strawberry.field(description="Timestamp of last change\nČasové razítko poslední změny")
    valid: Optional[bool] = strawberry.field(description="Role validity status\nStav platnosti role", default=None)
    startdate: Optional[datetime.datetime] = strawberry.field(description="Start date of role\nDatum začátku role", default=None)
    enddate: Optional[datetime.datetime] = strawberry.field(description="End date of role\nDatum ukončení role", default=None)
    changedby_id: strawberry.Private[IDType] = None

@strawberry.input(description="""## Description
Insert input for Role entity.
Vstup pro vytvoření entity Role.

## Details
Provides input for creating a new Role, including user, group, and role type identifiers. Optional fields include deputy status and role duration.
Poskytuje vstup pro vytvoření nové role, včetně identifikátorů uživatele, skupiny a typu role. Volitelná pole zahrnují status zástupce a dobu trvání role.
""")
class RoleInsertGQLModel(InputModelMixin):
    user_id: IDType = strawberry.field(description="User identifier\nIdentifikátor uživatele")
    group_id: IDType = strawberry.field(description="Group identifier\nIdentifikátor skupiny")
    roletype_id: IDType = strawberry.field(description="Role type identifier\nIdentifikátor typu role")
    id: Optional[IDType] = strawberry.field(description="Primary key\nPrimární klíč", default=None)
    deputy: Optional[bool] = strawberry.field(description="Deputy role status\nStatus zástupce", default=False)
    startdate: Optional[datetime.datetime] = strawberry.field(description="Start datetime of role\nDatum začátku role", default_factory=datetime.datetime.now)
    enddate: Optional[datetime.datetime] = strawberry.field(description="End datetime of role\nDatum ukončení role", default=None)
    createdby_id: strawberry.Private[IDType] = None
    rbacobject_id: strawberry.Private[IDType] = None

@strawberry.input(description="""## Description
Delete input for Role entity.
Vstup pro odstranění entity Role.

## Details
Provides input for deleting a Role using its unique identifier and last change timestamp.
Poskytuje vstup pro odstranění role pomocí unikátního identifikátoru a časového razítka poslední změny.
""")
class RoleDeleteGQLModel:
    id: IDType = strawberry.field(description="Unique identifier\nUnikátní identifikátor")
    lastchange: datetime.datetime = strawberry.field(description="Timestamp of last change\nČasové razítko poslední změny")

   
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
    description="""## Description
Updates a role.
Aktualizuje roli.

## Details
Executes a safe update operation for a role based on the provided input, verifying that the user has the necessary permissions to update the role.
Provádí bezpečnou aktualizaci role na základě poskytnutého vstupu, přičemž ověřuje, zda má uživatel potřebná oprávnění pro aktualizaci role.

## Permissions
Accessible only to authenticated users with update permissions.
Přístup mají pouze autentizovaní uživatelé s oprávněními pro aktualizaci.
""",
    permission_classes=[OnlyForAuthentized, UpdateRolePermission]
)
async def role_update(self, info: strawberry.types.Info, role: RoleUpdateGQLModel) -> typing.Union[RoleGQLModel, UpdateError[RoleGQLModel]]:
    return await Update[RoleGQLModel].DoItSafeWay(info=info, entity=role)

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
    description="""## Description
Inserts a new role.
Vloží novou roli.

## Details
Sets rbacobject_id to group_id to ensure role association consistency before insertion.
Nastaví rbacobject_id na group_id pro zajištění konzistence přiřazení role před vložením.

## Permissions
Accessible only to authenticated users with the necessary permissions to insert roles.
Přístup mají pouze autentizovaní uživatelé s potřebnými oprávněními pro vkládání rolí.
""",
    permission_classes=[OnlyForAuthentized, InsertRolePermission]
)
async def role_insert(self, info: strawberry.types.Info, role: RoleInsertGQLModel) -> typing.Union[RoleGQLModel, InsertError[RoleGQLModel]]:
    role.rbacobject_id = role.group_id
    return await Insert[RoleGQLModel].DoItSafeWay(info=info, entity=role)

@strawberry.mutation(
    description="""## Description
Deletes a role.
Odstraní roli.

## Details
Performs safe deletion using the unique identifier and last change timestamp.
Provádí bezpečné odstranění pomocí unikátního identifikátoru a časového razítka poslední změny.

## Permissions
Accessible only to authenticated users with administrative privileges.
Přístup mají pouze autentizovaní uživatelé s administrátorskými právy.
""",
    permission_classes=[OnlyForAuthentized, OnlyForAdmins]
)
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


