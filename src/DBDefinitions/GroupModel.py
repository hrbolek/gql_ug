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

    path_attribute_name = "path"
    parent_attribute_name = "mastergroup"
    parent_id_attribute_name = "mastergroup_id"
    children_attribute_name = "subgroups"

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

    mastergroup = relationship(
        "GroupModel",
        viewonly=True, 
        remote_side="GroupModel.id",
        uselist=False,
        back_populates="subgroups",
    ) # https://docs.sqlalchemy.org/en/20/orm/self_referential.html

    subgroups = relationship(
        "GroupModel", 
        back_populates="mastergroup",
        uselist=True,
        init=True,
        cascade="save-update"
    ) # https://docs.sqlalchemy.org/en/20/orm/self_referential.html
    # https://docs.sqlalchemy.org/en/20/_modules/examples/materialized_paths/materialized_paths.html


    grouptype = relationship(
        "GroupTypeModel", 
        viewonly=True,
    )

    # grouptype: Mapped[typing.Optional["GroupTypeModel"]] = relationship(
    #     "GroupTypeModel", 
    #     viewonly=True,
    #     lazy="joined", default=None
    # )

    memberships = relationship(
        "MembershipModel", 
        foreign_keys="MembershipModel.group_id",
        back_populates="group", 
        uselist=True,
        init=True,
        cascade="save-update"
    )
    roles = relationship(
        "RoleModel", 
        foreign_keys="RoleModel.group_id",
        back_populates="group", 
        uselist=True,
        init=True,
        cascade="save-update"
    )

    # def buildTreeStructure(self, current_path=None, _visited=None):
    #     DBModel = type(self)
    #     if _visited is None:
    #         _visited = set()
    #     if self.id in _visited:
    #         return  # ochrana proti cyklení
    #     _visited.add(self.id)
    #     # Pokud je current_path None, nastav na path rodiče nebo na None (pokud není rodič)
    #     if current_path is None:
    #         session = Session.object_session(self)
    #         # Získej path nadřazené skupiny (nebo None, pokud žádná není)
    #         parent = getattr(self, DBModel.parent_attribute_name, None)
    #         parent_id = getattr(self, DBModel.parent_id_attribute_name, None)
    #         if parent:
    #             current_path = getattr(parent, DBModel.path_attribute_name, None)
    #         elif parent_id:
    #             parent = session.get(DBModel, parent_id)
    #             current_path = getattr(parent, DBModel.path_attribute_name, None) if parent else None
    #         else:
    #             current_path = None
    #     # Nastav path pro aktuální instanci
    #     self.path = f"{current_path}/{self.id}" if current_path else str(self.id)
    #     # Rekurzivně nastav path potomkům
    #     children = getattr(self, DBModel.children_attribute_name, None)
    #     assert children is not None, "Children should not be None here, probably this method is used in operation other than insert."
    #     for child in children:
    #         if child is None:
    #             continue
    #         if not isinstance(child, DBModel):
    #             raise TypeError(f"Expected child of type {DBModel.__name__}, got {type(child).__name__}")
    #         child.buildTreeStructure(self.path, _visited=_visited)
    #     return self

# class TreeModelMixin:
#     path_attribute_name = "path"
#     parent_attribute_name = "mastergroup"
#     parent_id_attribute_name = "mastergroup_id"
#     children_attribute_name = "subgroups"

