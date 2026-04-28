import strawberry
import datetime
import typing
import uuid
import asyncio

from typing import Annotated
from enum import Enum    

import strawberry.types
from uoishelpers.resolvers import (
    VectorResolver, 
    PageResolver, 
    ScalarResolver,

    Insert, InsertError,
    Update, UpdateError,
    Delete, DeleteError,

    getLoadersFromInfo,
    getUserFromInfo
)
from uoishelpers.gqlpermissions import (
    OnlyForAuthentized,
    SimpleInsertPermission,
    SimpleUpdatePermission,
    SimpleDeletePermission
)
from .BaseGQLModel import BaseGQLModel, IDType
from .NamedGQLModel import NamedGQLModel

# from ._GraphPermissions import RoleBasedPermission, OnlyForAuthentized

RoleTypeGQLModel = Annotated["RoleTypeGQLModel", strawberry.lazy('.roleTypeGQLModel')]
# StateMachineTypeGQLModel = Annotated["RoleTypeGQLModel", strawberry.lazy('.roleTypeGQLModel')]

from dataclasses import dataclass
from uoishelpers.resolvers import createInputs2, ScalarResolver

@createInputs2
class StateMachineWhereFilter:
    name: str
    name_en: str
    id: IDType
    created: datetime.datetime
    type_id: IDType

@createInputs2
class StateWhereFilter:
    name: str
    name_en: str
    id: IDType
    created: datetime.datetime
    statemachine_id: IDType

@createInputs2
class StateTransitionWhereFilter:
    name: str
    name_en: str
    id: IDType
    created: datetime.datetime
    source_id: IDType
    target_id: IDType
    statemachine_id: IDType


@strawberry.federation.type(
    keys=["id"], description="""Entity representing a state machine"""
)
class StateMachineGQLModel(NamedGQLModel):
    """
    """
    @classmethod
    def getLoader(cls, info):
        return getLoadersFromInfo(info).StateMachineModel
  
    states: typing.List["StateGQLModel"] = strawberry.field(
        description="""All states associated with this state machine""",
        permission_classes=[
            OnlyForAuthentized
        ],
        resolver=VectorResolver["StateGQLModel"](fkey_field_name="statemachine_id", whereType=StateWhereFilter)
    )
    
    transitions: typing.List["StateTransitionGQLModel"] = strawberry.field(
        description="""All states associated with this state machine""",
        permission_classes=[
            OnlyForAuthentized
        ],
        resolver=VectorResolver["StateTransitionGQLModel"](fkey_field_name="statemachine_id", whereType=StateTransitionWhereFilter)
    )
    type_id: typing.Optional[IDType] = strawberry.field(
        description="""state machine type id""",
        permission_classes=[
            OnlyForAuthentized
        ],
        default=None
    )
    # type: typing.Optional[IDType] = strawberry.field(
    #     description="""state machine type""",
    #     permission_classes=[
    #         OnlyForAuthentized
    #     ],
    #     resolver=ScalarResolver["StateMachineTypeGQLModel"](fkey_field_name="type_id")
    # )

@strawberry.enum(description="")
class StateDataAccessType(Enum):
    READ = "read"
    WRITE = "write"


