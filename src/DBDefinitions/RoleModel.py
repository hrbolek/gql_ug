import uuid
import datetime
import sqlalchemy
from typing import Optional
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

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True, nullable=True, default=None)
    group_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("groups.id"), index=True, nullable=True, default=None)
    roletype_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("roletypes.id"), index=True, nullable=True, default=None)

    deputy: Mapped[bool] = mapped_column(comment="if this role is deputy role", nullable=True, default=None)
    startdate: Mapped = mapped_column(DateTime, comment="When the role begins", nullable=True, default=None)
    enddate: Mapped = mapped_column(DateTime, comment="When the role ends", nullable=True, default=None)

    __table_args__ = (
        sqlalchemy.Index("ix_roles_group_roletype", "group_id", "roletype_id"),
        sqlalchemy.Index("ix_roles_user_group", "user_id", "group_id"),
        # volitelně:
        # Index("ix_roles_roletype_group", "roletype_id", "group_id"),
        # Index("ix_roles_group_start_end", "group_id", "startdate", "enddate"),
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
        now = sqlalchemy.func.now()
        return sqlalchemy.and_(
            sqlalchemy.or_(cls.startdate <= now, cls.startdate.is_(None)),  # Valid if startdate is in the past or missing
            sqlalchemy.or_(cls.enddate >= now, cls.enddate.is_(None))       # Valid if enddate is in the future or missing
        )
    
    roletype: Mapped[Optional["RoleTypeModel"]] = relationship("RoleTypeModel", viewonly=True, lazy="joined", default=None)
    # roletype = relationship("RoleTypeModel", viewonly=True, lazy="joined", default=None)

    # user = relationship(
    #     "UserModel", 
    #     foreign_keys=[user_id], 
    #     viewonly=True
    # )

    user: Mapped[Optional["UserModel"]] = relationship(
        "UserModel", 
        foreign_keys=[user_id], 
        viewonly=True,
        lazy="joined", default=None
    )

    # group = relationship(
    #     "GroupModel", 
    #     viewonly=True
    # )

    group: Mapped[Optional["GroupModel"]] = relationship(
        "GroupModel", 
        foreign_keys=[group_id], 
        viewonly=True,
        lazy="joined", default=None
    )

    memberships = relationship(
        "MembershipModel", 
        viewonly=True, 
        uselist=True, 
        primaryjoin="foreign(MembershipModel.group_id)==(RoleModel.group_id)"
    )

