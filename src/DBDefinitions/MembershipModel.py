import sqlalchemy
from sqlalchemy import (
    Column,
    String,
    ForeignKey,
    DateTime,
    Boolean,
)
from sqlalchemy.orm import relationship

from .BaseModel import BaseModel
import datetime
from sqlalchemy.orm import relationship, Mapped, mapped_column

class MembershipModel(BaseModel):
    """Links User to Group when a User is a member of a Group.
    Allows maintaining historical records of membership."""

    __tablename__ = "memberships"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True, default=None)
    group_id: Mapped[str] = mapped_column(ForeignKey("groups.id"), index=True, default=None)

    startdate: Mapped[datetime.datetime] = mapped_column(
        nullable=True,
        default=None,
        comment="First date of membership"
    )
    enddate: Mapped[datetime.datetime] = mapped_column(
        nullable=True,
        default=None,
        comment="Last date of membership"
    )
    valid: Mapped[bool] = mapped_column(
        default=True,
        comment="If the membership is still active"
    )

    user = relationship("UserModel", back_populates="memberships", foreign_keys=[user_id])
    group = relationship("GroupModel", back_populates="memberships")

    roles = relationship("RoleModel", viewonly=True, uselist=True, primaryjoin="(MembershipModel.group_id)==foreign(RoleModel.group_id)")