@strawberry.federation.type(
    keys=["id"], description="""Entity representing a state of state machine"""
)
class StateGQLModel(NamedGQLModel):
    """
    """
    @classmethod
    def getLoader(cls, info):
        return getLoadersFromInfo(info).StateModel
    
    statemachine_id: typing.Optional[IDType] = strawberry.field(
        description="""Id of state machine""",
        permission_classes=[OnlyForAuthentized],
        default=None
    )

    writerslist_id: typing.Optional[IDType] = strawberry.field(
        description="""Id of roletype list""",
        permission_classes=[OnlyForAuthentized],
        default=None
    )

    readerslist_id: typing.Optional[IDType] = strawberry.field(
        description="""Id of roletype list""",
        permission_classes=[OnlyForAuthentized],
        default=None
    )

    statemachine: typing.Optional["StateMachineGQLModel"] = strawberry.field(
        description="""Owing state machine""",
        permission_classes=[OnlyForAuthentized],
        resolver=ScalarResolver[StateMachineGQLModel](fkey_field_name="statemachine_id")
    )
    
    order: typing.Optional[int] = strawberry.field(
        description="""position in list of states""",
        permission_classes=[OnlyForAuthentized],
        default=None
    )
    
    sources: typing.List["StateTransitionGQLModel"] = strawberry.field(
        description="""Transitions linked into thist state""",
        permission_classes=[OnlyForAuthentized],
        # graphql_type=typing.List["StateTransitionGQLModel"],
        resolver=VectorResolver["StateTransitionGQLModel"](fkey_field_name="target_id", whereType=StateTransitionWhereFilter)
    )
    
    targets: typing.List["StateTransitionGQLModel"] = strawberry.field(
        description="""Transitions going out of this state""",
        permission_classes=[OnlyForAuthentized],
        # graphql_type=typing.List["StateTransitionGQLModel"],
        resolver=VectorResolver["StateTransitionGQLModel"](fkey_field_name="source_id", whereType=StateTransitionWhereFilter)
    )

    # @strawberry.field(
    #     description="""All roletypes associated with this state, all roles will be enabled for read""",
    #     permission_classes=[OnlyForAuthentized])
    # async def readersroletypes(self, info: strawberry.types.Info) -> typing.List["RoleTypeGQLModel"]:
    #     from .roleListGQLModel import RoleTypeListGQLModel
    #     from .roleGQLModel import RoleGQLModel
    #     loader = RoleTypeListGQLModel.getLoader(info)
    #     results = await loader.filter_by(list_id=self.readerslist_id)
    #     awaitables = (RoleGQLModel.resolve_reference(info, id=r.roletype_id) for r in results)
    #     return await asyncio.gather(*awaitables)

    # @strawberry.field(
    #     description="""All roletypes associated with this state, all roles will be enabled for update""",
    #     permission_classes=[OnlyForAuthentized])
    # async def writersroletypes(self, info: strawberry.types.Info, access: typing.Optional[StateDataAccessType] = StateDataAccessType.READ) -> typing.List["RoleTypeGQLModel"]:

    #     from .roleListGQLModel import RoleTypeListGQLModel
    #     from .roleGQLModel import RoleGQLModel

    #     loader = RoleTypeListGQLModel.getLoader(info)
    #     if access == StateDataAccessType.READ:
    #         results = await loader.filter_by(list_id=self.readerslist_id)
    #     else:
    #         results = await loader.filter_by(list_id=self.writerslist_id)
    #     awaitables = (RoleGQLModel.resolve_reference(info, id=r.roletype_id) for r in results)
    #     return await asyncio.gather(*awaitables)

    readerslist_id: typing.Optional[IDType] = strawberry.field(
        description="list of roles which can read at this state",
        permission_classes=[OnlyForAuthentized],
        default=None
    )

    # @strawberry.field(
    #     description="""All roletypes associated with this state, all roles will be enabled for update""",
    #     permission_classes=[OnlyForAuthentized])
    # async def readers(self, info: strawberry.types.Info) -> typing.List["RoleTypeGQLModel"]:
    #     from .roleListGQLModel import RoleTypeListGQLModel
    #     from .roleTypeGQLModel import RoleTypeGQLModel

    #     loader = RoleTypeListGQLModel.getLoader(info)
    #     results = await loader.filter_by(list_id=self.readerslist_id)
    #     awaitables = (RoleTypeGQLModel.resolve_reference(info, id=r.type_id) for r in results)
    #     return await asyncio.gather(*awaitables)
    
    # writerslist_id: typing.Optional[IDType] = strawberry.field(
    #     description="list of roles which can write at this state",
    #     permission_classes=[OnlyForAuthentized]
    # )

    @classmethod
    async def resolve_roletypes(cls, state, info: strawberry.types.Info, access: typing.Optional[StateDataAccessType] = StateDataAccessType.READ) -> typing.List["RoleTypeGQLModel"]:
        from .roleListGQLModel import RoleTypeListGQLModel
        loader = RoleTypeListGQLModel.getLoader(info)
        if access == StateDataAccessType.READ:
            if state.readerslist_id is None:
                results = []
            else:
                results = await loader.filter_by(id=state.readerslist_id)
        else:
            if state.writerslist_id is None:
                results = []
            else:
                results = await loader.filter_by(id=state.writerslist_id)
        return results

    @strawberry.field(
        description="""All roletypes associated with this state, all roles will be enabled for update""",
        permission_classes=[OnlyForAuthentized])
    async def roletypes(self, info: strawberry.types.Info, access: typing.Optional[StateDataAccessType] = StateDataAccessType.READ) -> typing.List["RoleTypeGQLModel"]:
        # from .roleListGQLModel import RoleTypeListGQLModel
        from .roleTypeGQLModel import RoleTypeGQLModel
        # loader = RoleTypeListGQLModel.getLoader(info)
        # if access == StateDataAccessType.READ:
        #     results = await loader.filter_by(list_id=self.readerslist_id)
        # else:
        #     results = await loader.filter_by(list_id=self.writerslist_id)
        # awaitables = (RoleTypeGQLModel.resolve_reference(info, id=r.type_id) for r in results)
        # return await asyncio.gather(*awaitables)
        
        results = await StateGQLModel.resolve_roletypes(state=self, info=info, access=access)
        awaitables = (RoleTypeGQLModel.resolve_reference(info, id=r.type_id) for r in results)
        return await asyncio.gather(*awaitables)


    @strawberry.field(
        description="""If logged user is authorized to operation on rbacobject_id""",
        permission_classes=[OnlyForAuthentized])
    async def user_can(self, info: strawberry.types.Info, access: StateDataAccessType, rbacobject_id: IDType, user_id: typing.Optional[IDType] = None ) -> typing.Optional[bool]:
        from .RBACObjectGQLModel import RBACObjectGQLModel
        # user = getUserFromInfo(info=info)
        _user_id = getUserFromInfo(info=info)["id"] if user_id is None else user_id
        roletypes = await StateGQLModel.resolve_roletypes(state=self, info=info, access=access)
        roletypes_ids = set(roletype.type_id for roletype in roletypes)
        print(f"roletypes_ids {roletypes_ids}", flush=True)
        _rbacobject_id = IDType(rbacobject_id) if type(rbacobject_id) == str else rbacobject_id
        rbacroles = await RBACObjectGQLModel.resolve_roles(info=info, id=_rbacobject_id)
        rbacroletype_ids = set(rbacrole["roletype_id"] for rbacrole in rbacroles if rbacrole["user_id"] == _user_id)
        print(f"rbacroletype_ids {rbacroletype_ids}", flush=True)
        intersection = roletypes_ids.intersection(rbacroletype_ids)
        print(f"intersection {intersection}", flush=True)
        return len(intersection) > 0
        
