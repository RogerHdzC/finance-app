from uuid import UUID, uuid4
from app.core.security import pwd_context
from sqlalchemy.orm import Session
from app.exceptions.user import UsernameAlreadyExistsError, EmailAlreadyExistsError, UserNotFoundError
from app.models.user import User
from app.schemas.user import UserCreate

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
        db: Session
    ) -> list:
        """
        Retrieve all users from the database.
        """
        return db.query(User).all()