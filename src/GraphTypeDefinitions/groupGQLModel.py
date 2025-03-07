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
Group is an entity with members.  
Skupina je entita se členy.

## Details
- It can have a master group; only one master group is allowed.  
  Může mít nadřazenou skupinu; je povolena pouze jedna nadřazená skupina.
- Groups are organized in a hierarchical tree structure.  
  Skupiny jsou organizovány ve stromové hierarchii.
- Roles can be defined on the group to control permissions and access.  
  Na skupině lze definovat role, které ovlivňují oprávnění a přístup.

## Business Rules
- A group may have only one master group.  
  Skupina může mít pouze jednu nadřazenou skupinu.
- The hierarchy must be consistent.  
  Hierarchie musí být udržována konzistentně.
"""

@strawberry.federation.type(keys=["id"], description=GroupGQLModel_description)
class GroupGQLModel(NamedGQLModel):
    @classmethod
    def getLoader(cls, info):
        return getLoader(info).GroupModel

    email: typing.Optional[str] = strawberry.field(
        description="""Group's email address.  
Emailová adresa skupiny.""",
        permission_classes=[OnlyForAuthentized]
    )
    
    abbreviation: typing.Optional[str] = strawberry.field(
        description="""Abbreviation or short name for the group.  
Zkratka nebo krátký název skupiny.""",
        permission_classes=[OnlyForAuthentized]
    )
    
    @strawberry.field(
        description="""Indicates whether the group is currently active.  
Indikuje, zda je skupina aktuálně aktivní.""",
        permission_classes=[OnlyForAuthentized]
    )
    async def valid(self) -> typing.Optional[bool]:
        result = (self.enddate is None) or (datetime.datetime.now() < self.enddate)
        return result

    startdate: typing.Optional[datetime.datetime] = strawberry.field(
        description="""Start date of the group's activity.  
Datum zahájení aktivity skupiny.""",
        permission_classes=[OnlyForAuthentized]
    )

    enddate: typing.Optional[datetime.datetime] = strawberry.field(
        description="""End date of the group's activity (if applicable).  
Datum ukončení aktivity skupiny (je-li relevantní).""",
        permission_classes=[OnlyForAuthentized]
    )

    grouptype_id: typing.Optional[IDType] = strawberry.field(
        description="""Identifier for the group's type (e.g., Department).  
Identifikátor typu skupiny (např. oddělení).""",
        permission_classes=[OnlyForAuthentized]
    )

    grouptype: typing.Optional["GroupTypeGQLModel"] = strawberry.field(
        description="""The type of the group represented as an object (e.g., Department).  
