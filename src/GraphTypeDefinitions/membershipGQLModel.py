import dataclasses
import typing
import datetime
import strawberry
import uuid
from typing import List, Optional, Union, Annotated, Type
from uoishelpers.resolvers import createInputs

from uoishelpers.gqlpermissions.LoadDataExtension import LoadDataExtension
from uoishelpers.gqlpermissions.RbacProviderExtension import RbacProviderExtension, MISSING
from uoishelpers.gqlpermissions.UserRoleProviderExtension import UserRoleProviderExtension
from uoishelpers.gqlpermissions.UserAccessControlExtension import UserAccessControlExtension
from uoishelpers.gqlpermissions.UserAbsoluteAccessControlExtension import UserAbsoluteAccessControlExtension

from .BaseGQLModel import BaseGQLModel, IDType, Relation
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
        permission_classes=[
            OnlyForAuthentized
        ],
        directives=[
            Relation(to="UserGQLModel")
        ]
    )

    group_id: typing.Optional[IDType] = strawberry.field(
        description="""ID of associated group.
ID spojené skupiny.""",
        permission_classes=[
            OnlyForAuthentized
        ],
        directives=[
            Relation(to="GroupGQLModel")
        ]
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
from uoishelpers.resolvers import createInputs2
from dataclasses import dataclass

GroupInputWhereFilter = Annotated["GroupInputWhereFilter", strawberry.lazy(".groupGQLModel")]
UserInputWhereFilter = Annotated["UserInputWhereFilter", strawberry.lazy(".userGQLModel")]

@createInputs2
class MembershipInputWhereFilter:
    valid: bool
    # from .userGQLModel import UserInputWhereFilter
    # from .groupGQLModel import GroupInputWhereFilter
    group: GroupInputWhereFilter
    user: UserInputWhereFilter

# from ._GraphResolvers import asPage
@strawberry.interface(description="Membership related queries")
class MembershipQueries:
    membership_page = strawberry.field(
        description="""Retrieves memberships in a paged format.""",
        permission_classes=[OnlyForAuthentized],
        graphql_type=List[MembershipGQLModel],
        resolver=PageResolver[MembershipGQLModel](whereType=MembershipInputWhereFilter)
    )

    membership_by_id = strawberry.field(
        description="""Retrieves a specific membership by its unique identifier.""",
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

from .utils import InputModelMixin

@strawberry.input(
    description="""Input model for inserting a new membership."""
)
class MembershipInsertGQLModel(InputModelMixin):
    getLoader = MembershipGQLModel.getLoader
    user_id: "IDType" = strawberry.field(
         description="""Unique identifier of the user."""
    )
    group_id: "IDType" = strawberry.field(
         description="""Unique identifier of the group."""
    )
    id: typing.Optional["IDType"] = strawberry.field(
         description="""Primary key of the membership entity.""",
         default=None
    )
#     valid: typing.Optional[bool] = strawberry.field(
#          description="""(Optional) Flag indicating if the membership is valid.
# (Volitelné) Příznak platnosti členství.""",
#          default=True
#     )
    startdate: typing.Optional[datetime.datetime] = strawberry.field(
         description="""(Optional) Date when the membership starts.""",
         default=None
    )
    enddate: typing.Optional[datetime.datetime] = strawberry.field(
         description="""(Optional) Date when the membership ends.""",
         default=None
    )
    # Private pole – nejsou zahrnuta do SDL
    createdby_id: strawberry.Private["IDType"] = None


@strawberry.input(
    description="""Input model for updating an existing membership."""
)
class MembershipUpdateGQLModel:
    id: "IDType" = strawberry.field(
         description="""Unique identifier of the membership."""
    )
    lastchange: datetime.datetime = strawberry.field(
         description="""Timestamp of the last modification for concurrency control."""
    )
    # valid: typing.Optional[bool] = strawberry.field(
    #      description="""(Optional) Flag indicating if the membership is valid.""",
    #      default=strawberry.UNSET
    # )
    startdate: typing.Optional[datetime.datetime] = strawberry.field(
         description="""(Optional) Updated date when the membership starts.""",
         default=strawberry.UNSET
    )
    enddate: typing.Optional[datetime.datetime] = strawberry.field(
         description="""(Optional) Updated date when the membership ends.""",
         default=strawberry.UNSET
    )
    # Private pole – nejsou zahrnuta do SDL
    changedby_id: strawberry.Private["IDType"] = None
    group_id: strawberry.Private["IDType"] = None


@strawberry.input(
    description="""Input model for deleting a membership."""
)
class MembershipDeleteGQLModel:
    id: "IDType" = strawberry.field(
         description="""Unique identifier of the membership."""
    )
    lastchange: datetime.datetime = strawberry.field(
         description="""Timestamp of the last modification for concurrency control."""
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

class InsertMembershipRbacProviderExtension(RbacProviderExtension):
    async def provide_rbac_object_id(self, source, info: strawberry.types.Info, *args, **kwargs):
        input_params = next(iter(kwargs.values()), None)
        rbacobject_id = getattr(input_params, "group_id", MISSING)
        return rbacobject_id

@strawberry.interface(description="Membership related mutations")
class MembershipMutations:


    @strawberry.mutation(
        description="""Updates the membership record, except the associated group and user""",
        permission_classes=[
            OnlyForAuthentized,
            # UpdateMembershipPermission
        ],
        extensions=[
            UserAccessControlExtension[UpdateError, MembershipGQLModel](roles=["administrátor", "personalista"]),
            UserRoleProviderExtension[UpdateError, MembershipGQLModel](),
            RbacProviderExtension[UpdateError, MembershipGQLModel](),
            LoadDataExtension[UpdateError, MembershipGQLModel]()
        ],
    )
    async def membership_update(self, 
        info: strawberry.types.Info, 
        membership: "MembershipUpdateGQLModel",
        user_roles: typing.List[dict],
        rbacobject_id: IDType,
        db_row: typing.Any
    ) -> Union[MembershipGQLModel, UpdateError[MembershipGQLModel]]:
        result = await Update[MembershipGQLModel].DoItSafeWay(info=info, entity=membership)
        return result

    @strawberry.mutation(
        description="""Inserts new membership""",
        permission_classes=[
            OnlyForAuthentized,
            # InsertMembershipPermission
        ],
        extensions=[
            UserAccessControlExtension[InsertError, MembershipGQLModel](
                roles=["administrátor", "personalista", "garant", "garant předmětu"]
            ),
            UserRoleProviderExtension[InsertError, MembershipGQLModel](),
            InsertMembershipRbacProviderExtension[InsertError, MembershipGQLModel](),
        ],
    )
    async def membership_insert(self, 
        info: strawberry.types.Info, 
        membership: "MembershipInsertGQLModel",
        user_roles: typing.List[dict],
        rbacobject_id: IDType,
    ) -> Union[MembershipGQLModel, InsertError[MembershipGQLModel]]:
        result = await Insert[MembershipGQLModel].DoItSafeWay(info=info, entity=membership)
        print("membership_insert", type(result), result)
        return result


    @strawberry.mutation(
        description="""Deletes the membership. If you want to end membership, you should update it with appropriate enddate.""",
        permission_classes=[
            OnlyForAuthentized,
            # OnlyForAdmins
        ],
        extensions=[
            UserAccessControlExtension[UpdateError, MembershipGQLModel](roles=["superadmin"]),
            UserRoleProviderExtension[UpdateError, MembershipGQLModel](),
            RbacProviderExtension[UpdateError, MembershipGQLModel](),
            LoadDataExtension[UpdateError, MembershipGQLModel]()
        ],
    )
    async def membership_delete(self, info: strawberry.types.Info, membership: MembershipDeleteGQLModel) -> typing.Optional[DeleteError[MembershipGQLModel]]:
        ""
        result = await Delete[MembershipGQLModel].DoItSafeWay(info=info, entity=membership)
        return result

