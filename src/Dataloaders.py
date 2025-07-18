import logging
from uoishelpers.dataloaders import createIdLoader
import uuid
import src.DBDefinitions
from src.DBDefinitions import (
    BaseModel,
    UserModel,
    MembershipModel,
    GroupModel,
    GroupTypeModel,
    GroupCategoryModel,
    RoleModel,
    RoleTypeModel,
    RoleCategoryModel,
    RoleTypeListModel,
    StateMachineModel,
    StateMachineTypeModel,
    StateMachineCategoryModel,
    StateModel,
    StateTransitionModel,


)

# from uoishelpers.resolvers import select, update, delete

from uoishelpers.dataloaders import createIdLoader
from uoishelpers.dataloaders.LoaderMapBase import LoaderMapBase
from uoishelpers.dataloaders.IDLoader import IDLoader
from functools import cache

class LoaderMap(LoaderMapBase[BaseModel]):
    """LoaderMap is a map of IDLoaders for all models in the BaseModel registry.
    It is used to create loaders for all models in the BaseModel registry.
    """
    BaseModel = BaseModel
    UserModel: IDLoader[src.DBDefinitions.UserModel] = None
    MembershipModel: IDLoader[src.DBDefinitions.MembershipModel] = None
    GroupModel: IDLoader[src.DBDefinitions.GroupModel] = None
    GroupTypeModel: IDLoader[src.DBDefinitions.GroupTypeModel] = None
    GroupCategoryModel: IDLoader[src.DBDefinitions.GroupCategoryModel] = None
    RoleModel: IDLoader[src.DBDefinitions.RoleModel] = None
    StateMachineModel: IDLoader[src.DBDefinitions.StateMachineModel] = None
    StateMachineTypeModel: IDLoader[src.DBDefinitions.StateMachineTypeModel] = None
    StateMachineCategoryModel: IDLoader[src.DBDefinitions.StateMachineCategoryModel] = None
    StateModel: IDLoader[src.DBDefinitions.StateModel] = None
    StateTransitionModel: IDLoader[src.DBDefinitions.StateTransitionModel] = None
    RoleTypeListModel: IDLoader[src.DBDefinitions.RoleTypeListModel] = None
    RoleTypeModel: IDLoader[src.DBDefinitions.RoleTypeModel] = None
    RoleCategoryModel: IDLoader[src.DBDefinitions.RoleCategoryModel] = None

    def __init__(self, session):
        super().__init__(session)
        self.UserModel = self.get(UserModel)
        self.MembershipModel = self.get(MembershipModel)
        self.GroupModel = self.get(GroupModel)
        self.GroupTypeModel = self.get(GroupTypeModel)
        self.GroupCategoryModel = self.get(GroupCategoryModel)
        self.RoleModel = self.get(RoleModel)
        self.RoleModel = self.get(RoleModel)
        self.StateMachineModel = self.get(StateMachineModel)
        self.StateMachineTypeModel = self.get(StateMachineTypeModel)
        self.StateMachineCategoryModel = self.get(StateMachineCategoryModel)
        self.StateModel = self.get(StateModel)
        self.StateTransitionModel = self.get(StateTransitionModel)
        self.RoleTypeListModel = self.get(RoleTypeListModel)
        self.RoleTypeModel = self.get(RoleTypeModel)
        self.RoleCategoryModel = self.get(RoleCategoryModel)
        # print(f"LoaderMap created with session: {session}")


def createLoaders(asyncSessionMaker):

    def createLambda(loaderName, DBModel):
        return lambda self: createIdLoader(asyncSessionMaker, DBModel)

    attrs = {}

    for DBModel in BaseModel.registry.mappers:
        cls = DBModel.class_
        attrs[cls.__tablename__] = property(cache(createLambda(asyncSessionMaker, cls)))
        attrs[cls.__name__] = attrs[cls.__tablename__]
    
    # attrs["authorizations"] = property(cache(lambda self: AuthorizationLoader()))
    Loaders = type('Loaders', (), attrs)   
    return Loaders()


def getUserFromInfo(info):
    context = info.context
    #print(list(context.keys()))
    result = context.get("user", None)
    if result is None:
        print(f"user in context is None {context}")
        request = context.get("request", None)
        assert request is not None, context
        result = request.scope.get("user", None)

    if result is None:
        result = {"id": None}
    else:
        result = {**result, "id": uuid.UUID(result["id"])}
    # logging.debug("getUserFromInfo", result)
    return result

def getLoadersFromInfo(info) -> LoaderMap:
    # print("info", info)
    context = info.context
    # print("context", context)
    loaders = context.get("loaders", None)
    assert loaders is not None, f"'loaders' key missing in context"
    return loaders

def createLoadersContext(asyncSessionMaker):
    return {
        "loaders": createLoaders(asyncSessionMaker)
    }

def createLoadersContext(session):
    return {
        "loaders": LoaderMap(session)
    }
