import sqlalchemy
from sqlalchemy import (
    Column,
    String,
    ForeignKey,
    DateTime,
    Boolean,
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property

from .Base import BaseModel


from .utils import createTypeAndCategory
GroupTypeModel, GroupCategoryModel = createTypeAndCategory(tableNamePrefix="group")
print("GroupTypeModel", GroupTypeModel.__name__)
class GroupModel(BaseModel):
    """Spravuje data spojena se skupinou"""

    __tablename__ = "groups"

    name = Column(String, comment="name of the group")
    name_en = Column(String, comment="english name of the group")
    abbreviation = Column(String, comment="name abbreviation of the group")
    email = Column(String, comment="can be an email for whole group")

    startdate = Column(DateTime, comment="born date of the group")
    enddate = Column(DateTime, comment="date when group `died`")
    valid = Column(Boolean, default=True, comment="if the group still exists")

    grouptype_id = Column(ForeignKey("grouptypes.id"), index=True, comment="link to the group type (aka faculty)")

    @hybrid_property
    def type_id(self):
        return self.grouptype_id
    
    grouptype = relationship("GroupTypeModel", viewonly=True)

    mastergroup_id = Column(ForeignKey("groups.id"), index=True, comment="link to the commanding group")

    memberships = relationship("MembershipModel", viewonly=True)
    roles = relationship("RoleModel", viewonly=True)
