from app.db.models import User
from app.db.database import SessionLocal
from sqlalchemy.exc import IntegrityError

class UserService:
    @staticmethod
    def signup(name: str, phone: str):
        db = SessionLocal()
        try:
            existing = db.query(User).filter(User.phone == phone).first()
            if existing:
                return {"error": "User already exists"}
            user = User(name=name, phone=phone)
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
