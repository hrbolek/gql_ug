import typing
import strawberry
import uuid
import asyncio
from typing import List, Annotated, Optional, Union

import strawberry.types
from .BaseGQLModel import BaseGQLModel, IDType

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

from ._GraphResolvers import resolve_id
from ._GraphPermissions import RoleBasedPermission, OnlyForAuthentized
from src.Dataloaders import getLoadersFromInfo as getLoader, getUserFromInfo, getLoadersFromInfo
from .stateGQLModel import StateDataAccessType, StateGQLModel

RoleGQLModel = Annotated["RoleGQLModel", strawberry.lazy(".roleGQLModel")]

#@strawberry.federation.type(extend=False, keys=["id"])
@strawberry.federation.interface(keys=["id"])
class RBACObjectGQLInterface:

    id: IDType = strawberry.field(description="id") # = resolve_id
    asUser: strawberry.Private[bool] = False
    asGroup: strawberry.Private[bool] = False
    
    @classmethod
    async def resolve_roles(cls, info: strawberry.types.Info, id: IDType):
        from .roleGQLModel import resolve_roles_on_user, resolve_roles_on_group
        from ._GraphPermissions import RBACPermission
        awaitableresult0 = resolve_roles_on_user(None, info, user_id=id)
        awaitableresult1 = resolve_roles_on_group(None, info, group_id=id)
        result0, result1 = await asyncio.gather(awaitableresult0, awaitableresult1)
        roles = [*result0, *result1]
        allRoleTypes = await RBACPermission.getAllRoles(info=info)
        index = {roleType["id"]: roleType for roleType in allRoleTypes}
        extresult = [
            {
                "id": r.id,
                "user_id": r.user_id,
                "group_id": r.group_id,
                "roletype_id": r.roletype_id,
                "type": index[r.roletype_id]
            } for r in roles
        ]
        return extresult

    @classmethod
    async def resolve_reference(cls, info: strawberry.types.Info, id: IDType):
        from ..DBDefinitions import GroupModel
        from .groupGQLModel import GroupGQLModel
        from .userGQLModel import UserGQLModel
        if id is None: return None
                
        if isinstance(id, str): id = IDType(id)

        loaderU = UserGQLModel.getLoader(info)
        loaderG = GroupGQLModel.getLoader(info)
        futures = [loaderU.load(id), loaderG.load(id)]
        # rows = await asyncio.gather(*futures)

        urows = await futures[0]
        grows = await futures[1]
        if urows is None and grows is None:
            return None
        
        if urows == grows:
            raise Exception(f"RBACObjectGQLModel.resolve_reference: id {id} is both User and Group")
        
        if isinstance(grows, GroupModel):
            asGroup = True
            asUser = False
            # print(f"RBACObjectGQLModel.resolve_reference: asGroup={grows}, id={id}", flush=True)
        else: 
            asGroup = False
            asUser = True
            # print(f"RBACObjectGQLModel.resolve_reference: asUser={urows}, id={id}", flush=True)

        
        # print(f"RBACObjectGQLModel.resolve_reference: asUser={asUser}, asGroup={asGroup}, id={id}", flush=True)
        # print(f"RBACObjectGQLModel.resolve_reference: {urows} ({id} {type(id)})", flush=True)
        # if asUser is None and asGroup is None: return None
        if not asUser and not asGroup:
            return None
        result = RBACObjectGQLModel(id=id, asGroup=asGroup, asUser=asUser)
        # result.id = id
        # result._data = None
        return result

    @strawberry.field(
        description="Roles associated with this RBAC",
        permission_classes=[OnlyForAuthentized])
    async def roles(
        self, 
        info: strawberry.types.Info,
        user_id: Annotated[Optional[IDType], strawberry.argument(description="if defined, only roles with this user will be returned")] = None
        ) -> List["RoleGQLModel"]:
        from .roleGQLModel import resolve_roles_on_user, resolve_roles_on_group, RoleGQLModel
        result = []
        if self.asUser:
            result = await resolve_roles_on_user(self, info, user_id=self.id, filter_user_id=user_id)
        if self.asGroup:
            result = await resolve_roles_on_group(self, info, group_id=self.id, filter_user_id=user_id)
        result = (
            RoleGQLModel.from_dataclass(r) 
            # for result in results
            for r in result
            )
        return result
    
    @strawberry.field(
        description="Roles associated with this RBAC for logged (asking) user",
        permission_classes=[OnlyForAuthentized])
    async def current_user_roles(
        self, 
        info: strawberry.types.Info
        ) -> List["RoleGQLModel"]:
        user = getUserFromInfo(info=info)
        user_id = user["id"]
        # print(f"current_user_roles.user type {type(user_id)}")
        from .roleGQLModel import resolve_roles_on_user, resolve_roles_on_group, RoleGQLModel
        result = []
        if self.asUser:
            result = await resolve_roles_on_user(self, info, user_id=self.id, filter_user_id=user_id)
        if self.asGroup:
            result = await resolve_roles_on_group(self, info, group_id=self.id, filter_user_id=user_id)
        result = (
            RoleGQLModel.from_dataclass(r) 
            # for result in results
            for r in result
            )
        return result
    


    @strawberry.field(
        description="""If logged user is authorized to operation on rbacobject_id""",
        permission_classes=[OnlyForAuthentized])
    async def user_can_with_state(self, 
            info: strawberry.types.Info, 
            access: StateDataAccessType, 
            state_id: uuid.UUID, 
            user_id: Optional[uuid.UUID] = None) -> Optional[bool]:
        # user = getUserFromInfo(info=info)
        _user_id = getUserFromInfo(info=info)["id"] if user_id is None else user_id

        _rbacobject_id = self.id # uuid.UUID(rbacobject_id) if type(rbacobject_id) == str else rbacobject_id
        rbacroles = await RBACObjectGQLModel.resolve_roles(info=info, id=_rbacobject_id)
        rbacroletype_ids = set(rbacrole["roletype_id"] for rbacrole in rbacroles if rbacrole["user_id"] == _user_id)
        print(f"rbacroletype_ids {rbacroletype_ids}", flush=True)

        loader = StateGQLModel.getLoader(info=info)
        state = await loader.load(id=state_id)

        roletypes = await StateGQLModel.resolve_roletypes(state=state, info=info, access=access)
        roletypes_ids = set(roletype.type_id for roletype in roletypes)
        print(f"roletypes_ids {roletypes_ids}", flush=True)
        intersection = roletypes_ids.intersection(rbacroletype_ids)
        print(f"intersection {intersection}", flush=True)
        return len(intersection) > 0

    @strawberry.field(
        description="""If logged user is authorized to operation on rbacobject_id""",
        permission_classes=[OnlyForAuthentized])
    async def user_can_without_state(self, 
            info: strawberry.types.Info, 
            roles_needed: List[str], # = strawberry.argument(description="role type names needed to have access"),
            # setthistottrue: bool,
            # strawberry.types.StrawberryArgument(description="roles needed to have access", ),           
            user_id: Optional[uuid.UUID] = None) -> Optional[bool]:
        from .roleTypeGQLModel import RoleTypeGQLModel
        loader = RoleTypeGQLModel.getLoader(info=info)

        _user_id = getUserFromInfo(info=info)["id"] if user_id is None else user_id
        # print(f"user_can_without_state called with roles_needed={roles_needed} and user_id={user_id} / _user_id={_user_id}", flush=True)
        # print(f"self.asUser {self.asUser}, self.asGroup {self.asGroup}", flush=True)
        from .roleGQLModel import resolve_roles_on_user, resolve_roles_on_group
        rbac_roles = []
        if self.asUser:
            rbac_roles = await resolve_roles_on_user(self, info, user_id=self.id, filter_user_id=_user_id)
            # rbac_roles = list(rbac_roles)
            # print(f"rbac_roles {self.id} roles_needed {roles_needed} rbac_roles {rbac_roles}", flush=True)
        if self.asGroup:
            rbac_roles = await resolve_roles_on_group(self, info, group_id=self.id, filter_user_id=_user_id)        

        # 👇 ids of role types associated with this rbac and available for the user
        rbac_role_type_ids = (role.roletype_id for role in rbac_roles)

        # 👇 prepare load of role types associated with this rbac
        role_types = (loader.load(role_type_id) for role_type_id in rbac_role_type_ids)
        
        # 👇 wait for load ...
        role_types = await asyncio.gather(*role_types)

        # 👇 filter loaded to needed ...
        role_types_need = (role_type.name for role_type in role_types if (role_type.name in roles_needed))

        # 👇 is there any role ?
        first_role = next(role_types_need, None)
        return first_role is not None


    # @strawberry.field(
    #     description="Roles associated with this RBAC",
    #     permission_classes=[OnlyForAuthentized])
    # async def object(
    #     self, 
    #     info: strawberry.types.Info) -> Optional[Union["UserGQLModel", "GroupGQLModel"]]:
    #     if self.asGroup:
    #         return await GroupGQLModel.resolve_reference(info=info, id=self.id)
    #     if self.asUser:
    #         return await UserGQLModel.resolve_reference(info=info, id=self.id)
    #     return None
    

