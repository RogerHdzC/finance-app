# tests/services/test_user_service.py
import pytest
from uuid import UUID
from app.services.user import UserService
from app.schemas.user import UserCreate
from app.exceptions.user import UsernameAlreadyExistsError, EmailAlreadyExistsError, UserNotFoundError
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

def test_create_user_duplicate_email(db_session):
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
        username="jadoe",
        email="john@doe.com",
        password="password123",
    )
    UserService.create_user(db=db_session, data=data1)
    with pytest.raises(EmailAlreadyExistsError):
        UserService.create_user(db=db_session, data=data2)

def test_get_user_by_id_not_found(db_session):
    non_existent_id = UUID("00000000-0000-0000-0000-000000000001")
    with pytest.raises(UserNotFoundError):
        UserService.get_user_by_id(db=db_session, user_id=non_existent_id)
        
def test_get_users_pagination(db_session):
    for i in range(10):
        UserService.create_user(db=db_session, data=UserCreate(
            name=f"User {i}",
            lastname=f"Lastname {i}",
            username=f"user{i}",
            email=f"user{i}@example.com",
            password="password123",
        ))
    users,_,_ = UserService.get_users(db=db_session, offset=0, limit=5)
    assert len(users) == 5
    users,_,_ = UserService.get_users(db=db_session, offset=5, limit=5)
    assert len(users) == 5
    users,_,_ = UserService.get_users(db=db_session, offset=0, limit=15)
    assert len(users) == 10
    
def test_delete_user(db_session):    
    user = UserService.create_user(db=db_session, data=UserCreate(
        name="ToDelete",
        lastname="User",
        username="todelete",
        email="todelete@example.com",
        password="password123",
    ))
    UserService.delete_user(db=db_session, user_id=user.id)
    with pytest.raises(UserNotFoundError):
        UserService.get_user_by_id(db=db_session, user_id=user.id)

def test_delete_user_not_found(db_session):
    non_existent_id = UUID("00000000-0000-0000-0000-000000000001")
    with pytest.raises(UserNotFoundError):
        UserService.delete_user(db=db_session, user_id=non_existent_id)
        
def test_get_user_by_id_success(db_session):
    user = UserService.create_user(db=db_session, data=UserCreate(
        name="FindMe",
        lastname="User",
        username="findme",
        email="findme@example.com",
        password="password123",
    ))
    fetched_user = UserService.get_user_by_id(db=db_session, user_id=user.id)
    assert fetched_user.id == user.id
    assert fetched_user.username == "findme"

def test_get_users_empty(db_session):
    users,_,_ = UserService.get_users(db=db_session, offset=0, limit=10)
    assert len(users) == 0
    