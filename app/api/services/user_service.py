from app.db.models import User
from app.db.database import SessionLocal
from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext

class UserService:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @staticmethod
    def signup(name: str, phone: str, password: str):
        db = SessionLocal()
        try:
            existing = db.query(User).filter(User.phone == phone).first()
            if existing:
                return {"error": "User already exists"}
            password_hash = UserService.pwd_context.hash(password)
            user = User(name=name, phone=phone, password_hash=password_hash)
            db.add(user)
            db.commit()
            db.refresh(user)
            return {"message": "Signup successful", "user": {"id": str(user.id), "name": user.name, "phone": user.phone}}
        except IntegrityError:
            db.rollback()
            return {"error": "User already exists"}
        finally:
            db.close()

    @staticmethod
    def get_user_by_phone(phone: str):
        db = SessionLocal()
        user = db.query(User).filter(User.phone == phone).first()
        db.close()
        if not user:
            return {"error": "User not found"}
        return {"user": {"id": str(user.id), "name": user.name, "phone": user.phone}}

    @staticmethod
    def signin(phone: str, password: str):
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.phone == phone).first()
            if not user:
                return {"error": "User not found"}
            if not UserService.pwd_context.verify(password, user.password_hash):
                return {"error": "Incorrect password"}
            return {"message": "Signin successful", "user": {"id": str(user.id), "name": user.name, "phone": user.phone}}
        finally:
            db.close()
