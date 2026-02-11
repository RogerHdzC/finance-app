from uuid import UUID
from app.core.security import pwd_context
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.exceptions.user import UsernameAlreadyExistsError, EmailAlreadyExistsError, UserNotFoundError
from app.models.user import User
from app.schemas.user import UserCreate
from typing import List, Tuple

class UserService:
    @staticmethod
    def create_user(
        db: Session,
        data: UserCreate
    ) -> User:
        """
        Create a new user in the database.
        """
        if db.query(User).filter(User.username == data.username).first():
            raise UsernameAlreadyExistsError()
        if db.query(User).filter(User.email == data.email).first():
            raise EmailAlreadyExistsError()
        password_hash = pwd_context.hash(data.password)
        user = User(
            name=data.name,
            lastname=data.lastname,
            username=data.username,
            email=data.email,
            password_hash=password_hash
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def get_users(
        db: Session,
        limit: int,
        offset: int,
    ) -> Tuple[List[User], int, int]:
        """
        Retrieve all users from the database with a limit of 50 by default.
        """
        total = db.query(func.count(User.id)).scalar() or 0
        total_pages = (total + limit - 1) // limit
        users = (db.query(User).order_by(User.created_at.asc()).offset(offset).limit(limit).all())
        
        return users, total, total_pages
    
    @staticmethod
    def get_user_by_id(
        db: Session,
        user_id: UUID
    ) -> User:
        """
        Retrieve a user by their ID.
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise UserNotFoundError()
        return user
    
    def delete_user(
        db: Session,
        user_id: UUID
    ) -> None:
        """
        Delete a user by their ID.
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise UserNotFoundError()
        db.delete(user)
        db.commit()