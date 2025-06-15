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

class GroupTypeModel(BaseModel):
    """group type"""

    __tablename__ = "grouptypes"


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

    # category_id: Mapped[int] = mapped_column(ForeignKey("groupcategories.id"), index=True, nullable=True, default=None)

    mastertype_id: Mapped[int] = mapped_column(ForeignKey("grouptypes.id"), index=True, nullable=True, default=None)

    mastertype = relationship(
        "GroupTypeModel",
        viewonly=True, 
        remote_side="GroupTypeModel.id",
        uselist=False,
        back_populates="subtypes",
    ) # https://docs.sqlalchemy.org/en/20/orm/self_referential.html

    subtypes = relationship(
        "GroupTypeModel", 
        back_populates="mastertype",
        uselist=True,
        init=True,
        cascade="save-update"
    ) # https://docs.sqlalchemy.org/en/20/orm/self_referential.html
