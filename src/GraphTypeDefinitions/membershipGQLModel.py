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
    default_vector_resolver,
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
    description="""Entity representing a relation between an user and a group""",
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

    # id = resolve_id
    # changedby = resolve_changedby
    # created = resolve_created
    # lastchange = resolve_lastchange
    # createdby = resolve_createdby
   
    # async def resolve_user(self, info: strawberry.Info):
    #     from .userGQLModel import UserGQLModel
    #     user_id = self.user_id if self._data is None else self._data.user_id
    #     return await UserGQLModel.resolve_reference(info=info, id=user_id)
    user_id: typing.Optional[IDType] = strawberry.field(
        description="ID of associated user",
        permission_classes=[
            OnlyForAuthentized
        ]        
    )

    group_id: typing.Optional[IDType] = strawberry.field(
        description="ID of associated group",
        permission_classes=[
            OnlyForAuthentized
        ]        
    )

    user = strawberry.field(
        description="""user""",
        permission_classes=[
            OnlyForAuthentized
        ],
        graphql_type=Optional[UserGQLModel],
        # resolver=default_scalar_resolver(fkey_field_name="user_id", gql_type=Type[UserGQLModel]) # DBResolvers.MembershipModel.user(UserGQLModel)
        resolver=default_scalar_resolver(fkey_field_name="user_id")
    )

    # async def resolve_group(self, info: strawberry.Info):
    #     from .groupGQLModel import GroupGQLModel
    #     group_id = self.group_id if self._data is None else self._data.group_id
    #     return await GroupGQLModel.resolve_reference(info=info, id=group_id)
    
    group = strawberry.field(
        description="""group""",
        permission_classes=[
            OnlyForAuthentized
        ],
        graphql_type=Optional[GroupGQLModel],
        # resolver=default_scalar_resolver(fkey_field_name="group_id", gql_type=Type[GroupGQLModel])#DBResolvers.MembershipModel.group(GroupGQLModel)
        resolver=default_scalar_resolver(fkey_field_name="group_id")#DBResolvers.MembershipModel.group(GroupGQLModel)
    )

    valid = strawberry.field(
        description="""is the membership is still valid""",
        permission_classes=[
            OnlyForAuthentized
        ],
        graphql_type=bool,
        resolver=default_resolver
    )
    
    startdate: Optional[datetime.datetime] = strawberry.field(
        description="""date when the membership begins""",
        permission_classes=[
            OnlyForAuthentized
        ],
    )
    
    enddate: Optional[datetime.datetime] = strawberry.field(
        description="""date when the membership ends""",
        permission_classes=[
            OnlyForAuthentized
        ],
    )

    valid: Optional[bool] = strawberry.field(
        description="""if membership is valid""",
        permission_classes=[
            OnlyForAuthentized
        ],
    )

    RBACObjectGQLModel = Annotated["RBACObjectGQLModel", strawberry.lazy(".RBACObjectGQLModel")]
    @strawberry.field(
        description="""""",
        permission_classes=[OnlyForAuthentized])
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
    description="Retrieves memberships",
    permission_classes=[
        OnlyForAuthentized
    ],
    graphql_type=List[MembershipGQLModel],
    # resolver=DBResolvers.MembershipModel.resolve_page(MembershipGQLModel, WhereFilterModel=MembershipInputWhereFilter)
    resolver=default_page_resolver(whereType=MembershipInputWhereFilter)
)

membership_by_id = strawberry.field(
    description="Retrieves the membership",
    permission_classes=[
        OnlyForAuthentized
    ],
    graphql_type=Optional[MembershipGQLModel],
    # resolver=DBResolvers.MembershipModel.resolve_by_id(MembershipGQLModel)
    resolver=default_by_id_resolver()
)
#####################################################################
#
# Mutation section
#
#####################################################################
import datetime

@strawberry.input(description="")
class MembershipUpdateGQLModel:
    id: IDType
    lastchange: datetime.datetime   
    valid: Optional[bool] = None
    startdate: Optional[datetime.datetime] = None
    enddate: Optional[datetime.datetime] = None
    changedby_id: strawberry.Private[IDType] = None
    group_id: strawberry.Private[IDType] = None

@strawberry.input(description="")
class MembershipInsertGQLModel:
    user_id: IDType
    group_id: IDType
    id: Optional[IDType] = strawberry.field(description="Primary key of entity", default_factory=uuid.uuid1)
    valid: Optional[bool] = True
    startdate: Optional[datetime.datetime] = None
    enddate: Optional[datetime.datetime] = None
    createdby_id: strawberry.Private[IDType] = None
    

@strawberry.type(description="")
class MembershipResultGQLModel:
    id: IDType = None
    msg: str = None

    @strawberry.field(description="""Result of membership operation""")
    async def membership(self, info: strawberry.types.Info) -> Union[MembershipGQLModel, None]:
        result = await MembershipGQLModel.resolve_reference(info, self.id)
        return result
    
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
    description="""Update the membership, cannot update group / user""",
    permission_classes=[
        OnlyForAuthentized,
        UpdateMembershipPermission
    ])
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
    description="""Inserts new membership""",
    permission_classes=[
        OnlyForAuthentized,
        InsertMembershipPermission
    ])
async def membership_insert(self, 
    info: strawberry.types.Info, 
    membership: "MembershipInsertGQLModel"
) -> Union[MembershipGQLModel, InsertError[MembershipGQLModel]]:
    result = await Insert[GroupGQLModel].DoItSafeWay(info=info, entity=membership)
    return result

@strawberry.mutation(
    description="Deletes the membership",
    permission_classes=[
        OnlyForAuthentized,
        OnlyForAdmins
    ])
async def membership_delete(self, info: strawberry.types.Info, membership: IDType) -> Union[MembershipGQLModel, DeleteError[MembershipGQLModel]]:
    result = await Delete[GroupGQLModel].DoItSafeWay(info=info, entity=membership)
    return result

