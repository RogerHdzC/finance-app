from app.services.refresh_tokens import RefreshTokenService
from app.exceptions.base import ConflictError
import pytest


def test_issue_and_verify_refresh_token(db_session):
    from uuid import uuid4

    user_id = uuid4()
    token = RefreshTokenService.issue(db=db_session, user_id=user_id)

    row = RefreshTokenService.verify(db=db_session, refresh_token_plain=token)
    assert str(row.user_id) == str(user_id)


def test_rotate_revokes_old_token(db_session):
    from uuid import uuid4

    user_id = uuid4()
    token = RefreshTokenService.issue(db=db_session, user_id=user_id)
    row = RefreshTokenService.verify(db=db_session, refresh_token_plain=token)

    new_token = RefreshTokenService.rotate(db=db_session, row=row)

    assert new_token != token


    with pytest.raises(ConflictError):
        RefreshTokenService.verify(db=db_session, refresh_token_plain=token)
