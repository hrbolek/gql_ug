import typing
import strawberry
import uuid
import asyncio
from typing import List, Annotated, Optional, Union

import strawberry.types
from .BaseGQLModel import BaseGQLModel, IDType
from uoishelpers.resolvers import createInputs

from ._GraphResolvers import resolve_id
from ._GraphPermissions import RoleBasedPermission, OnlyForAuthentized
from src.Dataloaders import getLoadersFromInfo as getLoader, getUserFromInfo
from .stateGQLModel import StateDataAccessType, StateGQLModel

RoleGQLModel = Annotated["RoleGQLModel", strawberry.lazy(".roleGQLModel")]

#@strawberry.federation.type(extend=False, keys=["id"])
@strawberry.federation.type(keys=["id"])
class RBACObjectGQLModel:

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
        from .groupGQLModel import GroupGQLModel
        from .userGQLModel import UserGQLModel
        if id is None: return None
                
        if isinstance(id, str): id = IDType(id)

        loaderU = UserGQLModel.getLoader(info)
        loaderG = GroupGQLModel.getLoader(info)
        futures = [loaderU.load(id), loaderG.load(id)]
        rows = await asyncio.gather(*futures)

        asUser = rows[0] is not None
        asGroup = rows[1] is not None

        if asUser is None and asGroup is None: return None
        
        result = RBACObjectGQLModel(asGroup=asGroup, asUser=asUser)
        result.id = id
        result._data = None
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

        from .roleGQLModel import resolve_roles_on_user, resolve_roles_on_group
        rbac_roles = []
        if self.asUser:
            rbac_roles = await resolve_roles_on_user(self, info, user_id=self.id, filter_user_id=_user_id)
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
    
@strawberry.field(
    description="""Finds a rbacobject by its id""",
    permission_classes=[OnlyForAuthentized])
async def rbac_by_id(
    self, info: strawberry.types.Info, id: IDType
) -> Optional["RBACObjectGQLModel"]:
    result = await RBACObjectGQLModel.resolve_reference(info=info, id=id)
    return result