@strawberry.federation.type(
    keys=["id"], description="""Entity representing an entity type"""
)
class StateTransitionGQLModel(NamedGQLModel):
    """
    """
    @classmethod
    def getLoader(cls, info):
        return getLoadersFromInfo(info).StateTransitionModel
    
    source_id: typing.Optional[IDType] = strawberry.field(
        description="",
        permission_classes=[OnlyForAuthentized]
    )

    source: typing.Optional["StateGQLModel"] = strawberry.field(
        description="""Going from state""",
        permission_classes=[OnlyForAuthentized],
        resolver=ScalarResolver["StateGQLModel"](fkey_field_name="source_id")
    )
    
    target_id: typing.Optional[IDType] = strawberry.field(
        description="",
        permission_classes=[OnlyForAuthentized]
    )

    target: typing.Optional["StateGQLModel"] = strawberry.field(
        description="""Going to state""",
        permission_classes=[OnlyForAuthentized],
        resolver=ScalarResolver["StateGQLModel"](fkey_field_name="target_id")
    )
    
    statemachine_id: typing.Optional[IDType] = strawberry.field(
        description="",
        permission_classes=[OnlyForAuthentized]
    ) 
    
    statemachine: typing.Optional["StateMachineGQLModel"] = strawberry.field(
        description="""Owing state machine""",
        permission_classes=[OnlyForAuthentized],
        resolver=ScalarResolver["StateMachineGQLModel"](fkey_field_name="statemachine_id")
    )
    
#############################################################
#
# Queries
#
#############################################################



# from src.DBResolvers import (
#     StateResolvers,
#     StateMachineResolvers,
#     StatemachineTypeResolvers,
#     StatemachineCategoryResolvers,
#     StateTransitionResolvers
# )