@strawberry.federation.type(keys=["id"])
class RBACObjectGQLModel(RBACObjectGQLInterface):
    pass


@strawberry.federation.type(keys=["id", "stateId"])
class RBACStateObjectGQLModel(RBACObjectGQLInterface):
    from .roleTypeGQLModel import RoleTypeGQLModel
    state_id: IDType = strawberry.field(description="state_id") # = resolve_id

    @strawberry.field(
        description="Roles associated with this RBAC for logged (asking) user",
        permission_classes=[OnlyForAuthentized])
    async def current_user_roles(
        self, 
        info: strawberry.types.Info
    ) -> List["RoleGQLModel"]:
        #TODO adapt it to use of state_id
        user = getUserFromInfo(info=info)
        user_id = user["id"]
        # print(f"current_user_roles.user type {type(user_id)}")
        from .roleGQLModel import resolve_roles_on_user, resolve_roles_on_group, RoleGQLModel
        result = []
        if self.asUser:
            result = await resolve_roles_on_user(self, info, user_id=self.id, filter_user_id=user_id)
        if self.asGroup:
            result = await resolve_roles_on_group(self, info, group_id=self.id, filter_user_id=user_id)
        result = (
            RoleGQLModel.from_dataclass(r) 
            # for result in results
            for r in result
            # TODO check if really works
            if r.valid
            )
        return result    
    
    # @strawberry.field(
    #     description="",
    #     permission_classes=[
    #         OnlyForAuthentized
    #     ]
    # )
    # async def roles(self, info: strawberry.types.Info) -> List[RoleTypeGQLModel]:
    #     loader = getLoadersFromInfo(info).RoleTypeListModel
    #     return []
    pass




