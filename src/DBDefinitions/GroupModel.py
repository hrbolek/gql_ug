import sqlalchemy
from sqlalchemy import (
    Uuid,
    Column,
    String,
    ForeignKey,
    DateTime,
    Boolean,
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property

from .Base import (BaseModel, uuid4)


from .utils import createTypeAndCategory
GroupTypeModel, GroupCategoryModel = createTypeAndCategory(tableNamePrefix="group")
print("GroupTypeModel", GroupTypeModel.__name__)
class GroupModel(BaseModel):
    """Spravuje data spojena se skupinou"""

    __tablename__ = "groups"
    id = Column(Uuid, primary_key=True, index=True, comment="primary key", default=uuid4)
    
    # https://stackoverflow.com/questions/59132388/postgres-materialized-path-what-are-the-benefits-of-using-ltree
    # IDA/IDB/SELF
    path = Column(String, index=True, comment="materialized path technique, not implemented") 

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
    

    mastergroup_id = Column(ForeignKey("groups.id"), index=True, comment="link to the commanding group")

    mastergroup = relationship("GroupModel", viewonly=True) # https://docs.sqlalchemy.org/en/20/orm/self_referential.html
    subgroups = relationship ("GroupModel", remote_side=[id], viewonly=True, uselist=True) # https://docs.sqlalchemy.org/en/20/orm/self_referential.html
    # https://docs.sqlalchemy.org/en/20/_modules/examples/materialized_paths/materialized_paths.html


    grouptype = relationship("GroupTypeModel", viewonly=True)
    memberships = relationship("MembershipModel", viewonly=True)
    roles = relationship("RoleModel", viewonly=True)


from sqlalchemy import select, update
async def createGroupPaths(asyncsessionmaker):
    # async with asyncsessionmaker() as session:
    #     stmt = update(GroupModel).values(path=".")
    #     await session.execute(stmt)
    #     await session.commit()

    stmt = select(GroupModel).filter_by(mastergroup_id=None)
    async with asyncsessionmaker() as session:
        rowstoupdate = await session.execute(stmt)
        groupstoupdate = [g for g in rowstoupdate.scalars()]
        for group in groupstoupdate:
            group.path = f"{group.id}"
        await session.commit()
        groupinfos = {group.id: {"id": group.id, "path": f"{group.path}"} for group in groupstoupdate}
        print(f"groupinfos: {groupinfos}", flush=True)
    
    while len(groupinfos) > 0:
        idsToQuery = [group["id"] for group in groupinfos.values()]
        # print(f"idsToQuery {idsToQuery}")
        stmt = select(GroupModel).where(GroupModel.mastergroup_id.in_(idsToQuery))
        async with asyncsessionmaker() as session:
            rowstoupdate = await session.execute(stmt)
            groupstoupdate = [g for g in rowstoupdate.scalars()]
            # print(f"groupstoupdate {groupstoupdate}")
            for group in groupstoupdate:
                # print(f"group {group}")
                masterpath = groupinfos[group.mastergroup_id]["path"]
                group.path = f"{masterpath}/{group.id}"
            await session.commit()
            groupinfos = {group.id: {"id": group.id, "path": f"{group.path}"} for group in groupstoupdate}
        print(f"groupinfos: {groupinfos}", flush=True)

    pass