import sqlalchemy
from sqlalchemy import (
    Column,
    String,
    ForeignKey,
    DateTime,
    Boolean,
)
from sqlalchemy.orm import relationship

from .UUID import UUIDColumn, UUIDFKey
from .Base import BaseModel

from .utils import createTypeAndCategory
RoleTypeModel, RoleCategoryModel = createTypeAndCategory(tableNamePrefix="role")

class RoleModel(BaseModel):
    """Spojuje uzivatele a skupinu, ve ktere uzivatel "hraje" roli"""

    __tablename__ = "roles"

    user_id = Column(ForeignKey("users.id"), index=True)
    group_id = Column(ForeignKey("groups.id"), index=True)
    roletype_id = Column(ForeignKey("roletypes.id"), index=True)

    startdate = Column(DateTime, comment="when the role begins")
    enddate = Column(DateTime, comment="when the role ends")
    valid = Column(Boolean, default=True, comment="if the role is still active")

    roletype = relationship("RoleTypeModel", viewonly=True)
    user = relationship("UserModel", foreign_keys=[user_id], viewonly=True)
    group = relationship("GroupModel", viewonly=True)
    memberships = relationship("MembershipModel", viewonly=True, uselist=True, primaryjoin="foreign(MembershipModel.group_id)==(RoleModel.group_id)")