@strawberry.interface(description="State related queries")
class StateQueries:
    state_page: typing.List["StateGQLModel"] = strawberry.field(
        description="all states",
        permission_classes=[OnlyForAuthentized],
        graphql_type=typing.List[StateGQLModel],
        resolver=PageResolver["StateGQLModel"](whereType=StateWhereFilter)
    )

    state_by_id = strawberry.field(
        description="one state",
        permission_classes=[OnlyForAuthentized],
        graphql_type=typing.Optional[StateGQLModel],
        # resolver=StateResolvers.ById(GQLModel=StateGQLModel)
        # resolver=default_by_id_resolver(),
        resolver=StateGQLModel.load_with_loader
    )

@strawberry.interface(description="State machine related queries")
class StateMachineQueries:
    statemachine_page = strawberry.field(
        description="all state machines",
        permission_classes=[OnlyForAuthentized],
        graphql_type=typing.List[StateMachineGQLModel],
        resolver=PageResolver[StateMachineGQLModel](whereType=StateMachineWhereFilter)
    )

    statemachine_by_id = strawberry.field(
        description="one state machine",
        permission_classes=[OnlyForAuthentized],
        graphql_type=typing.Optional[StateMachineGQLModel],
        # resolver=StateMachineResolvers.ById(GQLModel=StateMachineGQLModel)
        # resolver=default_by_id_resolver()
        resolver=StateMachineGQLModel.load_with_loader
    )

@strawberry.interface(description="State transition related queries")
class StateTransitionsQueries:
    statetransition_page = strawberry.field(
        description="all state transitions",
        permission_classes=[OnlyForAuthentized],
        graphql_type=typing.List[StateTransitionGQLModel],
        resolver=PageResolver[StateTransitionGQLModel](whereType=StateTransitionWhereFilter)
    )

    statetransition_by_id = strawberry.field(
        description="one state transition",
        permission_classes=[OnlyForAuthentized],
        graphql_type=typing.Optional[StateTransitionGQLModel],
        # resolver=StateTransitionResolvers.ById(GQLModel=StateTransitionGQLModel)
        # resolver=default_by_id_resolver()
        resolver=StateTransitionGQLModel.load_with_loader
    )

#############################################################
#
# Mutations
#
#############################################################
from uoishelpers.resolvers import InputModelMixin

from uoishelpers.gqlpermissions.LoadDataExtension import LoadDataExtension
from uoishelpers.gqlpermissions.RbacProviderExtension import RbacProviderExtension
from uoishelpers.gqlpermissions.RbacInsertProviderExtension import RbacInsertProviderExtension
from uoishelpers.gqlpermissions.UserRoleProviderExtension import UserRoleProviderExtension
from uoishelpers.gqlpermissions.UserAccessControlExtension import UserAccessControlExtension


@strawberry.input(description="Input structure - C operation")
class StatetransitionInsertGQLModel(InputModelMixin):
    getLoader = StateTransitionGQLModel.getLoader
    name: str = strawberry.field(description="name")   
    statemachine_id: IDType = strawberry.field(description="id of state machine", default=None)
    source_id: IDType = strawberry.field(description="id of state source")
    target_id: IDType = strawberry.field(description="id of state target")
    id: typing.Optional[IDType] = strawberry.field(description="primary key (UUID), could be client generated", default=None)
    name_en: typing.Optional[str] = strawberry.field(description="eng. name", default=None)   
    
    rbacobject_id: strawberry.Private[IDType] = None 
    createdby_id: strawberry.Private[IDType] = None 

@strawberry.input(description="Update structure - C operation")
class StatetransitionUpdateGQLModel:
    lastchange: datetime.datetime = strawberry.field(description="timestamp of last change = TOKEN")
    id: IDType = strawberry.field(description="primary key (UUID), identifies object of operation")

    name: typing.Optional[str] = strawberry.field(description="name", default=None)   
    name_en: typing.Optional[str] = strawberry.field(description="eng. name", default=None)   
    source_id: typing.Optional[IDType] = strawberry.field(description="id of state source", default=None)
    target_id: typing.Optional[IDType] = strawberry.field(description="id of state target", default=None)
    changedby_id: strawberry.Private[IDType] = None

@strawberry.input(description="Delete structure - D operation")
class StatetransitionDeleteGQLModel:
    lastchange: datetime.datetime = strawberry.field(description="timestamp of last change = TOKEN")
    id: IDType = strawberry.field(description="primary key (UUID), identifies object of operation")

