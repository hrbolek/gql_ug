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

    statemachine = relationship(
        "StateMachineModel", 
        back_populates="transitions"
    )
    source = relationship(
        "StateModel",
        foreign_keys=[source_id],
        back_populates="outgoing_transitions"
    )
    target = relationship(
        "StateModel",
        foreign_keys=[target_id],
        back_populates="incoming_transitions"
    )

    #b5d63c79-ccc1-43dc-b699-060679e8f255
    #01c2f968-0585-42ae-a949-13ab67097236