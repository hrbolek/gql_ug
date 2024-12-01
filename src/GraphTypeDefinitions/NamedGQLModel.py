import typing
import functools
import strawberry

from .BaseGQLModel import BaseGQLModel
from uoishelpers.gqlpermissions import OnlyForAuthentized

@strawberry.interface(description="base for types and categories")
class NamedGQLModel(BaseGQLModel):

    name: typing.Optional[str] = strawberry.field(
        description="type name",
        permission_classes=[OnlyForAuthentized]
        )
    
    name_en: typing.Optional[str] = strawberry.field(
        description="type name",
        permission_classes=[OnlyForAuthentized]
        )