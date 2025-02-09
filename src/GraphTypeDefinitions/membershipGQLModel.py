import dataclasses
import typing
import datetime
import strawberry
import uuid
from typing import List, Optional, Union, Annotated, Type
from uoishelpers.resolvers import createInputs

from .BaseGQLModel import BaseGQLModel, IDType
from ._GraphPermissions import (
    RoleBasedPermission, OnlyForAuthentized,
    OnlyForAdmins,
    RBACPermission
)
from ._GraphResolvers import (
    resolve_field,
    default_resolver,
    default_scalar_resolver,
    default_page_resolver,
    default_by_id_resolver,
    
    encapsulateInsert,
    encapsulateUpdate,
    encapsulateDelete,

    remove_constructor

)

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

from src.Dataloaders import (
    getLoadersFromInfo as getLoader,
    getUserFromInfo)
from src.DBResolvers import DBResolvers

GroupGQLModel = Annotated["GroupGQLModel", strawberry.lazy(".groupGQLModel")]
UserGQLModel = Annotated["UserGQLModel", strawberry.lazy(".userGQLModel")]

@strawberry.federation.type(
    keys=["id"],
    description="""## Description
Entity representing a relation between a user and a group.
Entita reprezentující vztah mezi uživatelem a skupinou.

## Details
This type defines the membership of a user in a group, including references to both the user and the group, as well as details on membership validity and effective dates.
Tento typ definuje členství uživatele ve skupině, včetně odkazů na uživatele a skupinu, platnosti členství a časových údajů.
"""
)
class MembershipGQLModel(BaseGQLModel):
    @classmethod
    def getLoader(cls, info):
        return getLoader(info).MembershipModel

    @classmethod
    def from_dataclass(cls, db_row):
        db_row_dict = dataclasses.asdict(db_row)
        db_row_dict["valid"] = db_row.valid
        instance = cls(**db_row_dict)
        return instance

    user_id: typing.Optional[IDType] = strawberry.field(
        description="""ID of associated user.
ID spojeného uživatele.""",
        permission_classes=[OnlyForAuthentized]
    )

    group_id: typing.Optional[IDType] = strawberry.field(
        description="""ID of associated group.
ID spojené skupiny.""",
        permission_classes=[OnlyForAuthentized]
    )

    user = strawberry.field(
        description="""User object associated with the membership.
Objekt uživatele spojený s členstvím.""",
        permission_classes=[OnlyForAuthentized],
        graphql_type=Optional[UserGQLModel],
        resolver=default_scalar_resolver(fkey_field_name="user_id")
    )

    group = strawberry.field(
        description="""Group object associated with the membership.
Objekt skupiny spojený s členstvím.""",
        permission_classes=[OnlyForAuthentized],
        graphql_type=Optional[GroupGQLModel],
        resolver=default_scalar_resolver(fkey_field_name="group_id")
    )

    valid: Optional[bool] = strawberry.field(
        description="""Indicates whether the membership is valid.
Indikuje, zda je členství platné.""",
        permission_classes=[OnlyForAuthentized]
    )

    startdate: Optional[datetime.datetime] = strawberry.field(
        description="""Date when the membership begins.
Datum začátku členství.""",
        permission_classes=[OnlyForAuthentized]
    )

    enddate: Optional[datetime.datetime] = strawberry.field(
        description="""Date when the membership ends.
Datum ukončení členství.""",
        permission_classes=[OnlyForAuthentized]
    )

    RBACObjectGQLModel = Annotated["RBACObjectGQLModel", strawberry.lazy(".RBACObjectGQLModel")]

    @strawberry.field(
        description="""Returns the RBAC object associated with this membership.
Vrací RBAC objekt spojený s tímto členstvím.""",
        permission_classes=[OnlyForAuthentized]
    )
    async def rbacobject(self, info: strawberry.types.Info) -> Optional[RBACObjectGQLModel]:
        from .RBACObjectGQLModel import RBACObjectGQLModel
        group_id = resolve_field(self=self, field_name="group_id")
        result = await RBACObjectGQLModel.resolve_reference(info=info, id=group_id)
        return result 

