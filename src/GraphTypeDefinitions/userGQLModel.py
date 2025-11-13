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

from .BaseGQLModel import BaseGQLModel, IDType, Relation
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


MembershipGQLModel = Annotated["MembershipGQLModel", strawberry.lazy(".membershipGQLModel")]
RoleGQLModel = Annotated["RoleGQLModel", strawberry.lazy(".roleGQLModel")]
GroupGQLModel = Annotated["GroupGQLModel", strawberry.lazy(".groupGQLModel")]

RoleInputWhereFilter = Annotated["RoleInputWhereFilter", strawberry.lazy(".roleGQLModel")]
MembershipInputWhereFilter = Annotated["MembershipInputWhereFilter", strawberry.lazy(".membershipGQLModel")]


@strawberry.federation.type(
    keys=["id"],
    description="""Description:
Entity representing a user
Entita reprezentujícího uživatele

Details:
GraphQL type that models user data including personal details, roles, memberships, and groups.
GraphQL typ modelující data uživatele včetně osobních údajů, rolí, členství a skupin.

Permissions:
Access to this type is restricted to authenticated users.
Přístup k tomuto typu je omezen na autentizované uživatele.
"""
)
class UserGQLModel(BaseGQLModel):
    @classmethod
    def getLoader(cls, info):
        return getLoader(info).UserModel

    name: Optional[str] = strawberry.field(
        default=None,
        description="""Full name (if in database)
Celé jméno (pokud je v databázi)""",
        permission_classes=[OnlyForAuthentized]
    )

    givenname: Optional[str] = strawberry.field(
        default=None,
        description="""User's name (like John)
Jméno uživatele (např. John)""",
        permission_classes=[OnlyForAuthentized]
    )

    middlename: Optional[str] = strawberry.field(
        default=None,
        description="""Middle name
Střední jméno""",
        permission_classes=[OnlyForAuthentized]
    )

    email: Optional[str] = strawberry.field(
        default=None,
        description="""Email address
Emailová adresa""",
        permission_classes=[OnlyForAuthentized]
    )

    firstname: Optional[str] = strawberry.field(
        default=None,
        description="""User's first name (like John)
Křestní jméno uživatele (např. John)""",
        permission_classes=[OnlyForAuthentized]
    )

    surname: Optional[str] = strawberry.field(
        default=None,
        description="""User's family name (like Obama)
Rodinné jméno uživatele (např. Obama)""",
        permission_classes=[OnlyForAuthentized]
    )

    valid: Optional[bool] = strawberry.field(
        default=None,
        description="""User validity status
Stav platnosti uživatele""",
        permission_classes=[OnlyForAuthentized]
    )

    startdate: Optional[datetime.datetime] = strawberry.field(
        default=None,
        description="""Account start date
Datum zahájení účtu""",
        permission_classes=[OnlyForAuthentized]
    )

    enddate: Optional[datetime.datetime] = strawberry.field(
        default=None,
        description="""Account end date
Datum ukončení účtu""",
        permission_classes=[OnlyForAuthentized]
    )

    type_id: Optional[IDType] = strawberry.field(
        default=None,
        description="""User type identifier
Identifikátor typu uživatele""",
        permission_classes=[OnlyForAuthentized]
    )

    @strawberry.field(
        description="""Checks if the current record belongs to the logged-in user
Zjistí, zda záznam patří přihlášenému uživateli""",
        permission_classes=[OnlyForAuthentized]
    )
    async def is_this_me(self, info: strawberry.types.Info) -> bool:
        user = getUserFromInfo(info)
        if user is None:
            return None
        user_id = user.get("id", None)
        return user_id == self.id

    @strawberry.field(
        description="""Fetches roles related to the user
Načte role vztažené k uživateli""",
        permission_classes=[OnlyForAuthentized]
    )
    async def roles_on(self, info: strawberry.types.Info) -> typing.List["RoleGQLModel"]:
        from .roleGQLModel import resolve_roles_on_user, RoleGQLModel
        user = getUserFromInfo(info)
        user_id = user.get("id", None)
        result = await resolve_roles_on_user(self, info=info, user_id=user_id)
        return list(RoleGQLModel.from_dataclass(r) for r in result)

    @strawberry.field(
        description="""Performs GDPR compliance check
Provádí kontrolu souladu s GDPR""",
        permission_classes=[OnlyForAuthentized]
    )
    def gdpr(self, info: strawberry.types.Info, force: Optional[bool] = False) -> Optional[str]:
        return "gdpr information" if force else None

    @strawberry.field(
        description="""Concatenates user's name parts into full name
Spojí části jména uživatele do celého jména""",
        permission_classes=[OnlyForAuthentized]
    )
    def fullname(self, info: strawberry.types.Info) -> Optional[str]:
        return f"{self.name} {self.middlename} {self.surname}" if self.middlename else f"{self.name} {self.surname}"

    memberships: typing.List[MembershipGQLModel] = strawberry.field(
        description="""List of memberships associated with the user
Seznam členství spojených s uživatelem""",
        permission_classes=[OnlyForAuthentized],
        resolver=VectorResolver[MembershipGQLModel](fkey_field_name="user_id", whereType=MembershipInputWhereFilter)
    )

    membership: typing.List[MembershipGQLModel] = strawberry.field(
        description="""Deprecated: list of memberships (use memberships)
Zastaralé: seznam členství (použijte memberships)""",
        deprecation_reason="use memberships",
        permission_classes=[OnlyForAuthentized],
        resolver=VectorResolver[MembershipGQLModel](fkey_field_name="user_id", whereType=MembershipInputWhereFilter)
    )

    roles: typing.List[RoleGQLModel] = strawberry.field(
        description="""Roles assigned to the user
Role přiřazené uživateli""",
        permission_classes=[OnlyForAuthentized],
        resolver=VectorResolver[RoleGQLModel](fkey_field_name="user_id", whereType=RoleInputWhereFilter)
    )