Typ skupiny reprezentovaný jako objekt (např. oddělení).""",
        permission_classes=[OnlyForAuthentized],
        resolver=ScalarResolver["GroupTypeGQLModel"](fkey_field_name="grouptype_id")
    )

#     type_: typing.Optional["GroupTypeGQLModel"] = strawberry.field(
#         name="type",
#         description="""Alias for the group's type (e.g., Department).  
# Alias pro typ skupiny (např. oddělení).""",
#         permission_classes=[OnlyForAuthentized],
#         graphql_type=typing.Optional["GroupTypeGQLModel"],
#         resolver=ScalarResolver["GroupTypeGQLModel"](fkey_field_name="grouptype_id")
#     )

    # Pozor: V původním kódu se objevuje duplicitní pole `grouptype_id`.
    # Zvažte odstranění jednoho z nich, pokud není potřeba.
    grouptype_id: typing.Optional[IDType] = strawberry.field(
        description="""Identifier for the group's type.  
Identifikátor typu skupiny.""",
        permission_classes=[OnlyForAuthentized],
        graphql_type=typing.Optional[IDType]
    )

    subgroups: typing.List["GroupGQLModel"] = strawberry.field(
        description="""List of directly subordinate groups.  
Seznam přímo podřízených skupin.""",
        permission_classes=[OnlyForAuthentized],
        resolver=VectorResolver["GroupGQLModel"](fkey_field_name="mastergroup_id", whereType=GroupInputWhereFilter)
    )

    mastergroup_id: typing.Optional[IDType] = strawberry.field(
        description="""Identifier of the master (commanding) group.  
Identifikátor nadřazené (řídící) skupiny.""",
        permission_classes=[OnlyForAuthentized]
    )

    mastergroup: typing.Optional["GroupGQLModel"] = strawberry.field(
        description="""The master group that commands this group.  
Nadřazená skupina, která řídí tuto skupinu.""",
        permission_classes=[OnlyForAuthentized],
        resolver=ScalarResolver["GroupGQLModel"](fkey_field_name="mastergroup_id")
    )

    @strawberry.field(
        description="""Returns the hierarchy of master groups from the topmost to the immediate master.  
Vrací hierarchii nadřazených skupin od nejvyšší po bezprostředního nadřízeného.""",
        permission_classes=[OnlyForAuthentized]
    )
    async def mastergroups(self, info: strawberry.types.Info) -> typing.List["GroupGQLModel"]:
        path = self.path 
        ids = [] if path is None else path.split('/')[:-1]
        print(f"path {path}", flush=True)
        print(f"ids {ids}", flush=True)
        futures = [GroupGQLModel.load_with_loader(info=info, id=id) for id in ids]
        results = await asyncio.gather(*futures)
        # groups = [GroupGQLModel.from_dataclass(result) for result in results if result is not None]
        return results

    path: typing.Optional[str] = strawberry.field(
        description="""Materialized path representing the group's hierarchical location.  
Materializovaná cesta reprezentující umístění skupiny v hierarchii.""",
        permission_classes=[OnlyForAuthentized]
    )

    memberships: typing.List["MembershipGQLModel"] = strawberry.field(
        description="""List of membership records for users in this group.  
Seznam záznamů členství uživatelů v této skupině.""",
        permission_classes=[OnlyForAuthentized],
        resolver=VectorResolver["MembershipGQLModel"](fkey_field_name="group_id", whereType=MembershipInputWhereFilter)
    )
    
    roles: typing.List["RoleGQLModel"] = strawberry.field(
        description="""List of roles defined for the group.  
Seznam rolí definovaných pro tuto skupinu.""",
        permission_classes=[OnlyForAuthentized],
        resolver=VectorResolver["RoleGQLModel"](fkey_field_name="group_id", whereType=RoleInputWhereFilter)
    )

    @strawberry.field(
        description="""Aggregates roles along the group's hierarchical path.  
Agreguje role podél hierarchie skupiny.""",
        permission_classes=[OnlyForAuthentized]
    )
    async def roles_on(self, info: strawberry.types.Info) -> typing.List["RoleGQLModel"]:
        from .roleGQLModel import RoleGQLModel
        loader = RoleGQLModel.getLoader(info=info)
        path = self.path  # funguje jako materializovaná cesta ;)
        ids = [] if path is None else path.split('/')
        futures = (loader.filter_by(group_id=IDType(id)) for id in ids)
        dbrows = await asyncio.gather(*futures)
        index = {
            id: row for rr in dbrows for row in rr
        }
        result = [RoleGQLModel.from_dataclass(row) for row in index.values() if row.valid]
        return result

#####################################################################
#
# Special fields for query
#
#####################################################################


group_page: typing.List[GroupGQLModel] = strawberry.field(
    description="""## Description
Returns a list of groups in a paged format.
Vrací seznam skupin s stránkováním.

## Details
This query supports pagination parameters to efficiently handle large datasets.
Tento dotaz podporuje stránkovací parametry pro efektivní zpracování rozsáhlých dat.

## Permissions
- Only authenticated users (OnlyForAuthentized) can access this query.
- Pouze autentizovaní uživatelé mají přístup k tomuto dotazu.
""",
    permission_classes=[OnlyForAuthentized],
    graphql_type=List[GroupGQLModel],
    resolver=PageResolver[GroupGQLModel](whereType=GroupInputWhereFilter)
)

group_by_id: typing.Optional[GroupGQLModel] = strawberry.field(
    description="""## Description
Finds a group by its unique identifier.
Vyhledá skupinu podle jejího unikátního identifikátoru.

## Details
If the group is found, the corresponding group object is returned; otherwise, null is returned.
Pokud je skupina nalezena, vrátí se odpovídající objekt skupiny; v opačném případě null.

## Permissions
- Only authenticated users (OnlyForAuthentized) can perform this query.
- Pouze autentizovaní uživatelé mají přístup k tomuto dotazu.
""",
    permission_classes=[OnlyForAuthentized],
    graphql_type=Optional[GroupGQLModel],
    resolver=GroupGQLModel.load_with_loader
)

#####################################################################
#
# Mutation section
#
#####################################################################
import datetime