@strawberry.input(description="Input structure - C operation")
class StatemachineInsertGQLModel(InputModelMixin):
    getLoader = StateMachineGQLModel.getLoader
    name: str = strawberry.field(description="name")   
    rbacobject_id: IDType = strawberry.field(
        description="who can access, crucial identificator, group.id is expected, must exists", 
        default=None
    )
    name_en: typing.Optional[str] = strawberry.field(description="name", default=None)   
    id: typing.Optional[IDType] = strawberry.field(description="primary key (UUID), could be client generated", default=None)
    states: typing.Optional[typing.List["StateInsertGQLModel"]] = strawberry.field(
        description="list states to be part of state machine", 
        default_factory=list
    )
    transitions: typing.Optional[typing.List["StatetransitionInsertGQLModel"]] = strawberry.field(
        description="list transitions to be part of state machine", 
        default_factory=list
    )
    createdby_id: strawberry.Private[IDType] = None 

@strawberry.input(description="Update structure - C operation")
class StatemachineUpdateGQLModel:
    lastchange: datetime.datetime = strawberry.field(description="timestamp of last change = TOKEN")
    id: IDType = strawberry.field(description="primary key (UUID), identifies object of operation")
    name: typing.Optional[str] = strawberry.field(description="name", default=None)   
    name_en: typing.Optional[str] = strawberry.field(description="eng. name", default=None)   
    changedby_id: strawberry.Private[IDType] = None
    
@strawberry.input(description="Delete structure - C operation")
class StatemachineDeleteGQLModel:
    lastchange: datetime.datetime = strawberry.field(description="timestamp of last change = TOKEN")
    id: IDType = strawberry.field(description="primary key (UUID), identifies object of operation")
    
@strawberry.interface(description="State machine related mutations")
class StateMachineMutations:
    
    @strawberry.mutation(
        description="Inserts new StateMachine - C operation",
        permission_classes=[
            OnlyForAuthentized,
            # SimpleInsertPermission[StateMachineGQLModel](roles=["administrátor"])
        ],
        extensions=[
            UserAccessControlExtension[InsertError, StateMachineGQLModel](roles=["administrátor"]),
            UserRoleProviderExtension[InsertError, StateMachineGQLModel](),
            RbacInsertProviderExtension[InsertError, StateMachineGQLModel]()
        ]
    )
    async def statemachine_insert(
        self, 
        info: strawberry.types.Info, 
        statemachine: StatemachineInsertGQLModel,
        user_roles: typing.List[dict],
        rbacobject_id: IDType
    ) -> typing.Union[StateMachineGQLModel, InsertError[StateMachineGQLModel]]:
        machineResult = await Insert[StateMachineGQLModel].DoItSafeWay(info=info, entity=statemachine)
        return machineResult

    @strawberry.mutation(
        description="U operation",
        permission_classes=[
            OnlyForAuthentized,
            # SimpleUpdatePermission[StateMachineGQLModel](roles=["administrátor"])
        ],
        extensions=[
            UserAccessControlExtension[UpdateError, StateMachineGQLModel](roles=["administrátor"]),
            UserRoleProviderExtension[UpdateError, StateMachineGQLModel](),
            RbacProviderExtension[UpdateError, StateMachineGQLModel](),
            LoadDataExtension[UpdateError, StateMachineGQLModel]()
        ]
    )
    async def statemachine_update(
        self, 
        info: strawberry.types.Info, 
        statemachine: StatemachineUpdateGQLModel,
        user_roles: typing.List[dict],
        rbacobject_id: IDType,
        db_row: typing.Any
    ) -> typing.Union[StateMachineGQLModel, UpdateError[StateMachineGQLModel]]:
        return await Update[StateMachineGQLModel].DoItSafeWay(info=info, entity=statemachine)

    @strawberry.mutation(
        description="U operation",
        permission_classes=[
            OnlyForAuthentized,
            SimpleDeletePermission[StateMachineGQLModel](roles=["admistrátor"])
            ],
        extensions=[
            UserAccessControlExtension[DeleteError, StateMachineGQLModel](roles=["administrátor"]),
            UserRoleProviderExtension[DeleteError, StateMachineGQLModel](),
            RbacProviderExtension[DeleteError, StateMachineGQLModel](),
            LoadDataExtension[DeleteError, StateMachineGQLModel]()
        ]
    )
    async def statemachine_delete(
        self, 
        info: strawberry.types.Info, 
        statemachine: StatemachineDeleteGQLModel,
        user_roles: typing.List[dict],
        rbacobject_id: IDType,
        db_row: typing.Any,
    ) -> typing.Optional[DeleteError[StateMachineGQLModel]]:
        return await Delete[StateMachineGQLModel].DoItSafeWay(info=info, entity=statemachine)