#####################################################################
#
# Special fields for query
#
#####################################################################
from uoishelpers.resolvers import createInputs
from dataclasses import dataclass
GroupInputWhereFilter = Annotated["GroupInputWhereFilter", strawberry.lazy(".groupGQLModel")]
UserInputWhereFilter = Annotated["UserInputWhereFilter", strawberry.lazy(".userGQLModel")]
@createInputs
@dataclass
class MembershipInputWhereFilter:
    valid: bool
    # from .userGQLModel import UserInputWhereFilter
    # from .groupGQLModel import GroupInputWhereFilter
    group: GroupInputWhereFilter
    user: UserInputWhereFilter

# from ._GraphResolvers import asPage

membership_page = strawberry.field(
    description="""## Description
Retrieves memberships in a paged format.
Vrací členství ve stránkovaném formátu.

## Details
This query returns a list of membership records. Pagination parameters can be applied to efficiently navigate large datasets.
Tento dotaz vrací seznam záznamů členství. Pro efektivní práci s rozsáhlými datovými sadami je podporováno stránkování.

## Permissions
- Only authenticated users (OnlyForAuthentized) can execute this query.
- Pouze autentizovaní uživatelé mají oprávnění tento dotaz spustit.
""",
    permission_classes=[OnlyForAuthentized],
    graphql_type=List[MembershipGQLModel],
    resolver=PageResolver[MembershipGQLModel](whereType=MembershipInputWhereFilter)
)

membership_by_id = strawberry.field(
    description="""## Description
Retrieves a specific membership by its unique identifier.
Vyhledá konkrétní členství podle jeho unikátního identifikátoru.

## Details
If the membership is found, the corresponding membership record is returned; otherwise, null is returned.
Pokud je členství nalezeno, vrací se odpovídající záznam; v opačném případě se vrací null.

## Permissions
- Only authenticated users (OnlyForAuthentized) can perform this query.
- Pouze autentizovaní uživatelé mají přístup k tomuto dotazu.
""",
    permission_classes=[OnlyForAuthentized],
    graphql_type=Optional[MembershipGQLModel],
    resolver=MembershipGQLModel.load_with_loader
)

#####################################################################
#
# Mutation section
#
#####################################################################
import datetime

@strawberry.input(
    description="""## Description
Input model for inserting a new membership.
Vstupní model pro vložení nového členství.

## Fields
- **user_id**: Unique identifier of the user.
  Unikátní identifikátor uživatele.
- **group_id**: Unique identifier of the group.
  Unikátní identifikátor skupiny.
- **id**: (Optional) Primary key of the membership entity. If not provided, a new unique identifier will be generated.
  (Volitelné) Primární klíč entity členství. Pokud není zadán, bude vygenerován nový unikátní identifikátor.
- **valid**: (Optional) Flag indicating if the membership is valid.
  (Volitelné) Příznak platnosti členství.
- **startdate**: (Optional) Date when the membership starts.
  (Volitelné) Datum začátku členství.
- **enddate**: (Optional) Date when the membership ends.
  (Volitelné) Datum ukončení členství.
- **createdby_id**: (Private) Identifier of the user who created the membership.
  (Interní) Identifikátor uživatele, který vytvořil členství.
"""
)
class MembershipInsertGQLModel:
    user_id: "IDType" = strawberry.field(
         description="""Unique identifier of the user.
Unikátní identifikátor uživatele."""
    )
    group_id: "IDType" = strawberry.field(
         description="""Unique identifier of the group.
Unikátní identifikátor skupiny."""
    )
    id: typing.Optional["IDType"] = strawberry.field(
         description="""Primary key of the membership entity.
Primární klíč entity členství. If not provided, a new unique identifier will be generated.
Pokud není zadán, bude vygenerován nový unikátní identifikátor.""",
         default=None
    )
    valid: typing.Optional[bool] = strawberry.field(
         description="""(Optional) Flag indicating if the membership is valid.
(Volitelné) Příznak platnosti členství.""",
         default=True
    )
    startdate: typing.Optional[datetime.datetime] = strawberry.field(
         description="""(Optional) Date when the membership starts.
(Volitelné) Datum začátku členství.""",
         default=None
    )
    enddate: typing.Optional[datetime.datetime] = strawberry.field(
         description="""(Optional) Date when the membership ends.
(Volitelné) Datum ukončení členství.""",
         default=None
    )
    # Private pole – nejsou zahrnuta do SDL
    createdby_id: strawberry.Private["IDType"] = None


