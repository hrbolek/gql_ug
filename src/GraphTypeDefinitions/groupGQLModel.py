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

from uoishelpers.gqlpermissions.LoadDataExtension import LoadDataExtension
from uoishelpers.gqlpermissions.RbacProviderExtension import RbacProviderExtension
from uoishelpers.gqlpermissions.RbacInsertProviderExtension import RbacInsertProviderExtension
from uoishelpers.gqlpermissions.UserRoleProviderExtension import UserRoleProviderExtension
from uoishelpers.gqlpermissions.UserAccessControlExtension import UserAccessControlExtension
from uoishelpers.gqlpermissions.UserAbsoluteAccessControlExtension import UserAbsoluteAccessControlExtension

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


from uoishelpers.resolvers import createInputs, createInputs2
from dataclasses import dataclass
# MembershipInputWhereFilter = Annotated["MembershipInputWhereFilter", strawberry.lazy(".membershipGQLModel")]
@createInputs2
class GroupInputWhereFilter:
    id: IDType
    name: str
    name_en: str
    valid: bool
    startdate: datetime.datetime
    enddate: datetime.datetime
    from .groupTypeGQLModel import GroupTypeInputWhereFilter
    grouptype: GroupTypeInputWhereFilter
    from .roleGQLModel import RoleInputWhereFilter
    roles: RoleInputWhereFilter
    mastergroup_id: IDType
    grouptype_id: IDType

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
        loader = getLoader(info).GroupModel
        return loader

    email: typing.Optional[str] = strawberry.field(
        description="""Group's email address.  
Emailová adresa skupiny.""",
        default=None,
        permission_classes=[OnlyForAuthentized]
    )
    
    abbreviation: typing.Optional[str] = strawberry.field(
        description="""Abbreviation or short name for the group.  
Zkratka nebo krátký název skupiny.""",
        default=None,
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
        default=None,
        permission_classes=[OnlyForAuthentized]
    )

    enddate: typing.Optional[datetime.datetime] = strawberry.field(
        description="""End date of the group's activity (if applicable).  
Datum ukončení aktivity skupiny (je-li relevantní).""",
        default=None,
        permission_classes=[OnlyForAuthentized]
    )

    grouptype_id: typing.Optional[IDType] = strawberry.field(
        description="""Identifier for the group's type (e.g., Department).  
Identifikátor typu skupiny (např. oddělení).""",
        default=None,
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
        default=None,
        permission_classes=[OnlyForAuthentized]
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
        default=None,
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
        default=None,
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
            row.id: row for rr in dbrows for row in rr
        }
        result = [RoleGQLModel.from_dataclass(row) for row in index.values() if row.valid]
        return result

#####################################################################
#
# Special fields for query
#
#####################################################################

@strawberry.interface(description="Base interface for group queries")
class GroupQueries:
    
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

    # @strawberry.field(
    #     extensions=[
    #         UserRoleProviderExtension[UpdateError, GroupGQLModel](),
    #         RbacProviderExtension[UpdateError, GroupGQLModel](),
    #         LoadDataExtension[UpdateError, GroupGQLModel]()
    #     ]
    # )
    # async def group_by_id2(
    #     self, 
    #     info: strawberry.types.Info, 
    #     id: IDType, 
    #     db_row: typing.Any,
    #     rbacobject_id: IDType,
    #     user_roles: typing.List[typing.Any]
    # ) -> typing.Union[UpdateError[GroupGQLModel], GroupGQLModel]:
    #     print(f"group_by_id2 {user_roles}")
    #     result = GroupGQLModel.from_dataclass(db_row)
    #     return result

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




from uoishelpers.resolvers import InputModelMixin, TreeInputStructureMixin