@strawberry.input(
    description="""## Description
Input model for updating a group.
Vstupní model pro aktualizaci skupiny.

## Fields
- **id**: Unique identifier of the group.
  Unikátní identifikátor skupiny.
- **lastchange**: Timestamp of the last modification.
  Časové razítko poslední změny.
- **name**: (Optional) Updated name of the group.
  (Volitelné) Aktualizovaný název skupiny.
- **name_en**: (Optional) Updated English name.
  (Volitelné) Aktualizovaný anglický název skupiny.
- **grouptype_id**: (Optional) Identifier for the new group type.
  (Volitelné) Identifikátor nového typu skupiny.
- **mastergroup_id**: (Optional) Identifier of the new master group.
  (Volitelné) Identifikátor nové nadřazené skupiny.
- **valid**: (Optional) Flag indicating if the group is active.
  (Volitelné) Příznak indikující, zda je skupina aktivní.
- **abbreviation**: (Optional) Abbreviation or short name.
  (Volitelné) Zkratka nebo krátký název.
- **email**: (Optional) Email address associated with the group.
  (Volitelné) Emailová adresa spojená se skupinou.
- **changedby_id**: (Private) Identifier of the user who made the change.
  (Interní) Identifikátor uživatele, který provedl změnu.
"""
)
class GroupUpdateGQLModel:
    id: "IDType" = strawberry.field(
         description="""Unique identifier of the group.
Unikátní identifikátor skupiny."""
    )
    lastchange: datetime.datetime = strawberry.field(
         description="""Timestamp of the last modification.
Časové razítko poslední změny."""
    )
    name: typing.Optional[str] = strawberry.field(
         description="""(Optional) Updated name of the group.
(Volitelné) Aktualizovaný název skupiny.""",
         default=None
    )
    name_en: typing.Optional[str] = strawberry.field(
         description="""(Optional) Updated English name of the group.
(Volitelné) Aktualizovaný anglický název skupiny.""",
         default=None
    )
    grouptype_id: typing.Optional["IDType"] = strawberry.field(
         description="""(Optional) Identifier for the new group type.
(Volitelné) Identifikátor nového typu skupiny.""",
         default=None
    )
    mastergroup_id: typing.Optional["IDType"] = strawberry.field(
         description="""(Optional) Identifier for the new master group.
(Volitelné) Identifikátor nové nadřazené skupiny.""",
         default=None
    )
    valid: typing.Optional[bool] = strawberry.field(
         description="""(Optional) Flag indicating if the group is active.
(Volitelné) Příznak indikující, zda je skupina aktivní.""",
         default=None
    )
    abbreviation: typing.Optional[str] = strawberry.field(
         description="""(Optional) Abbreviation or short name.
(Volitelné) Zkratka nebo krátký název.""",
         default=None
    )
    email: typing.Optional[str] = strawberry.field(
         description="""(Optional) Email address associated with the group.
(Volitelné) Emailová adresa spojená se skupinou.""",
         default=None
    )
    # Private pole – bez použití strawberry.field
    changedby_id: strawberry.Private["IDType"] = None


@strawberry.input(
    description="""## Description
Input model for inserting a new group.
Vstupní model pro vložení nové skupiny.

## Fields
- **name**: Name of the new group.
  Název nové skupiny.
- **grouptype_id**: Identifier for the group's type.
  Identifikátor typu skupiny.
- **id**: (Optional) Primary key of the group. If not provided, a new unique identifier will be generated.
  (Volitelné) Primární klíč skupiny. Pokud není zadán, bude vygenerován nový unikátní identifikátor.
- **name_en**: (Optional) English name of the group.
  (Volitelné) Anglický název skupiny.
- **mastergroup_id**: (Optional) Identifier for the master group.
  (Volitelné) Identifikátor nadřazené skupiny.
- **valid**: (Optional) Validity flag of the group.
  (Volitelné) Příznak platnosti skupiny.
- **abbreviation**: (Optional) Abbreviation of the group.
  (Volitelné) Zkratka skupiny.
- **email**: (Optional) Email address of the group.
  (Volitelné) Emailová adresa skupiny.
- **path**: (Private) Materialized path in the group hierarchy.
  (Interní) Materializovaná cesta v hierarchii skupin.
- **createdby_id**: (Private) Identifier of the creator.
  (Interní) Identifikátor tvůrce.
- **rbacobject**: (Private) RBAC-related identifier.
  (Interní) Identifikátor pro RBAC.
"""
)
class GroupInsertGQLModel:
    name: str = strawberry.field(
         description="""Name of the new group.
Název nové skupiny."""
    )
    grouptype_id: "IDType" = strawberry.field(
         description="""Identifier for the group's type.
Identifikátor typu skupiny."""
    )
    id: typing.Optional["IDType"] = strawberry.field(
         description="""Primary key of the group.
Primární klíč skupiny. If not provided, a new unique identifier will be generated.
Pokud není zadán, bude vygenerován nový unikátní identifikátor.""",
         default=None
    )
    name_en: typing.Optional[str] = strawberry.field(
         description="""(Optional) English name of the group.
(Volitelné) Anglický název skupiny.""",
         default=None
    )
    mastergroup_id: typing.Optional["IDType"] = strawberry.field(
         description="""(Optional) Identifier for the master group.
(Volitelné) Identifikátor nadřazené skupiny.""",
         default=None
    )
    valid: typing.Optional[bool] = strawberry.field(
         description="""(Optional) Validity flag of the group.
(Volitelné) Příznak platnosti skupiny.""",
         default=None
    )
    abbreviation: typing.Optional[str] = strawberry.field(
         description="""(Optional) Abbreviation of the group.
(Volitelné) Zkratka skupiny.""",
         default=None
    )
    email: typing.Optional[str] = strawberry.field(
         description="""(Optional) Email address of the group.
(Volitelné) Emailová adresa skupiny.""",
         default=None
    )
    # Private pole – bez použití strawberry.field
    path: strawberry.Private[str] = ""
    createdby_id: strawberry.Private["IDType"] = None
    rbacobject: strawberry.Private["IDType"] = None