#     def updateTreeStructure(self, current_path=None, _visited=None):
#         DBModel = type(self)
#         if _visited is None:
#             _visited = set()
#         if self.id in _visited:
#             return  # ochrana proti cyklení
#         _visited.add(self.id)
#         # Pokud je current_path None, nastav na path rodiče nebo na None (pokud není rodič)
#         if current_path is None:
#             session = Session.object_session(self)
#             # Získej path nadřazené skupiny (nebo None, pokud žádná není)
#             parent = getattr(self, DBModel.parent_attribute_name, None)
#             parent_id = getattr(self, DBModel.parent_id_attribute_name, None)
#             if parent:
#                 current_path = getattr(parent, DBModel.path_attribute_name, None)
#             elif parent_id:
#                 parent = session.get(DBModel, parent_id)
#                 current_path = getattr(parent, DBModel.path_attribute_name, None) if parent else None
#             else:
#                 current_path = None
#         # Nastav path pro aktuální instanci
#         self.path = f"{current_path}/{self.id}" if current_path else str(self.id)
#         # Rekurzivně nastav path potomkům
#         children = getattr(self, DBModel.children_attribute_name, None)
#         assert children is not None, "Children should not be None here, probably this method is used in operation other than insert."
#         for child in children:
#             child.updateTreeStructure(self.path, _visited=_visited)

#     async def updateTreeStructureAsync(self, session, current_path=None, _visited=None):
#         """
#         Asynchronně rekurzivně aktualizuje materialized path této instance a všech potomků.
#         """
#         DBModel = type(self)
#         if _visited is None:
#             _visited = set()
#         if self.id in _visited:
#             return  # ochrana proti cyklení
#         _visited.add(self.id)

#         # Nastav správnou cestu podle rodiče
#         parent = getattr(self, DBModel.parent_attribute_name, None)
#         parent_id = getattr(self, DBModel.parent_id_attribute_name, None)
#         if current_path is None:
#             if parent:
#                 current_path = getattr(parent, DBModel.path_attribute_name, None)
#             elif parent_id:
#                 parent_obj = await session.get(DBModel, parent_id)
#                 current_path = getattr(parent_obj, DBModel.path_attribute_name, None) if parent_obj else None
#             else:
#                 current_path = None

#         setattr(
#             self,
#             DBModel.path_attribute_name,
#             f"{current_path}/{self.id}" if current_path else str(self.id)
#         )

#         # Pokus se načíst děti z relace, jinak fallback na DB
#         children = getattr(self, DBModel.children_attribute_name, None)
#         if not children:
#             result = await session.execute(
#                 select(DBModel).filter(
#                     getattr(DBModel, DBModel.parent_id_attribute_name) == self.id
#                 )
#             )
#             children = result.scalars().all()
#         for child in children:
#             await child.updateTreeStructureAsync(session, getattr(self, DBModel.path_attribute_name), _visited=_visited)            

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

from sqlalchemy.orm import Session
from sqlalchemy import event

def create_path_updater(
    parent_id_attribute_name="mastergroup_id",
    parent_attribute_name="mastergroup",
    path_attribute_name="path",
    children_attribute_name="subgroups",
    ):
    
    async def update_tree_path(mapper, connection, target, current_path=None, _visited=None):
        if _visited is None:
            _visited = set()
        if target.id in _visited:
            return  # ochrana proti cyklení
        _visited.add(target.id)
        # Pokud je current_path None, nastav na path rodiče nebo na None (pokud není rodič)
        if current_path is None:
            session = Session.object_session(target)
            # Získej path nadřazené skupiny (nebo None, pokud žádná není)
            parent = getattr(target, parent_attribute_name, None)
            parent_id = getattr(target, parent_id_attribute_name, None)
            if parent:
                current_path = getattr(parent, path_attribute_name, None)
            elif parent_id:
                parent = await session.get(type(target), parent_id)
                current_path = getattr(parent, path_attribute_name, None) if parent else None
            else:
                current_path = None
        # Nastav path pro aktuální instanci
        target.path = f"{current_path}/{target.id}" if current_path else str(target.id)
        # Rekurzivně nastav path potomkům
        children = getattr(target, children_attribute_name, None)
        if children is None:
            # Fallback: načti děti z DB
            session = Session.object_session(target)
            DBModel = type(target)
            children = await session.execute(
                select(DBModel).filter(getattr(DBModel, parent_id_attribute_name)==target.id)
            )
            children = children.scalars().all()
        for child in children:
            await update_tree_path(mapper, connection, child, target.path, _visited=_visited)
    return update_tree_path

update_group_path = create_path_updater()
# event.listen(GroupModel, "before_insert", update_group_path)