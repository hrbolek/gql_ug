import sqlalchemy
from sqlalchemy import (
    Column,
    String,
    ForeignKey,
    DateTime,
    Boolean,
)
from sqlalchemy.orm import relationship, mapped_column, Mapped

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
    valid: Mapped = mapped_column(Boolean, default=True, comment="If the role is still active", nullable=False)

    roletype = relationship("RoleTypeModel", viewonly=True, lazy="joined")
    user = relationship("UserModel", foreign_keys=[user_id], viewonly=True)
    group = relationship("GroupModel", viewonly=True)
    memberships = relationship("MembershipModel", viewonly=True, uselist=True, primaryjoin="foreign(MembershipModel.group_id)==(RoleModel.group_id)")

