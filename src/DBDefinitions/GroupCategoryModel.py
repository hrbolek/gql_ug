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

class GroupCategoryModel(BaseModel):
    """group category"""

    __tablename__ = "groupcategories2"


    name: Mapped[str] = mapped_column(
        nullable=True, default=None,
        comment="Name of the category"
    )
    name_en: Mapped[str] = mapped_column(
        nullable=True, default=None,
        comment="English name of the category"
    )
