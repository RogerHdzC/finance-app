from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

from app.models.user import User
from app.models.account import Account
from app.models.category import Category
from app.models.transaction import Transaction

