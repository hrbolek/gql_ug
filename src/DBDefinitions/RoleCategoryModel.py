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

class RoleCategoryModel(BaseModel):
    """role category"""

    __tablename__ = "rolecategories2"


    name: Mapped[str] = mapped_column(
        nullable=True, default=None,
        comment="Name of the category"
    )
    name_en: Mapped[str] = mapped_column(
        nullable=True, default=None,
        comment="English name of the category"
    )
