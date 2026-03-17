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
    # list_id: Mapped[uuid.UUID] = UUIDFKey(comment="list which item belongs to")#Column(ForeignKey("users.id"), index=True, nullable=True)
    list_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("roletypenamedlists.id"), index=True, nullable=True, default=None)
    
    # role_list = relationship(
    #     "RoleTypeNameListModel", 
    #     back_populates="role_types",
    #     uselist=False
    # )
    # roles = relationship(
    #     "RoleModel",
    #     uselist=True,
    #     init=True,
    #     cascade="save-update"
    # )
                               
class RoleTypeListNameModel(BaseModel):
    """Spojeni mezi typem role a seznamem roli."""

    __tablename__ = "roletypenamedlists"
    # id = None
    name: Mapped[str] = Column(String, nullable=True, default=None, comment="name of the role type list", index=True)

    role_types = relationship(
        "RoleTypeModel",
        uselist=True,
        secondary="roletypelists",
    )
