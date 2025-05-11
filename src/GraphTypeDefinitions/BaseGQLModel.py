import uuid
import datetime
import typing
import strawberry
import dataclasses

import strawberry.types
from uoishelpers.gqlpermissions import OnlyForAuthentized

IDType = uuid.UUID
UserGQLModel = typing.Annotated["UserGQLModel", strawberry.lazy(".userGQLModel")]
RBACObjectGQLModel = typing.Annotated["RBACObjectGQLModel", strawberry.lazy(".RBACObjectGQLModel")]


from strawberry.federation.schema_directive import schema_directive, Location
from strawberry.directive import DirectiveLocation
@schema_directive(
    repeatable=True,
    compose=True,
    description="Description for foreign keys",
    locations=[Location.INPUT_FIELD_DEFINITION, Location.FIELD_DEFINITION, DirectiveLocation.FIELD],
)
class Relation:
    """
    @relation(to: Typ, field: 'id')
    říká, že pole inputu je cizí klíč na zadaný typ.
    """
    to: str
    field: str = "id"

@classmethod
async def resolve_reference(cls, info: strawberry.types.Info, id: IDType, **otherData):
    _id = IDType(id) if isinstance(id, str) else id
    return None if id is None else cls(id=_id, **otherData)



@strawberry.federation.interface(
    description="""Technical base interface for all GraphQL objects.
Technický základní interface pro všechny GraphQL objekty."""
)
class BaseGQLModel:
    
    @classmethod
    def getLoader(cls, info: strawberry.types.Info):
        """Method that should be implemented in subclasses to provide a data loader."""
        raise NotImplementedError("Subclasses must implement getLoader method.")
    
    @classmethod
    def from_dataclass(cls, db_row):
        """Transforms a dataclass instance into a GraphQL model instance."""
        db_row_dict = dataclasses.asdict(db_row)
        instance = cls(**db_row_dict)
        return instance

    @classmethod
    async def load_with_loader(cls, info: strawberry.types.Info, id: uuid.UUID):
        """
        Loads an entity by its ID using the corresponding data loader.
        
        Načte entitu podle jejího ID pomocí příslušného datového loaderu.
        """
        if id is None:
            return None

        _id = IDType(id) if isinstance(id, str) else id
        loader = cls.getLoader(info=info)
        db_row = await loader.load(_id)
        
        return cls(id=_id) if db_row is None else cls.from_dataclass(db_row=db_row)
    
    @classmethod
    # def resolve_reference(cls, info: strawberry.types.Info, id: uuid.UUID, **otherdata):
    async def resolve_reference(cls, info: strawberry.types.Info, id: uuid.UUID):
        """
        Resolves a reference to this entity by its ID.
        
        Vyřeší referenci na tuto entitu pomocí jejího ID.
        """
        print(f"resolving reference for {cls} with id='{id}'")
        if id is None:
            return None
        _id = IDType(id) if isinstance(id, str) else id
        return await cls.load_with_loader(info=info, id=_id)
       
    id: IDType = strawberry.field(
        description="""Primary key of the entity.
Primární klíč entity.""", 
        permission_classes=[OnlyForAuthentized]
    )
    
    lastchange: typing.Optional[datetime.datetime] = strawberry.field(
        description="""Timestamp of the last change.
Časové razítko poslední změny.""", 
        default=None,
        permission_classes=[OnlyForAuthentized]
    )
    
    created: typing.Optional[datetime.datetime] = strawberry.field(
        description="""Date and time when the entity was created.
Datum a čas vytvoření entity.""", 
        default=None,
        permission_classes=[OnlyForAuthentized]
    )
    
    createdby_id: typing.Optional[IDType] = strawberry.field(
        description="""Identifier of the user who created this entity.
Identifikátor uživatele, který vytvořil tuto entitu.""", 
        default=None,
        permission_classes=[OnlyForAuthentized]
    )
    
    changedby_id: typing.Optional[IDType] = strawberry.field(
        description="""Identifier of the user who last modified this entity.
Identifikátor uživatele, který naposledy upravil tuto entitu.""", 
        default=None,
        permission_classes=[OnlyForAuthentized]
    )
    
    rbacobject_id: typing.Optional[IDType] = strawberry.field(
        description="""Reference to the RBAC object governing permissions.
Reference na RBAC objekt, který řídí oprávnění.""", 
        default=None,
        permission_classes=[OnlyForAuthentized]
    )

    @strawberry.field(
        description="""The user who created this entity.
Uživatel, který vytvořil tuto entitu.""",
        permission_classes=[OnlyForAuthentized]
    )
    async def createdby(self, info: strawberry.types.Info) -> typing.Optional["UserGQLModel"]:
        from .userGQLModel import UserGQLModel
        return None if self.createdby_id is None else await UserGQLModel.load_with_loader(info=info, id=self.createdby_id)

    @strawberry.field(
        description="""The user who last modified this entity.
Uživatel, který naposledy upravil tuto entitu.""",
        permission_classes=[OnlyForAuthentized]
    )
    async def changedby(self, info: strawberry.types.Info) -> typing.Optional["UserGQLModel"]:
        from .userGQLModel import UserGQLModel
        return None if self.changedby_id is None else await UserGQLModel.load_with_loader(info=info, id=self.changedby_id)

    @strawberry.field(
        description="""The RBAC object associated with this entity.
RBAC objekt spojený s touto entitou.""",
        permission_classes=[OnlyForAuthentized]
    )
    async def rbacobject(self, info: strawberry.types.Info) -> typing.Optional["RBACObjectGQLModel"]:
        from .RBACObjectGQLModel import RBACObjectGQLModel
        return None if self.rbacobject_id is None else await RBACObjectGQLModel.resolve_reference(info=info, id=self.rbacobject_id)