from __future__ import annotations
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.exceptions.user import UserNotFoundError
from app.models.user import User
from typing import List, Tuple

class UserService:

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
        total_pages = (total + limit - 1) // limit if limit > 0 else 0
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
        user = db.get(User, user_id)
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
        user = db.get(User, user_id)
        if not user:
            raise UserNotFoundError()
        db.delete(user)
        db.commit()