from uoishelpers.gqlpermissions.RbacProviderExtension import MISSING
class RbacStateMachineProviderExtension(RbacProviderExtension):
    "gets rbacobject_id from existing StateMachineModel"
    async def provide_rbac_object_id(self, source, info: strawberry.types.Info, *args, **kwargs):
        input_params = next(iter(kwargs.values()), None)
        statemachine_id = input_params.statemachine_id
        loader = StateMachineGQLModel.getLoader(info)
        db_row = await loader.load(statemachine_id)
        if db_row is None:
            return MISSING
        rbacobject_id = getattr(db_row, "rbacobject_id", MISSING)
        if rbacobject_id is None:
            # QUESTION FOR STUDENTS: Why must be this?
            return MISSING
        return rbacobject_id



@strawberry.input(description="Input structure - C operation")
class StateInsertGQLModel(InputModelMixin):
    getLoader = StateGQLModel.getLoader
    name: str = strawberry.field(description="name")   
    statemachine_id: IDType = strawberry.field(
        description="id of machine whichs state belongs to", default=None)
    name_en: typing.Optional[str] = strawberry.field(description="eng. name", default=None)   
    order: typing.Optional[int] = strawberry.field(description="order of states", default=0)
    id: typing.Optional[IDType] = strawberry.field(description="primary key (UUID), could be client generated", default=None)

    rbacobject_id: strawberry.Private[IDType] = None 
    createdby_id: strawberry.Private[IDType] = None 
    readerslist_id: strawberry.Private[IDType] = None 
    writerslist_id: strawberry.Private[IDType] = None 

@strawberry.input(description="Input structure - U operation")
class StateUpdateGQLModel:
    lastchange: datetime.datetime = strawberry.field(description="timestamp of last change = TOKEN")
    id: IDType = strawberry.field(description="primary key (UUID), identifies object of operation")
    name: typing.Optional[str] = strawberry.field(description="name", default=None)   
    name_en: typing.Optional[str] = strawberry.field(description="eng. name", default=None)   
    order: typing.Optional[int] = strawberry.field(description="order of state", default=None)
    changedby_id: strawberry.Private[IDType] = None

@strawberry.input(description="Delete state")
class StateDeleteGQLModel:
    lastchange: datetime.datetime = strawberry.field(description="timestamp of last change = TOKEN")
    id: IDType = strawberry.field(description="primary key (UUID), identifies object of operation")

async def state_insert_internal(self, info: strawberry.types.Info, state: StateInsertGQLModel) -> typing.Union[StateGQLModel, InsertError[StateGQLModel]]:
    state.readerslist_id = uuid.uuid4()
    state.writerslist_id = uuid.uuid4()
    return await Insert[StateGQLModel].DoItSafeWay(info=info, entity=state)

@strawberry.interface(description="State related mutations")
class StateMutations:
    @strawberry.mutation(
        description="C operation",
        permission_classes=[OnlyForAuthentized],
        extensions=[
            UserAccessControlExtension[InsertError, StateGQLModel](roles=["administrátor"]),
            UserRoleProviderExtension[InsertError, StateGQLModel](),
            RbacStateMachineProviderExtension[InsertError, StateGQLModel](),
            # LoadDataExtension[InsertError, StateGQLModel]()
        ]
    )
    async def state_insert(
        self, 
        info: strawberry.types.Info, 
        state: StateInsertGQLModel,
        user_roles: typing.List[dict],
        rbacobject_id: IDType,
    ) -> typing.Union[StateGQLModel, InsertError[StateGQLModel]]:
        state.rbacobject_id = rbacobject_id
        # TODO: remove state_insert_internal, uuids generated at sql model
        return await state_insert_internal(self=self, info=info, state=state)

    @strawberry.mutation(
        description="U operation",
        permission_classes=[OnlyForAuthentized],
        extensions=[
            UserAccessControlExtension[UpdateError, StateGQLModel](roles=["administrátor"]),
            UserRoleProviderExtension[UpdateError, StateGQLModel](),
            RbacProviderExtension[UpdateError, StateGQLModel](),
            LoadDataExtension[UpdateError, StateGQLModel]()
        ]
    )
    async def state_update(
        self, 
        info: strawberry.types.Info, 
        state: StateUpdateGQLModel,
        user_roles: typing.List[dict],
        rbacobject_id: IDType,
        db_row: typing.Any,
    ) -> typing.Union[StateGQLModel, UpdateError[StateGQLModel]]:
        return await Update[StateGQLModel].DoItSafeWay(info=info, entity=state)

    @strawberry.mutation(
        description="D operation",
        permission_classes=[OnlyForAuthentized],
        extensions=[
            UserAccessControlExtension[DeleteError, StateGQLModel](roles=["administrátor"]),
            UserRoleProviderExtension[DeleteError, StateGQLModel](),
            RbacProviderExtension[DeleteError, StateGQLModel](),
            LoadDataExtension[DeleteError, StateGQLModel]()
        ]
    )
    async def state_delete(
        self, 
        info: strawberry.types.Info, 
        state: StateDeleteGQLModel,
        user_roles: typing.List[dict],
        rbacobject_id: IDType,
        db_row: typing.Any,
    ) -> typing.Optional[DeleteError[StateGQLModel]]:
        return await Delete[StateGQLModel].DoItSafeWay(info=info, entity=state)


