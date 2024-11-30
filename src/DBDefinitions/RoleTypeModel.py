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


    name: Mapped[str] = mapped_column(
        nullable=True, default=None,
        comment="Name of the type"
    )
    name_en: Mapped[str] = mapped_column(
        nullable=True, default=None,
        comment="English name of the type"
    )

    category_id: Mapped[int] = mapped_column(ForeignKey("rolecategories.id"), index=True, nullable=True, default=None)