#     @strawberry.field(
#         description="""Retrieves a list of groups where the user is a member, with optional pagination and filtering
# Načte seznam skupin, kde je uživatel členem, s volitelným stránkováním a filtrováním""",
#         permission_classes=[OnlyForAuthentized]
#     )
#     async def groups(
#         self,
#         info: strawberry.types.Info,
#         limit: Optional[int] = 10,
#         skip: Optional[int] = 0,
#         order_by: Optional[str] = None,
#         where: Optional[MembershipInputWhereFilter] = None
#     ) -> typing.List["GroupGQLModel"]:
#         from .membershipGQLModel import MembershipGQLModel
#         from .groupGQLModel import GroupGQLModel
#         membershipLoader = MembershipGQLModel.getLoader(info=info)
#         extendedfilter = {"user_id": self.id}
#         where = None if where is None else strawberry.asdict(where)
#         memberships = await membershipLoader.page(skip=skip, limit=limit, orderby=order_by, where=where, extendedfilter=extendedfilter)
#         groupLoader = GroupGQLModel.getLoader(info=info)
#         future_groups = (groupLoader.load(membership.group_id) for membership in memberships)
#         group_rows = await asyncio.gather(*future_groups)
#         return list(GroupGQLModel.from_dataclass(row) for row in group_rows)

    @strawberry.field(
        description="""Retrieves a list of groups of a specified type where the user is a member
Načte seznam skupin daného typu, kde je uživatel členem""",
        permission_classes=[OnlyForAuthentized]
    )
    async def member_of(
        self,
        info: strawberry.types.Info,
        grouptype_id: Optional[IDType] = None
    ) -> typing.List["GroupGQLModel"]:
        from .groupGQLModel import GroupGQLModel
        from .membershipGQLModel import MembershipGQLModel
        loader = MembershipGQLModel.getLoader(info)
        rows = await loader.filter_by(user_id=self.id)
        groupLoader = GroupGQLModel.getLoader(info=info)
        futureresults = (groupLoader.load(row.group_id) for row in rows if row.valid)
        group_rows = await asyncio.gather(*futureresults)
        filtered_groups = filter(lambda item: item.grouptype_id == grouptype_id, group_rows)
        return list(GroupGQLModel.from_dataclass(g) for g in filtered_groups)
    
#####################################################################
#
# Special fields for query
#
#####################################################################