@strawberry.field(
    description="""Finds a rbacobject by its id""",
    permission_classes=[OnlyForAuthentized])
async def rbac_by_id(
    self, info: strawberry.types.Info, id: IDType
) -> Optional["RBACObjectGQLModel"]:
    result = await RBACObjectGQLModel.resolve_reference(info=info, id=id)
    return result

from uoishelpers.resolvers import InputModelMixin, TreeInputStructureMixin
@strawberry.input(
    description="Define the initial state of RBAC object"
)
class RBACInputObject(TreeInputStructureMixin):
    from .groupGQLModel import GroupGQLModel
    from .roleGQLModel import RoleInsertGQLModel
    getLoader = GroupGQLModel.getLoader
    mastergroup_id: IDType = strawberry.field(description="Which group will rule this RBAC object")
    name: typing.Optional[str] = strawberry.field(description="Name", default="RBACObject")
    abbreviation: typing.Optional[str] = strawberry.field(description="abbreviation", default="RBACObject")
    roles: typing.Optional[typing.List[RoleInsertGQLModel]] = strawberry.field(description="roles on this rbacobject", default_factory=list)

    id: IDType = strawberry.field(description="Client generated id of this RBAC object")
    grouptype_id: strawberry.Private[IDType] = None
    rbacobject_id: strawberry.Private[IDType] = IDType("3ffbc624-fe29-4486-9a56-3bc6a4e5b576")
    path: strawberry.Private[str] = None
    createdby_id: strawberry.Private[IDType] = None


@strawberry.interface(description="RBAC mutations")
class RBACMutations:
    from .groupGQLModel import GroupGQLModel
    @strawberry.field(
        description="creates an rbac object based on group",
        permission_classes=[
            OnlyForAuthentized
        ],
        extensions=[
            UserRoleProviderExtension[InsertError, RBACObjectGQLModel](),
            RbacProviderExtension[InsertError, RBACObjectGQLModel](),
            LoadDataExtension[InsertError, RBACObjectGQLModel](
                getLoader=GroupGQLModel.getLoader,
                primary_key_name="mastergroup_id"
            )
        ]
    )
    async def rbac_insert(
        self, 
        info: strawberry.types.Info, 
        rbac: RBACInputObject,
        db_row: typing.Any,
        rbacobject_id: IDType,
        user_roles: typing.List[dict],
    ) -> typing.Union[RBACObjectGQLModel, InsertError[RBACObjectGQLModel]]:
        
        from .roleGQLModel import RoleGQLModel, RoleInsertGQLModel
        from .groupGQLModel import GroupGQLModel
        actinguser = getUserFromInfo(info)
        # print(f"actinguser {actinguser}")
        # "08912fe1-0d0b-48e4-b9e1-56b0350c653b"
        actinguser_id = actinguser["id"]
        rbac.grouptype_id = "3ffbc624-fe29-4486-9a56-3bc6a4e5b576"
        if len(rbac.roles) == 0:
            rbac.roles = [
                RoleInsertGQLModel(
                    user_id=actinguser_id,
                    group_id=rbac.id,
                    roletype_id=IDType("ced46aa4-3217-4fc1-b79d-f6be7d21c6b6"),
                )
            ]
        rbac.rbacobject_id = rbac.id
        result_group = await Insert[GroupGQLModel].DoItSafeWay(info, entity=rbac)
        if isinstance(result_group, InsertError):
            result = InsertError[RBACObjectGQLModel](
                msg=result_group.msg,
                code=result_group.code,
                location=result_group.location,
                _input=rbac
            )
            return result
        result = RBACObjectGQLModel(id=result_group.id, asGroup=True)
        return result
        

"""
mutation rbacinsert{
  rbacInsert(rbac: {
    mastergroupId: "04e93e6a-7180-4d01-a3e5-16790fe1498c",
    name: "rbacX",
    
  }) {
    __typename
    ...on InsertError {
      msg
      failed
      code
      location
      input
    }
    ...on RBACObjectGQLModel {
      id
      roles {
        id
        startdate
        enddate
        user {
          id
          email
        }
        group {
          id
          name
        }
      }
      
    }
  }
  
}
"""