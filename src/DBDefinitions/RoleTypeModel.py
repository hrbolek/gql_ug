import sqlalchemy
from sqlalchemy import (
    Column,
    String,
    ForeignKey,
    DateTime,
    Boolean,
)
from sqlalchemy.orm import relationship, mapped_column, Mapped

from .BaseModel import BaseModel

class RoleTypeModel(BaseModel):
    """role type"""

    __tablename__ = "roletypes"

    path_attribute_name = "path"
    parent_attribute_name = "mastertype"
    parent_id_attribute_name = "mastertype_id"
    children_attribute_name = "subtypes"

    # Materialized path technique
    path: Mapped[str] = mapped_column(
        index=True,
        nullable=True,
        default=None,
        comment="Materialized path technique, not implemented"
    )

    name: Mapped[str] = mapped_column(
        nullable=True, default=None,
        comment="Name of the type"
    )
    name_en: Mapped[str] = mapped_column(
        nullable=True, default=None,
        comment="English name of the type"
    )

    # category_id: Mapped[int] = mapped_column(ForeignKey("rolecategories.id"), index=True, nullable=True, default=None)
    # category = relationship("RoleCategoryModel", uselist=False, viewonly=True)

    mastertype_id: Mapped[int] = mapped_column(ForeignKey("roletypes.id"), index=True, nullable=True, default=None)

    mastertype = relationship(
        "RoleTypeModel",
        viewonly=True, 
        remote_side="RoleTypeModel.id",
        uselist=False,
        back_populates="subtypes",
    ) # https://docs.sqlalchemy.org/en/20/orm/self_referential.html

    subtypes = relationship(
        "RoleTypeModel", 
        back_populates="mastertype",
        uselist=True,
        init=True,
        cascade="save-update"
    ) # https://docs.sqlalchemy.org/en/20/orm/self_referential.html