@strawberry.input(
    description="""## Description
Input model for updating an existing membership.
Vstupní model pro aktualizaci existujícího členství.

## Fields
- **id**: Unique identifier of the membership.
  Unikátní identifikátor členství.
- **lastchange**: Timestamp of the last modification for concurrency control.
  Časové razítko poslední změny, sloužící k řízení konzistence.
- **valid**: (Optional) Flag indicating if the membership is valid.
  (Volitelné) Příznak platnosti členství.
- **startdate**: (Optional) Updated date when the membership starts.
  (Volitelné) Aktualizované datum začátku členství.
- **enddate**: (Optional) Updated date when the membership ends.
  (Volitelné) Aktualizované datum ukončení členství.
- **changedby_id**: (Private) Identifier of the user who made the change.
  (Interní) Identifikátor uživatele, který provedl změnu.
- **group_id**: (Private) Identifier for the group, if changed.
  (Interní) Identifikátor skupiny, pokud došlo ke změně.
"""
)
class MembershipUpdateGQLModel:
    id: "IDType" = strawberry.field(
         description="""Unique identifier of the membership.
Unikátní identifikátor členství."""
    )
    lastchange: datetime.datetime = strawberry.field(
         description="""Timestamp of the last modification for concurrency control.
Časové razítko poslední změny, sloužící k řízení konzistence."""
    )
    valid: typing.Optional[bool] = strawberry.field(
         description="""(Optional) Flag indicating if the membership is valid.
(Volitelné) Příznak platnosti členství.""",
         default=None
    )
    startdate: typing.Optional[datetime.datetime] = strawberry.field(
         description="""(Optional) Updated date when the membership starts.
(Volitelné) Aktualizované datum začátku členství.""",
         default=None
    )
    enddate: typing.Optional[datetime.datetime] = strawberry.field(
         description="""(Optional) Updated date when the membership ends.
(Volitelné) Aktualizované datum ukončení členství.""",
         default=None
    )
    # Private pole – nejsou zahrnuta do SDL
    changedby_id: strawberry.Private["IDType"] = None
    group_id: strawberry.Private["IDType"] = None


@strawberry.input(
    description="""## Description
Input model for deleting a membership.
Vstupní model pro smazání členství.

## Fields
- **id**: Unique identifier of the membership.
  Unikátní identifikátor členství.
- **lastchange**: Timestamp of the last modification for concurrency control.
  Časové razítko poslední změny, sloužící k řízení konzistence.
"""
)
class MembershipDeleteGQLModel:
    id: "IDType" = strawberry.field(
         description="""Unique identifier of the membership.
Unikátní identifikátor členství."""
    )
    lastchange: datetime.datetime = strawberry.field(
         description="""Timestamp of the last modification for concurrency control.
Časové razítko poslední změny, sloužící k řízení konzistence."""
    )

class UpdateMembershipPermission(RBACPermission):
    message = "User is not allowed to change membership"
    async def has_permission(self, source, info: strawberry.types.Info, membership: "MembershipUpdateGQLModel") -> bool:
        loader = MembershipGQLModel.getLoader(info)
        row = await loader.load(membership.id)
        membership.group_id = row.group_id

        adminRoleNames = ["administrátor"]
        allowedRoleNames = ["garant"]
        role = await self.resolveUserRole(info, 
            rbacobject=membership.group_id,
            adminRoleNames=adminRoleNames, 
            allowedRoleNames=allowedRoleNames)
        
        if not role: return False
        # roleTypeName = role["type"]["name"]
        # if roleTypeName in allowedRoleNames:
        #     if group.mastergroup_id:
        #         raise self.error_class(f"{roleTypeName} cannot change mastergroup_id")
        #     if group.grouptype_id:
        #         raise self.error_class(f"{roleTypeName} cannot change grouptype_id")
        return True