@strawberry.input(
    description="""Input model for inserting a new group."""
)
class GroupInsertGQLModel(TreeInputStructureMixin):
    getLoader = GroupGQLModel.getLoader
    name: str = strawberry.field(
         description="""Name of the new group."""
    )
    grouptype_id: IDType = strawberry.field(
         description="""Identifier for the group's type."""
    )
    id: typing.Optional[IDType] = strawberry.field(
         description="""Primary key of the group. If not provided, a new unique identifier will be generated.""",
         default=None
    )
    name_en: typing.Optional[str] = strawberry.field(
         description="""(Optional) English name of the group.""",
         default=None
    )
    
    abbreviation: typing.Optional[str] = strawberry.field(
         description="""(Optional) Abbreviation of the group.""",
         default=None
    )
    email: typing.Optional[str] = strawberry.field(
         description="""(Optional) Email address of the group.""",
         default=None
    )

    subgroups: typing.Optional[typing.List["GroupInsertSubGroupGQLModel"]] = strawberry.field(
        description="""podskupiny, které budou vytvořeny jako podřízené této skupině.""",
        default_factory=list
    )

    from .membershipGQLModel import MembershipInsertGQLModel
    memberships: typing.Optional[typing.List[MembershipInsertGQLModel]] = strawberry.field(
        description="""členství, která budou vytvořena pro tuto skupinu""",
        default_factory=list
    )
    from .roleGQLModel import RoleInsertGQLModel
    roles: Optional[List[RoleInsertGQLModel]] = strawberry.field(
        description="List of roles assigned to the user\nSeznam rolí přiřazených uživateli",
        default_factory=list
    )

    # Private pole – bez použití strawberry.field
    path: strawberry.Private[str] = ""
    createdby_id: strawberry.Private["IDType"] = None
    rbacobject: strawberry.Private["IDType"] = None
    mastergroup_id: strawberry.Private["IDType"] = None


@strawberry.input(
    description="""Input model for inserting a new group."""
)
class RbacFreeInsertGQLModel(TreeInputStructureMixin):
    getLoader = GroupGQLModel.getLoader
    grouptype_id: IDType = strawberry.field(
         description="""Identifier for the group's type."""
    )
    id: IDType = strawberry.field(
         description="""Primary key of the group.""",
    )
    from .membershipGQLModel import MembershipInsertGQLModel
    memberships: typing.Optional[typing.List[MembershipInsertGQLModel]] = strawberry.field(
        description="""členství, která budou vytvořena pro tuto skupinu""",
        default_factory=list
    )
    from .roleGQLModel import RoleInsertGQLModel
    roles: Optional[List[RoleInsertGQLModel]] = strawberry.field(
        description="List of roles assigned to the user\nSeznam rolí přiřazených uživateli",
        default_factory=list
    )

    # Private pole – bez použití strawberry.field
    path: strawberry.Private[str] = ""
    name: strawberry.Private[str] = "rbacobject"
    name_en: strawberry.Private[str] = "rbacobject"
    abbreviation: strawberry.Private[str] = "rbac"
    email: strawberry.Private[str] = None
    startdate: strawberry.Private[datetime.datetime] = None
    enddate: strawberry.Private[datetime.datetime] = None
    createdby_id: strawberry.Private["IDType"] = None
    rbacobject_id: strawberry.Private["IDType"] = None
    mastergroup_id: strawberry.Private["IDType"] = None    

@strawberry.input(
    description="""Input model for inserting a new group."""
)
class GroupInsertSubGroupGQLModel(TreeInputStructureMixin):
    getLoader = GroupGQLModel.getLoader
    mastergroup_id: IDType = strawberry.field(
         description="""Identifier for the master group.""",
         default=None
    )
    name: str = strawberry.field(
         description="""Name of the new group."""
    )
    grouptype_id: IDType = strawberry.field(
         description="""Identifier for the group's type."""
    )
    id: typing.Optional[IDType] = strawberry.field(
         description="""Primary key of the group. If not provided, a new unique identifier will be generated.""",
         default=None
    )
    name_en: typing.Optional[str] = strawberry.field(
         description="""(Optional) English name of the group.""",
         default=None
    )
    
    abbreviation: typing.Optional[str] = strawberry.field(
         description="""(Optional) Abbreviation of the group.""",
         default=None
    )
    email: typing.Optional[str] = strawberry.field(
         description="""(Optional) Email address of the group.""",
         default=None
    )

    subgroups: typing.Optional[typing.List["GroupInsertSubGroupGQLModel"]] = strawberry.field(
        description="""podskupiny, které budou vytvořeny jako podřízené této skupině.""",
        default_factory=list
    )

    from .membershipGQLModel import MembershipInsertGQLModel
    memberships: typing.Optional[typing.List[MembershipInsertGQLModel]] = strawberry.field(
        description="""členství, která budou vytvořena pro tuto skupinu""",
        default_factory=list
    )
    from .roleGQLModel import RoleInsertGQLModel
    roles: Optional[List[RoleInsertGQLModel]] = strawberry.field(
        description="List of roles assigned to the user\nSeznam rolí přiřazených uživateli",
        default_factory=list
    )

    # Private pole – bez použití strawberry.field
    path: strawberry.Private[str] = ""
    createdby_id: strawberry.Private["IDType"] = None
    rbacobject: strawberry.Private["IDType"] = None    



