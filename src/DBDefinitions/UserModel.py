import datetime
import uuid
import sqlalchemy
from sqlalchemy import (
    Column,
    String,
    DateTime,
    Boolean,
    ForeignKey
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import func

from .BaseModel import BaseModel

class UserModel(BaseModel):
    """Manages data associated with a user."""

    __tablename__ = "users"

    name: Mapped[str] = mapped_column(comment="Name of the user", nullable=True, default=None)
    givenname: Mapped[str] = mapped_column(comment="First name of the user", nullable=True, default=None)
    middlename: Mapped[str] = mapped_column(comment="Middle name of the user", nullable=True, default=None)
    surname: Mapped[str] = mapped_column(comment="Surname of the user", nullable=True, default=None)

    email: Mapped[str] = mapped_column(nullable=True, default=None)
    startdate: Mapped[datetime.datetime] = mapped_column(comment="First date of user in the system", nullable=True, default=None)
    enddate: Mapped[datetime.datetime] = mapped_column(comment="Last date of user in the system", nullable=True, default=None)
    valid: Mapped[bool] = mapped_column(default=True, comment="If the user is still active", nullable=False)

    type_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("usertypes.id"), nullable=True, index=True, default=None)

    @hybrid_property
    def fullname(self) -> str:
        """Constructs the full name of the user."""
        parts = filter(None, [self.name, self.givenname, self.middlename, self.surname])
        return " ".join(parts)

    @fullname.expression
    def fullname(cls):
        """Defines how to query the full name in the database."""
        return (
            func.concat(
                func.coalesce(cls.name, ""),
                " ",
                func.coalesce(cls.givenname, ""),
                " ",
                func.coalesce(cls.middlename, ""),
                " ",
                func.coalesce(cls.surname, ""),
            )
        )

    memberships = relationship("MembershipModel", back_populates="user", foreign_keys="MembershipModel.user_id")
    roles = relationship("RoleModel", back_populates="user", foreign_keys="RoleModel.user_id")
    # groups = relationship("GroupModel", 
    #     secondary="join(MembershipModel, GroupModel, GroupModel.id==MembershipModel.group_id)",
    #     primaryjoin="UserModel.id==MembershipModel.user_id",
    #     secondaryjoin="GroupModel.id==MembershipModel.group_id",
    #     uselist=True,
    #     viewonly=True
    # )

