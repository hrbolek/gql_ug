import uuid
import sqlalchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column

from .BaseModel import BaseModel

class StateMachineModel(BaseModel):
    __tablename__ = "statemachines"

    name: Mapped[str] = mapped_column(
        nullable=True, default=None,
        comment="Name of the state"
    )
    name_en: Mapped[str] = mapped_column(
        nullable=True, default=None,
        comment="English name of the state"
    )

    type_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("statemachinetypes.id"), index=True, nullable=True, default=None)
    
    states = relationship(
        "StateModel", 
        uselist=True, 
        
        init=True,
        cascade="save-update"
    )

    transitions = relationship(
        "StateTransitionModel", 
        uselist=True, 
        
        init=True,
        cascade="save-update"
    )