@strawberry.input(
    description="""Input model for splitting the group."""
)
class GroupSplitGQLModel(TreeInputStructureMixin):
    getLoader = GroupGQLModel.getLoader
    id: IDType = strawberry.field(
         description="""Primary key of the group.""",
         default=None
    )
    subgroups: typing.List["GroupInsertGQLModel"] = strawberry.field(
        description="""""",
        default_factory=list
    )

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

# b9fdbc41-c6d4-4bde-a88a-46d7bba84826

   
# from uoishelpers.gqlpermissions.InsertPermissionCheckRoleFieldExtension import InsertPermissionCheckRoleFieldExtension
# from uoishelpers.gqlpermissions.UpdatePermissionCheckRoleFieldExtension import UpdatePermissionCheckRoleFieldExtension

# class UpdateGroupPermission(RBACPermission):
#     message = "User is not allowed to create a new group"
#     async def has_permission(self, source, info: strawberry.types.Info, group: GroupInsertGQLModel) -> bool:
#         adminRoleNames = ["administrátor"]
#         allowedRoleNames = ["garant"]
#         role = await self.resolveUserRole(info, 
#             rbacobject=group.id, 
#             adminRoleNames=adminRoleNames, 
#             allowedRoleNames=allowedRoleNames)
        
#         if not role: return False
#         roleTypeName = role["roletype"]["name"]
#         if roleTypeName in allowedRoleNames:
#             if group.mastergroup_id:
#                 raise self.error_class(f"{roleTypeName} cannot change mastergroup_id")
#             if group.grouptype_id:
#                 raise self.error_class(f"{roleTypeName} cannot change grouptype_id")
#         return True

# class InsertGroupPermission(RBACPermission):
#     message = "User is not allowed to create a new group"
#     async def has_permission(self, source, info: strawberry.types.Info, group: GroupInsertGQLModel) -> bool:
#         adminRoleNames = ["administrátor"]
#         allowedRolesNames = ["garant"]
#         result = await self.resolveUserRole(info, 
#             rbacobject=group.mastergroup_id, 
#             adminRoleNames=adminRoleNames, 
#             allowedRoleNames=allowedRolesNames)
#         if result is None:
#             user = getUserFromInfo(info)
#             logging.info(f"user {user} has no right to insert new group {group}")
#             print(f"user {user} has no right to insert new group {group}")
#         return result

