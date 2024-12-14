import datetime
import sqlalchemy
from sqlalchemy import (
    Column,
    String,
    ForeignKey,
    DateTime,
    Boolean,
)
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.ext.hybrid import hybrid_property

from .BaseModel import BaseModel

# from .utils import createTypeAndCategory
# RoleTypeModel, RoleCategoryModel = createTypeAndCategory(tableNamePrefix="role")

class RoleModel(BaseModel):
    """Links a user to a group where the user 'plays' a specific role."""

    __tablename__ = "roles"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=True, default=None)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), index=True, nullable=True, default=None)
    roletype_id: Mapped[int] = mapped_column(ForeignKey("roletypes.id"), index=True, nullable=True, default=None)

    startdate: Mapped = mapped_column(DateTime, comment="When the role begins", nullable=True, default=None)
    enddate: Mapped = mapped_column(DateTime, comment="When the role ends", nullable=True, default=None)

    @hybrid_property
    def valid(self):
        """Evaluates if the entity is valid based on the current datetime."""
        now = datetime.datetime.utcnow()
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
        now = datetime.datetime.utcnow()
        return sqlalchemy.and_(
            sqlalchemy.or_(cls.startdate <= now, cls.startdate.is_(None)),  # Valid if startdate is in the past or missing
            sqlalchemy.or_(cls.enddate >= now, cls.enddate.is_(None))       # Valid if enddate is in the future or missing
        )
    
    roletype = relationship("RoleTypeModel", viewonly=True, lazy="joined")
    user = relationship("UserModel", foreign_keys=[user_id], viewonly=True)
    group = relationship("GroupModel", viewonly=True)
    memberships = relationship("MembershipModel", viewonly=True, uselist=True, primaryjoin="foreign(MembershipModel.group_id)==(RoleModel.group_id)")

