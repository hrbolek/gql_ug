import sqlalchemy
import typing
import uuid
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

from .BaseModel import BaseModel


# from .utils import createTypeAndCategory
# GroupTypeModel, GroupCategoryModel = createTypeAndCategory(tableNamePrefix="group")
# print("GroupTypeModel", GroupTypeModel.__name__)

import datetime
from sqlalchemy.orm import relationship, Mapped, mapped_column

class GroupModel(BaseModel):
    """Manages data associated with a group."""

    __tablename__ = "groups"

    # Materialized path technique
    path: Mapped[str] = mapped_column(
        index=True,
        nullable=True,
        default=None,
        comment="Materialized path technique, not implemented"
    )

    name: Mapped[str] = mapped_column(
        nullable=True, default=None,
        comment="Name of the group"
    )
    name_en: Mapped[str] = mapped_column(
        nullable=True, default=None,
        comment="English name of the group"
    )
    abbreviation: Mapped[str] = mapped_column(
        nullable=True, default=None,
        comment="Name abbreviation of the group"
    )
    email: Mapped[str] = mapped_column(
        nullable=True, default=None,
        comment="Email for the entire group"
    )

    startdate: Mapped[datetime.datetime] = mapped_column(
        nullable=True, default=None,
        comment="Born date of the group"
    )
    enddate: Mapped[datetime.datetime] = mapped_column(
        nullable=True, default=None,
        comment="Date when the group 'died'"
    )
    valid: Mapped[bool] = mapped_column(
        nullable=True, 
        default=True, 
        comment="If the group still exists"
    )

    grouptype_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("grouptypes.id"),
        index=True, nullable=True, default=None,
        comment="Link to the group type (aka faculty)"
    )

    mastergroup_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("groups.id"),
        index=True,
        nullable=True, default=None,
        comment="Link to the commanding group"
    )

    @hybrid_property
    def type_id(self) -> typing.Optional[uuid.UUID]:
        return self.grouptype_id

    mastergroup = relationship("GroupModel", viewonly=True) # https://docs.sqlalchemy.org/en/20/orm/self_referential.html
    subgroups = relationship ("GroupModel", remote_side="GroupModel.id", viewonly=True, uselist=True) # https://docs.sqlalchemy.org/en/20/orm/self_referential.html
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
        # print(f"groupinfos: {groupinfos}", flush=True)
    
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
        # print(f"groupinfos: {groupinfos}", flush=True)

    pass