import sqlalchemy
import asyncio
import pytest

# from ..uoishelpers.uuid import UUIDColumn

from src.DBDefinitions import BaseModel
from src.DBDefinitions import RoleTypeModel, RoleModel
from src.DBDefinitions import UserModel, GroupModel, GroupTypeModel, MembershipModel

from tests.shared import prepare_demodata, prepare_in_memory_sqllite, get_demodata


@pytest.mark.asyncio
async def test_table_users_feed():
    async_session_maker = await prepare_in_memory_sqllite()
    await prepare_demodata(async_session_maker)

    stmt = sqlalchemy.select(UserModel)
    async with async_session_maker() as session:
        response = await session.execute(stmt)
        rows = list(response.scalars())
        print(rows)

    data = get_demodata()
    data = list(data["users"])
    result = [
        {"id": u.id, "name": u.name, "surname": u.surname, "email": u.email}
        for u in rows
    ]
    for dr, rr in zip(data, result):
        assert dr == rr


from src.DBDefinitions import ComposeConnectionString


def test_connection_string():
    connectionString = ComposeConnectionString()

    assert "://" in connectionString
    #assert "@" in connectionString


from src.DBDefinitions import UUIDColumn


def test_connection_uuidcolumn():
    col = UUIDColumn()

    assert col is not None


from src.DBDefinitions import startEngine


@pytest.mark.asyncio
async def test_table_start_engine():
    connectionString = "sqlite+aiosqlite:///:memory:"
    async_session_maker = await startEngine(
        connectionString, makeDrop=True, makeUp=True
    )

    assert async_session_maker is not None
