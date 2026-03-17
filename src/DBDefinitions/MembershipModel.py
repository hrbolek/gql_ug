import uuid
import sqlalchemy
from sqlalchemy import (
    Column,
    String,
    ForeignKey,
    DateTime,
    Boolean,
)
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey, DateTime, Index, CheckConstraint, func
from .BaseModel import BaseModel
import datetime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.ext.hybrid import hybrid_property

class MembershipModel(BaseModel):
    """Links User to Group when a User is a member of a Group.
    Allows maintaining historical records of membership."""

    __tablename__ = "memberships"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True, default=None)
    group_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("groups.id"), index=True, default=None)

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
    
    __table_args__ = (
        # Klíčový index pro resolvery a join role<->membership
        Index("ix_memberships_user_group", "user_id", "group_id"),
        # Volitelné: hledání členů skupiny (admin UI apod.)
        Index("ix_memberships_group_user", "group_id", "user_id"),
        # Integrita času (nepovinné, ale velmi doporučené)
        CheckConstraint(
            "(startdate IS NULL) OR (enddate IS NULL) OR (startdate <= enddate)",
            name="ck_memberships_start_le_end",
        ),
    )


    @hybrid_property
    def valid(self):
        """Evaluates if the entity is valid based on the current datetime."""
        now = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
        if self.startdate and self.enddate:
            return self.startdate <= now <= self.enddate
        elif self.startdate:
            return self.startdate <= now
        elif self.enddate:
            return now <= self.enddate
        return False

    @valid.expression
    def valid(cls):
        """Defines the SQL expression for the 'valid' property."""
        now = func.now()
        return sqlalchemy.and_(
            sqlalchemy.or_(cls.startdate <= now, cls.startdate.is_(None)),  # Valid if startdate is in the past or missing
            sqlalchemy.or_(cls.enddate >= now, cls.enddate.is_(None))       # Valid if enddate is in the future or missing
        )

    user = relationship("UserModel", back_populates="memberships", foreign_keys=[user_id])
    group = relationship("GroupModel", back_populates="memberships")

    roles = relationship("RoleModel", viewonly=True, uselist=True, primaryjoin="(MembershipModel.group_id)==foreign(RoleModel.group_id)")
