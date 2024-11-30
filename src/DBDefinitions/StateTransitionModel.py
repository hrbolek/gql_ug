import sqlalchemy
from sqlalchemy.schema import Column
from sqlalchemy import Uuid, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column

from .BaseModel import BaseModel

class StateTransitionModel(BaseModel):
    """Represents transitions between states in a state machine."""

    __tablename__ = "statetransitions"

    name: Mapped[str] = mapped_column(String, comment="Name of state transition", nullable=True, default=None)
    name_en: Mapped[str] = mapped_column(String, comment="English name of state transition", nullable=True, default=None)

    source_id: Mapped[int] = mapped_column(ForeignKey("states.id"), index=True, nullable=True, default=None)
    target_id: Mapped[int] = mapped_column(ForeignKey("states.id"), index=True, nullable=True, default=None)
    statemachine_id: Mapped[int] = mapped_column(ForeignKey("statemachines.id"), index=True, nullable=True, default=None)