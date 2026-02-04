# tests/services/test_user_service.py
import pytest

from app.services.user import UserService
from app.schemas.user import UserCreate
from app.exceptions.user import UsernameAlreadyExistsError
from app.models.user import User


def test_create_user_success(db_session):
    data = UserCreate(
        name="John",
        lastname="Doe",
        username="jdoe",
        email="john@doe.com",
        password="password123",
    )

    user = UserService.create_user(db=db_session, data=data)

    assert user.id is not None
    assert user.username == "jdoe"

    persisted = db_session.query(User).filter_by(username="jdoe").first()
    assert persisted is not None


def test_create_user_duplicate_username(db_session):
    data1 = UserCreate(
        name="John",
        lastname="Doe",
        username="jdoe",
        email="john@doe.com",
        password="password123",
    )

    data2 = UserCreate(
        name="Jane",
        lastname="Doe",
        username="jdoe",  # same username
        email="jane@doe.com",
        password="password123",
    )

    UserService.create_user(db=db_session, data=data1)

    with pytest.raises(UsernameAlreadyExistsError):
        UserService.create_user(db=db_session, data=data2)
