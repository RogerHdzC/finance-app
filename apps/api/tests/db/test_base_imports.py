# tests/db/test_base_imports.py
def test_db_base_imports_models():
    # Si esto falla, normalmente se rompe Alembic/autogenerate o el mapeo de modelos.
    import app.db.base as base  # noqa: F401

    # asserts mínimos pero útiles
    from app.models.user import User
    from app.models.account import Account
    from app.models.category import Category
    from app.models.transaction import Transaction
    from app.models.refresh_token import RefreshToken

    assert User.__tablename__
    assert Account.__tablename__
    assert Category.__tablename__
    assert Transaction.__tablename__
    assert RefreshToken.__tablename__
