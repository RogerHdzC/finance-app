# tests/domain/test_user_errors.py
from app.exceptions.user import (
    UsernameAlreadyExistsError,
    EmailAlreadyExistsError,
    UserNotFoundError,
)

def test_username_already_exists_error():
    err = UsernameAlreadyExistsError()

    assert err.code == "user.username_already_exists"
    assert err.detail == "The username is already taken."


def test_email_already_exists_error():
    err = EmailAlreadyExistsError()

    assert err.code == "user.email_already_exists"
    assert err.detail == "The email is already registered."


def test_user_not_found_error():
    err = UserNotFoundError()

    assert err.code == "user.not_found"
    assert err.detail == "The requested user does not exist."
