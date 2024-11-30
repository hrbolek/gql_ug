import uuid
import sqlalchemy
from sqlalchemy.schema import Column
from sqlalchemy import Uuid, String, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column

from .BaseModel import BaseModel, UUIDFKey

class StateModel(BaseModel):
    """Represents a state with localized names and order."""

    __tablename__ = "states"

    name: Mapped[str] = mapped_column(comment="Name of the type", nullable=True, default=None)
    name_en: Mapped[str] = mapped_column(comment="English name of the type", nullable=True, default=None)
    order: Mapped[int] = mapped_column(
        Integer, 
        comment="Determines order of states", 
        server_default="0", 
        nullable=False,
        default=0
    )

    statemachine_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("statemachines.id"), index=True, nullable=True, default=None)

    readerslist_id: Mapped[uuid.UUID] = UUIDFKey(comment="who can read item in this state", default=uuid.uuid4)
    writerslist_id: Mapped[uuid.UUID] = UUIDFKey(comment="who can update item in this state", default=uuid.uuid4)

    statemachine = relationship("StateMachineModel", back_populates="states")