from uoishelpers.resolvers import createInputs2
from dataclasses import dataclass
#MembershipInputWhereFilter = Annotated["MembershipInputWhereFilter", strawberry.lazy(".membershipGQLModel")]
@createInputs2
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
    roles: RoleInputWhereFilter = strawberry.field(description="""Filter for roles
for field roles the filters could be
{"roles": {"start_date": {"_ge": "2025-06-30T18:01:59"}}}
{"roles": {"roletype_id": {"_eq": "8da9cec4-bfc2-487f-8080-dc596dfec53c"}}}
{"roles": {"_and": [{"start_date": {"_ge": "2025-06-30T18:01:59"}}, {"roletype_id": {"_eq": "8da9cec4-bfc2-487f-8080-dc596dfec53c"}}]}}

""", default=None)

@strawberry.interface(description="User queries interface")
class UserQueries:

    user_by_id = strawberry.field(
        description="""## Description
Fetches a user by its unique identifier.
Načte uživatele podle jeho unikátního identifikátoru.

## Details
Utilizes a data loader to efficiently retrieve user details from the underlying data source.
Využívá loader pro efektivní načítání detailů uživatele z databáze.

## Permissions
Only authenticated users can access this field.
Pouze autentizovaní uživatelé mají přístup k tomuto poli.
    """,
        permission_classes=[OnlyForAuthentized],
        graphql_type=Optional[UserGQLModel],
        resolver=UserGQLModel.load_with_loader
    )


    user_page = strawberry.field(
        description="""## Description
Fetches a paginated list of users.
Načte stránkovaný seznam uživatelů.

## Details
Returns a list of users based on filtering criteria defined in UserInputWhereFilter. Supports pagination, sorting, and advanced filtering options.
Vrací seznam uživatelů na základě filtračních kritérií definovaných ve třídě UserInputWhereFilter. Podporuje stránkování, řazení a pokročilé filtrovací možnosti.

## Permissions
Accessible only to authenticated users.
Přístup pouze pro autentizované uživatele.
    """,
        permission_classes=[OnlyForAuthentized],
        graphql_type=List[UserGQLModel],
        resolver=PageResolver[UserGQLModel](whereType=UserInputWhereFilter)
    )

    @strawberry.field(
        description="""## Description
Returns the logged in user.
Vrací přihlášeného uživatele.

## Details
Retrieves the currently authenticated user based on context information.
Načítá aktuálně autentizovaného uživatele na základě informací v kontextu.

## Permissions
Accessible only to authenticated users.
Přístup pouze pro autentizované uživatele.
    """,
        permission_classes=[OnlyForAuthentized]
    )
    async def me(self, info: strawberry.types.Info) -> Optional[UserGQLModel]:
        user = getUserFromInfo(info)
        if user is None:
            return None
        user_id = user.get("id", None)
        if user_id is None:
            return None
        result = await UserGQLModel.resolve_reference(info=info, id=user_id)
        return result

#####################################################################
#
# Mutation section
#
#####################################################################
import datetime

import datetime
from typing import Optional
import strawberry
from uoishelpers.resolvers import InputModelMixin
@strawberry.input(description="""
Description:
Input for updating a UserGQLModel entity.
Vstup pro aktualizaci entity UserGQLModel.
Details:
Requires a unique identifier and a lastchange timestamp for concurrency control. Optional fields include name, surname, email, and valid status.
Vyžaduje unikátní identifikátor a časové razítko poslední změny pro řízení souběžnosti. Volitelná pole zahrnují jméno, příjmení, email a stav validace.
Permissions:
Only authenticated users with appropriate RBAC permissions can perform update operations.
Pouze autentizovaní uživatelé s odpovídajícími RBAC oprávněními mohou tuto operaci provádět.
""")
class UserUpdateGQLModel:
    id: IDType = strawberry.field(description="Unique identifier\nUnikátní identifikátor")
    lastchange: datetime.datetime = strawberry.field(description="Timestamp of last change\nČasové razítko poslední změny")
    name: Optional[str] = strawberry.field(description="User's first name\nJméno uživatele", default=strawberry.UNSET)
    surname: Optional[str] = strawberry.field(description="User's surname\nPříjmení uživatele", default=strawberry.UNSET)
    email: Optional[str] = strawberry.field(description="User's email address\nEmail uživatele", default=strawberry.UNSET)
    valid: Optional[bool] = strawberry.field(description="Validation status of the user\nStav validace uživatele", default=strawberry.UNSET)
    changedby_id: strawberry.Private[IDType] = None