@strawberry.input(
    description="""## Description
Input model for deleting a group.
Vstupní model pro smazání skupiny.

## Fields
- **id**: Unique identifier of the group.
  Unikátní identifikátor skupiny.
- **lastchange**: Timestamp of the last change, used for concurrency control.
  Časové razítko poslední změny, používané pro kontrolu konzistence.
"""
)
class GroupDeleteGQLModel:
    id: "IDType" = strawberry.field(
         description="""Unique identifier of the group.
Unikátní identifikátor skupiny."""
    )
    lastchange: datetime.datetime = strawberry.field(
         description="""Timestamp of the last change, used for concurrency control.
Časové razítko poslední změny, používané pro kontrolu konzistence."""
    )


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
        roleTypeName = role["roletype"]["name"]
        if roleTypeName in allowedRoleNames:
            if group.mastergroup_id:
                raise self.error_class(f"{roleTypeName} cannot change mastergroup_id")
            if group.grouptype_id:
                raise self.error_class(f"{roleTypeName} cannot change grouptype_id")
        return True

@strawberry.mutation(
    description="""## Description
Allows updating a group, including changing its master group.
Umožňuje aktualizaci skupiny, včetně změny nadřazené skupiny.

## Details
Performs safe update operations ensuring data consistency.
Provádí bezpečné aktualizační operace zajišťující konzistenci dat.

## Permissions
- Only authenticated users (e.g. OnlyForAuthentized) with proper RBAC permissions can perform this mutation.
- The user must satisfy the conditions defined by UpdateGroupPermission.
"""
)
async def group_update(self, info: strawberry.types.Info, group: GroupUpdateGQLModel) -> typing.Union["GroupGQLModel", UpdateError[GroupGQLModel]]:
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
        return result

@strawberry.mutation(
    description="""## Description
Allows inserting a new group.
Umožňuje vložení nové skupiny.

## Details
Handles the creation logic, including setting up the hierarchical path for the group.
Řeší logiku vytvoření, včetně nastavení hierarchické cesty pro skupinu.

## Permissions
- Only authenticated users (e.g. OnlyForAuthentized) with proper RBAC permissions can perform this mutation.
- The user must satisfy the conditions defined by InsertGroupPermission.
"""
)
async def group_insert(self, info: strawberry.types.Info, group: GroupInsertGQLModel) -> typing.Union["GroupGQLModel", InsertError["GroupGQLModel"]]:
    group.rbacobject = group.id
    if group.mastergroup_id is not None:
        loader = GroupGQLModel.getLoader(info=info)
        master = await loader.load(group.mastergroup_id)
    group.path = f"{group.id}" if group.mastergroup_id is None else f"{master.path}/{group.id}"
    result = await Insert[GroupGQLModel].DoItSafeWay(info=info, entity=group)
    return result


@strawberry.mutation(
    description="""## Description
Deletes a group.
Maže skupinu.

## Details
This operation removes the group entity from the system.
Tato operace odstraní entitu skupiny ze systému.

## Permissions
- Only authenticated users with administrative rights (e.g. OnlyForAdmins) can perform this mutation.
- The operation is restricted to administrators.
"""
)
async def group_delete(self, info: strawberry.types.Info, group: GroupDeleteGQLModel) -> typing.Optional[DeleteError[GroupGQLModel]]:
    result = await Delete[GroupGQLModel].DoItSafeWay(info=info, entity=group)
    return result