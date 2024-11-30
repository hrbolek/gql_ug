import sqlalchemy
from sqlalchemy.schema import Column
from sqlalchemy import Uuid, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from .BaseModel import BaseModel, UUIDFKey, UUIDColumn

def createTypeAndCategory(tableNamePrefix: str):
    "returns SQLModels named {tableNamePrefix}TypeModel, {tableNamePrefix}Category, describing tables {tableNamePrefix}types, {tableNamePrefix}categories "
    # https://stackoverflow.com/questions/5352781/how-to-set-class-names-dynamically
    prefixModelName = tableNamePrefix.capitalize()
    EntityTypeModelName = f"{prefixModelName}TypeModel"
    EntityCategoryModelName = f"{prefixModelName}CategoryModel"

    EntityTypeTableName = f"{tableNamePrefix}types"
    EntityCategoryTableName = f"{tableNamePrefix}categories"

    ECAttrs = {
        "__tablename__": EntityCategoryTableName,
        "name": Column(String, comment="name of category"),
        "name_en": Column(String, comment="english name of category"),

        "types": relationship(EntityTypeModelName, uselist=True, viewonly=True),
    }
    ETAttrs = {
        "__tablename__": EntityTypeTableName,
        "name": Column(String, comment="name of type"),
        "name_en": Column(String, comment="english name of type"),

        "category_id": Column(ForeignKey(f"{EntityCategoryTableName}.id"), index=True, nullable=True),
        "category": relationship(EntityCategoryModelName, viewonly=True)
    }

    EntityCategoryModel = type(
        EntityCategoryModelName,
        (BaseModel, ),
        ECAttrs
    )

    EntityTypeModel = type(
        EntityTypeModelName,
        (BaseModel, ),
        ETAttrs
    )
    # class EntityCategoryModel(BaseModel):
    #     __tablename__ = EntityCategoryTableName

    #     name = Column(String, comment="name of category")
    #     name_en = Column(String, comment="english name of category")

    #     types = relationship(EntityTypeModelName, uselist=True, viewonly=True)

    # class EntityTypeModel(BaseModel):
    #     __tablename__ = EntityTypeTableName

    #     name = Column(String, comment="name of type")
    #     name_en = Column(String, comment="english name of type")

    #     category_id = Column(ForeignKey(f"{EntityCategoryTableName}.id"), index=True, nullable=True)

    #     category = relationship(EntityCategoryModelName, viewonly=True)

    # EntityTypeModel.__name__ = EntityTypeModelName
    # EntityCategoryModel.__name__ = EntityCategoryModelName
    
    return EntityTypeModel, EntityCategoryModel