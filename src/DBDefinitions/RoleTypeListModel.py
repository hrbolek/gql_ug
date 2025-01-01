import uuid
import sqlalchemy
from sqlalchemy import (
    Column,
    String,
    ForeignKey,
    DateTime,
    Boolean,
)
from sqlalchemy.orm import relationship, mapped_column, Mapped

from .BaseModel import BaseModel, UUIDFKey, UUIDColumn


class RoleTypeListModel(BaseModel):
    """Urcuje typ role (Vedouci katedry, dekan apod.)"""

    __tablename__ = "roletypelists"
    # id = None
    # pk_id: Mapped[uuid.UUID] = UUIDColumn(index=True, primary_key=True, default_factory=uuid.uuid4)
    type_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("roletypes.id"), index=True, nullable=True, default=None)
    list_id: Mapped[uuid.UUID] = UUIDFKey(comment="list which item belongs to")#Column(ForeignKey("users.id"), index=True, nullable=True)