@strawberry.input(description="""
Description:
Input for creating a new UserGQLModel entity.
Vstup pro vytvoření nové entity UserGQLModel.
Details:
Optional fields include id (primary key), name, surname, email, and valid status.
Volitelná pole zahrnují id (primární klíč), jméno, příjmení, email a stav validace.
Permissions:
Only authenticated users with appropriate RBAC permissions can perform create operations.
Pouze autentizovaní uživatelé s odpovídajícími RBAC oprávněními mohou tuto operaci provádět.
""")
class UserInsertGQLModel(InputModelMixin):
    id: Optional[IDType] = strawberry.field(description="Primary key identifier\nPrimární klíč", default=None)
    name: Optional[str] = strawberry.field(description="User's first name\nJméno uživatele", default=None)
    surname: Optional[str] = strawberry.field(description="User's surname\nPříjmení uživatele", default=None)
    email: Optional[str] = strawberry.field(description="User's email address\nEmail uživatele", default=None)
    valid: Optional[bool] = strawberry.field(description="Validation status of the user\nStav validace uživatele", default=None)

    from .membershipGQLModel import MembershipInsertGQLModel
    memberships: Optional[List[MembershipInsertGQLModel]] = strawberry.field(
        description="List of memberships associated with the user\nSeznam členství spojených s uživatelem",
        default_factory=list
    )
    from .roleGQLModel import RoleInsertGQLModel
    roles: Optional[List[RoleInsertGQLModel]] = strawberry.field(
        description="List of roles assigned to the user\nSeznam rolí přiřazených uživateli",
        default_factory=list
    )
    createdby_id: strawberry.Private[IDType] = None

@strawberry.input(description="""
Description:
Input for deleting a UserGQLModel entity.
Vstup pro odstranění entity UserGQLModel.
Details:
Requires the id and lastchange timestamp to ensure safe deletion and data consistency.
Vyžaduje id a časové razítko poslední změny pro zajištění bezpečného odstranění a zachování konzistence dat.
Permissions:
Only authenticated users with appropriate RBAC permissions can perform delete operations.
Pouze autentizovaní uživatelé s odpovídajícími RBAC oprávněními mohou tuto operaci provádět.
""")
class UserDeleteGQLModel:
    id: IDType = strawberry.field(description="Primary key identifier\nPrimární klíč")
    lastchange: datetime.datetime = strawberry.field(description="Timestamp of last change\nČasové razítko poslední změny")


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
    
from uoishelpers.gqlpermissions.LoadDataExtension import LoadDataExtension
from uoishelpers.gqlpermissions.RbacProviderExtension import RbacProviderExtension
from uoishelpers.gqlpermissions.UserRoleProviderExtension import UserRoleProviderExtension
from uoishelpers.gqlpermissions.UserAccessControlExtension import UserAccessControlExtension