@strawberry.mutation(
    description="""## Description
Updates the membership record, except for the associated group and user.
Aktualizuje záznam členství, s výjimkou změny asociované skupiny a uživatele.

## Details
This mutation updates membership details such as validity and effective dates.
Changing the associated group or user is not permitted.
Tato mutace aktualizuje detaily členství, jako je platnost a datum začátku/ukončení.
Změna asociované skupiny nebo uživatele není povolena.

## Permissions
- Only authenticated users (OnlyForAuthentized) with appropriate membership update permissions (UpdateMembershipPermission) can perform this mutation.
- Pouze autentizovaní uživatelé s odpovídajícími právy pro aktualizaci členství (UpdateMembershipPermission) mohou tuto mutaci provést.
""",
    permission_classes=[
        OnlyForAuthentized,
        UpdateMembershipPermission
    ]
)
async def membership_update(self, 
    info: strawberry.types.Info, 
    membership: "MembershipUpdateGQLModel"
) -> Union[MembershipGQLModel, UpdateError[MembershipGQLModel]]:
    result = await Update[GroupGQLModel].DoItSafeWay(info=info, entity=membership)
    return result

class InsertMembershipPermission(RBACPermission):
    message = "User is not allowed create new membership"
    async def has_permission(self, source, info: strawberry.types.Info, membership: "MembershipInsertGQLModel") -> bool:
        adminRoleNames = ["administrátor"]
        allowedRoleNames = ["garant"]
        role = await self.resolveUserRole(info, 
            rbacobject=membership.group_id, 
            adminRoleNames=adminRoleNames, 
            allowedRoleNames=allowedRoleNames)
        
        if not role: return False
        return True

@strawberry.mutation(
    description="""## Description
Inserts new membership.
Vloží nové členství.

## Details
This mutation creates a new membership record using the provided details.
All required fields must be specified and valid.
Tato mutace vytvoří nový záznam členství se zadanými detaily.
Všechna povinná pole musí být správně vyplněna.

## Permissions
- Only authenticated users (OnlyForAuthentized) with the permissions defined by InsertMembershipPermission can perform this mutation.
- Pouze autentizovaní uživatelé s oprávněními definovanými pomocí InsertMembershipPermission mohou tuto mutaci provést.
""",
    permission_classes=[
        OnlyForAuthentized,
        InsertMembershipPermission
    ]
)
async def membership_insert(self, 
    info: strawberry.types.Info, 
    membership: "MembershipInsertGQLModel"
) -> Union[MembershipGQLModel, InsertError[MembershipGQLModel]]:
    result = await Insert[MembershipGQLModel].DoItSafeWay(info=info, entity=membership)
    return result


@strawberry.mutation(
    description="""## Description
Deletes the membership.
Maže členství.

## Details
This mutation removes an existing membership record identified by its unique identifier.
It uses the last change timestamp for concurrency control to ensure data consistency.
Tato mutace odstraní existující záznam členství, který je identifikován jeho unikátním identifikátorem.
Pro kontrolu konzistence se využívá časové razítko poslední změny.

## Permissions
- Only authenticated users with administrative rights (OnlyForAdmins) are allowed to perform this mutation.
- Pouze autentizovaní uživatelé s administrátorskými právy (OnlyForAdmins) mohou tuto mutaci provést.
""",
    permission_classes=[
        OnlyForAuthentized,
        OnlyForAdmins
    ]
)
async def membership_delete(self, info: strawberry.types.Info, membership: MembershipDeleteGQLModel) -> typing.Optional[DeleteError[MembershipGQLModel]]:
    result = await Delete[MembershipGQLModel].DoItSafeWay(info=info, entity=membership)
    return result