async def statetransition_insert_internal(self, info: strawberry.types.Info, statetransition: StatetransitionInsertGQLModel) -> typing.Union[StateTransitionGQLModel, InsertError[StateTransitionGQLModel]]:
    return await Insert[StateTransitionGQLModel].DoItSafeWay(info=info, entity=statetransition)

@strawberry.interface(description="State transitions related mutations")
class StateTransitionMutations:
    @strawberry.mutation(
        description="C operation",
        permission_classes=[OnlyForAuthentized],
        extensions=[
            UserAccessControlExtension[InsertError, StateTransitionGQLModel](roles=["administrátor"]),
            UserRoleProviderExtension[InsertError, StateTransitionGQLModel](),
            RbacStateMachineProviderExtension[InsertError, StateTransitionGQLModel](),
            # LoadDataExtension[InsertError, StateTransitionGQLModel]()
        ]
    )
    async def statetransition_insert(
        self, 
        info: strawberry.types.Info, 
        statetransition: StatetransitionInsertGQLModel,
        user_roles: typing.List[dict],
        rbacobject_id: IDType,
        # db_row: typing.Any,
    ) -> typing.Union[StateTransitionGQLModel, InsertError[StateTransitionGQLModel]]:
        statetransition.rbacobject_id = rbacobject_id
        return await statetransition_insert_internal(self=self, info=info, statetransition=statetransition)

    @strawberry.mutation(
        description="U operation",
        permission_classes=[OnlyForAuthentized],
        extensions=[
            UserAccessControlExtension[UpdateError, StateTransitionGQLModel](roles=["administrátor"]),
            UserRoleProviderExtension[UpdateError, StateTransitionGQLModel](),
            RbacProviderExtension[UpdateError, StateTransitionGQLModel](),
            LoadDataExtension[UpdateError, StateTransitionGQLModel]()
        ]
    )
    async def statetransition_update(
        self, 
        info: strawberry.types.Info, 
        statetransition: StatetransitionUpdateGQLModel,
        user_roles: typing.List[dict],
        rbacobject_id: IDType,
        db_row: typing.Any,
    ) -> typing.Union[StateTransitionGQLModel, UpdateError[StateTransitionGQLModel]]:
        return await Update[StateTransitionGQLModel].DoItSafeWay(info=info, entity=statetransition)

    @strawberry.mutation(
        description="D operation",
        permission_classes=[OnlyForAuthentized],
        extensions=[
            UserAccessControlExtension[DeleteError, StateTransitionGQLModel](roles=["administrátor"]),
            UserRoleProviderExtension[DeleteError, StateTransitionGQLModel](),
            RbacProviderExtension[DeleteError, StateTransitionGQLModel](),
            LoadDataExtension[DeleteError, StateTransitionGQLModel]()
        ]
    )
    async def statetransition_delete(
        self, 
        info: strawberry.types.Info, 
        statetransition: StatetransitionDeleteGQLModel,
        user_roles: typing.List[dict],
        rbacobject_id: IDType,
        db_row: typing.Any,
    ) -> typing.Optional[DeleteError[StateTransitionGQLModel]]:
        return await Delete[StateTransitionGQLModel].DoItSafeWay(info=info, entity=statetransition)