@strawberry.interface(description="User mutations interface")
class UserMutations:

    @strawberry.mutation(
        description="""
Description:
Mutation for updating a UserGQLModel entity.
Mutace pro aktualizaci entity UserGQLModel.

Details:
Executes a safe update operation with concurrency control using provided update input.
Provádí bezpečnou aktualizaci s využitím kontroly souběžnosti na základě zadaného vstupu.

Permissions:
Only authenticated users with the necessary update permissions can execute this mutation.
Pouze autentizovaní uživatelé s potřebnými oprávněními mohou tuto mutaci provést.
    """,
        permission_classes=[
            OnlyForAuthentized,
            # UpdateUserPermission
        ],
        extensions=[
            # UpdatePermissionCheckRoleFieldExtension[GroupGQLModel](roles=["administrátor", "personalista"]),
            UserAccessControlExtension[UpdateError, UserGQLModel](roles=["administrátor", "personalista"]),
            UserRoleProviderExtension[UpdateError, UserGQLModel](),
            RbacProviderExtension[UpdateError, UserGQLModel](),
            LoadDataExtension[UpdateError, UserGQLModel]()
        ]
    )
    async def user_update(
        self, 
        info: strawberry.types.Info, 
        user: UserUpdateGQLModel,
        db_row: typing.Any,
        rbacobject_id: IDType,
        user_roles: typing.List[dict],
    ) -> typing.Union[UserGQLModel, UpdateError[UserGQLModel]]:
        print(f"user_update.db_row={db_row}")
        # return UserGQLModel.from_dataclass(db_row)
        return await Update[UserGQLModel].DoItSafeWay(info=info, entity=user)

    class InsertUserPermission(RBACPermission):
        message = "User is not allowed to create an user"
        async def has_permission(self, source, info: strawberry.types.Info, user: UserInsertGQLModel) -> bool:
            adminRoleNames = ["administrátor", "personalista"]
            allowedRoleNames = []
            role = await self.resolveUserRole(
                info, 
                rbacobject=user.id, 
                adminRoleNames=adminRoleNames, 
                allowedRoleNames=allowedRoleNames
            )
            if not role:
                return False
            return True

    @strawberry.mutation(
        description="""
Description:
Mutation for inserting a new UserGQLModel entity.
Mutace pro vytvoření nové entity UserGQLModel.
Details:
Executes a safe insertion operation with role-based access control and data validation.
Provádí bezpečné vytvoření s kontrolou přístupových práv a validací vstupních dat.
Permissions:
Only authenticated users with the necessary insert permissions can perform this mutation.
Pouze autentizovaní uživatelé s potřebnými oprávněními mohou tuto mutaci provádět.
    """,
        permission_classes=[
            OnlyForAuthentized,
            # InsertUserPermission                
        ],
        extensions=[
            # UpdatePermissionCheckRoleFieldExtension[GroupGQLModel](roles=["administrátor", "personalista"]),
            UserAccessControlExtension[InsertError, UserGQLModel](roles=["administrátor", "personalista"]),
            UserRoleProviderExtension[InsertError, UserGQLModel](),
            RbacProviderExtension[InsertError, UserGQLModel](),
            LoadDataExtension[InsertError, UserGQLModel]()
        ]
    )
    async def user_insert(
        self, 
        info: strawberry.types.Info, 
        user: UserInsertGQLModel,
        db_row: typing.Any,
        rbacobject_id: IDType,
        user_roles: typing.List[dict],
    ) -> typing.Union[UserGQLModel, InsertError[UserGQLModel]]:
        return await Insert[UserGQLModel].DoItSafeWay(info=info, entity=user)

    @strawberry.mutation(
        description="""
Description:
Mutation for deleting a UserGQLModel entity.
Mutace pro odstranění entity UserGQLModel.

Details:
Requires the id and lastchange timestamp to ensure safe deletion and data consistency.
Vyžaduje id a časové razítko poslední změny pro zajištění bezpečného odstranění a zachování konzistence dat.

Permissions:
Only authenticated users with appropriate RBAC permissions can perform delete operations.
Pouze autentizovaní uživatelé s odpovídajícími RBAC oprávněními mohou tuto mutaci provádět.
    """,
        permission_classes=[
            OnlyForAuthentized,
            # OnlyForAdmins
        ],
        extensions=[
            # UpdatePermissionCheckRoleFieldExtension[GroupGQLModel](roles=["administrátor", "personalista"]),
            UserAccessControlExtension[DeleteError, UserGQLModel](roles=["administrátor", "personalista"]),
            UserRoleProviderExtension[DeleteError, UserGQLModel](),
            RbacProviderExtension[DeleteError, UserGQLModel](),
            LoadDataExtension[DeleteError, UserGQLModel]()
        ]
    )
    async def user_delete(
        self, 
        info: strawberry.types.Info, 
        user: UserDeleteGQLModel,
        user_roles: typing.List[dict],
        rbacobject_id: IDType,
        db_row: typing.Any
    ) -> typing.Optional[DeleteError[UserGQLModel]]:
        return await Delete[UserGQLModel].DoItSafeWay(info=info, entity=user)