@strawberry.interface(description="Base interface for group mutations")
class GroupMutations:

    @strawberry.mutation(
        description="Upravi rbacobject_ids",
        extensions=[
            UserAbsoluteAccessControlExtension[UpdateError, GroupGQLModel](roles=["superadmin"]),
        ],
    )
    async def group_update_rbacobject_ids(self, info: strawberry.types.Info, group: GroupUpdateGQLModel) -> typing.Union[GroupGQLModel, UpdateError[GroupGQLModel]]:
        group_loader = GroupGQLModel.getLoader(info=info)
        group_row = await group_loader.load(group.id)
        # TODO implmentace updates
        return GroupGQLModel.from_dataclass(group_row) if group_row is not None else None

    @strawberry.mutation(
        description="Insertion of multiple subgroups",
        extensions=[
            # UpdatePermissionCheckRoleFieldExtension[GroupGQLModel](roles=["administrátor", "personalista"]),
            UserAccessControlExtension[UpdateError, GroupGQLModel](roles=["administrátor", "personalista"]),
            UserRoleProviderExtension[UpdateError, GroupGQLModel](),
            RbacProviderExtension[UpdateError, GroupGQLModel](),
            LoadDataExtension[UpdateError, GroupGQLModel]()
        ],
    )
    async def group_insert_subgroups(
        self, 
        info: strawberry.types.Info, 
        group: GroupSplitGQLModel,
        user_roles: typing.List[dict],
        rbacobject_id: IDType,
        db_row: typing.Any
    ) -> typing.Union[GroupGQLModel, UpdateError[GroupGQLModel]]:
        group_loader = GroupGQLModel.getLoader(info=info)
        group_row = await group_loader.load(group.id)
        group_model = group.intoModel(info)
        for subgroup in group_model.subgroups:
            subgroup.mastergroup_id = group_row.id
            subgroup.rbacobject = group_row.rbacobject
            subgroup.createdby_id = group_row.createdby_id
            subgroup.path = f"{group_row.path}/{subgroup.id}" if group_row.path else f"{subgroup.id}"
            session = info.context.get("session", None)
            session.add(subgroup)
        # TODO implmentace updates
        return GroupGQLModel.from_dataclass(group_row) if group_row is not None else None
    
    @strawberry.mutation(
        description="Splits a group into subgroups. All memberships of the original group must be converted into new subgroups.",
        extensions=[
            # InsertPermissionCheckRoleFieldExtension[GroupGQLModel](roles=["administrátor", "garant", "garant předmětu"]),
            UserAccessControlExtension[InsertError, GroupGQLModel](roles=["administrátor", "garant", "garant předmětu"]),
            UserRoleProviderExtension[InsertError, GroupGQLModel](),
            RbacProviderExtension[InsertError, GroupGQLModel](),
            LoadDataExtension[InsertError, GroupGQLModel]()
        ],
    )
    async def group_split(
        self, 
        info: strawberry.types.Info, 
        group: GroupSplitGQLModel,
        user_roles: typing.List[dict],
        rbacobject_id: IDType,
        db_row: typing.Any
    ) -> typing.Union[GroupGQLModel, InsertError[GroupGQLModel]]:
        print(f"group_split context: {info.context}", flush=True)
        if not group.subgroups:
            error_description = {
                "code": "0098aa36-becf-40f2-9aa6-ff1f06652eca", 
                "msg": "No subgroups provided for splitting", 
                "_input": group
            }
            info.context["error"] = error_description        
            return InsertError[GroupGQLModel](**error_description)
        
        # group_loader = GroupGQLModel.getLoader(info=info)
        group_row = db_row

        from .groupTypeGQLModel import GroupTypeGQLModel
        group_type_loader = GroupTypeGQLModel.getLoader(info=info)
        group_type_row = await group_type_loader.load(group_row.grouptype_id)
        # TODO typy vytvareni velke stromove struktury, podminku odvodit od podstromu
        if "cd49e157-610c-11ed-9312-001a7dda7110" not in group_type_row.path:
            error_description = {
                "code": "f0b1c8d2-3c4e-4b5a-9f6d-7e8f9a0b1c2d", 
                "msg": "Group type is not allowed for splitting", 
                "_input": group
            }
            info.context["error"] = error_description
            return InsertError[GroupGQLModel](**error_description)
        
        result = GroupGQLModel.from_dataclass(group_row) if group_row is not None else None

        from .membershipGQLModel import MembershipGQLModel
        membership_loader = MembershipGQLModel.getLoader(info=info)
        membership_rows = await membership_loader.filter_by(group_id=group.id)
        current_user_ids = {membership.user_id for membership in membership_rows}
        defined_user_ids = {membership.user_id for g in group.subgroups for membership in g.memberships}
        if current_user_ids != defined_user_ids:
            error_description = {
                "code": "4ac362b7-248d-4662-9ac2-e6f55be17304", 
                "msg": "Memberships in subgroups do not match the current group memberships", 
                "_input": group
            }
            info.context["error"] = error_description
            return InsertError[GroupGQLModel](**error_description)

        # konverze na modely
        group.subgroups = [group.intoModel(info) for group in group.subgroups]
        session = info.context.get("session", None)
        for subgroup in group.subgroups:
            subgroup.mastergroup_id = group_row.id
            session.add(subgroup)        
        # raise 
        return result
    
    @strawberry.mutation(
        description="""Allows updating a group, including changing its master group.""",
        extensions=[
            UserAccessControlExtension[UpdateError, GroupGQLModel](roles=["administrátor", "personalista"]),
            UserRoleProviderExtension[UpdateError, GroupGQLModel](),
            RbacProviderExtension[UpdateError, GroupGQLModel](),
            LoadDataExtension[UpdateError, GroupGQLModel]()
        ]
    )
    async def group_update(
        self, 
        info: strawberry.types.Info, 
        group: GroupUpdateGQLModel,
        user_roles: typing.List[dict],
        rbacobject_id: IDType,
        db_row: typing.Any
    ) -> typing.Union["GroupGQLModel", UpdateError[GroupGQLModel]]:
        result = await Update[GroupGQLModel].DoItSafeWay(info=info, entity=group)
        return result

    @strawberry.mutation(
        description="""Allows inserting a new group, including setting up the hierarchical path for the group.""",
        extensions=[
            UserAccessControlExtension[InsertError, GroupGQLModel](roles=["administrátor", "personalista"]),
            UserRoleProviderExtension[InsertError, GroupGQLModel](),
            RbacProviderExtension[InsertError, GroupGQLModel](),
            LoadDataExtension[InsertError, GroupGQLModel](primary_key_name="mastergroup_id")
        ]
    )
    async def group_insert(
        self, 
        info: strawberry.types.Info, 
        group: GroupInsertSubGroupGQLModel,
        user_roles: typing.List[dict],
        rbacobject_id: IDType,
        db_row: typing.Any
    ) -> typing.Union["GroupGQLModel", InsertError["GroupGQLModel"]]:
        group.rbacobject = group.id
        if group.mastergroup_id is not None:
            master = db_row
        group.path = f"{group.id}" if group.mastergroup_id is None else f"{master.path}/{group.id}"
        result = await Insert[GroupGQLModel].DoItSafeWay(info=info, entity=group)
        return result


    @strawberry.mutation(
        description="""Inserts new group without master group.""",
        extensions=[
            UserAccessControlExtension[InsertError, GroupGQLModel](roles=["administrátor"]),
            UserRoleProviderExtension[InsertError, GroupGQLModel](),
            RbacProviderExtension[InsertError, GroupGQLModel](),
            LoadDataExtension[InsertError, GroupGQLModel](primary_key_name="mastergroup_id")
        ]
    )
    async def group_insert_top_group(
        self, 
        info: strawberry.types.Info, 
        group: GroupInsertGQLModel,
        user_roles: typing.List[dict],
        rbacobject_id: IDType,
        db_row: typing.Any
    ) -> typing.Union["GroupGQLModel", InsertError["GroupGQLModel"]]:
        group.rbacobject = group.id
        group.path = f"{group.id}"
        result = await Insert[GroupGQLModel].DoItSafeWay(info=info, entity=group)
        return result

    @strawberry.mutation(
        description="""Inserts a new rbacobject out of structure represented by a group.""",
        extensions=[
            # UserAccessControlExtension[InsertError, GroupGQLModel](
            #     roles=["administrátor"]
            # ),
            UserRoleProviderExtension[InsertError, GroupGQLModel](),
            RbacInsertProviderExtension[InsertError, GroupGQLModel](
                rbac_key_name="id"
            ),
            # RbacProviderExtension[InsertError, GroupGQLModel](),
            # LoadDataExtension[InsertError, GroupGQLModel](primary_key_name="mastergroup_id")
        ]
    )
    async def rbac_object_insert(
        self, 
        info: strawberry.types.Info, 
        rbacobject: RbacFreeInsertGQLModel,
        user_roles: typing.List[dict],
        rbacobject_id: IDType,
        # db_row: typing.Any
    ) -> typing.Union["GroupGQLModel", InsertError["GroupGQLModel"]]:
        rbacobject.rbacobject_id = rbacobject.id
        print(f"rbac_object_insert\n{rbacobject}\n{strawberry.asdict(rbacobject)}")
        result = await Insert[GroupGQLModel].DoItSafeWay(info=info, entity=rbacobject)
        return result

    @strawberry.mutation(
        description="""Deletes a group""",
        extensions=[
            UserAccessControlExtension[DeleteError, GroupGQLModel](roles=["administrátor", "personalista"]),
            UserRoleProviderExtension[DeleteError, GroupGQLModel](),
            RbacProviderExtension[DeleteError, GroupGQLModel](),
            LoadDataExtension[DeleteError, GroupGQLModel]()
        ]
    )
    async def group_delete(
        self, 
        info: strawberry.types.Info, 
        group: GroupDeleteGQLModel,
        user_roles: typing.List[dict],
        rbacobject_id: IDType,
        db_row: typing.Any
    ) -> typing.Optional[DeleteError[GroupGQLModel]]:
        result = await Delete[GroupGQLModel].DoItSafeWay(info=info, entity=group)
        return result
    
# 0185a46d-42f9-4175-b7c9-99e8dad78af5