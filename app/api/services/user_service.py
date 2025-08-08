from datetime import datetime
from typing import Optional
from sqlalchemy.exc import IntegrityError

from app.db.models import User, Membership
from app.db.database import SessionLocal
from app.models.user import UserCreate, UserLogin
import uuid

class UserService:
        
    @staticmethod
    def get_user_by_phone(phone: str):
        db = SessionLocal()
        try:
            return db.query(User).filter(User.phone == phone).first()
        finally:
            db.close()
            
    @staticmethod
    def get_user_by_id(user_id: str):
        db = SessionLocal()
        try:
            # Cast to UUID if provided as string
            try:
                user_uuid = uuid.UUID(str(user_id))
            except Exception:
                return None
            return db.query(User).filter(User.id == user_uuid).first()
        finally:
            db.close()

    @staticmethod
    def signup(user_data: UserCreate):
        db = SessionLocal()
        try:
            # Treat phone as username for simplified auth-less flow
            if not user_data.phone:
                return {"error": "username is required"}
            existing = db.query(User).filter(User.phone == user_data.phone).first()
            if existing:
                # Return existing user without token
                return {"message": "Signup successful", "user": {"id": str(existing.id), "name": existing.name, "phone": existing.phone}}

            # Store name and phone as the same username; empty password hash
            user = User(
                name=user_data.name or user_data.phone,
                phone=user_data.phone,
                password_hash=""
            )
            db.add(user)
            db.commit()
            db.refresh(user)

            return {"message": "Signup successful", "user": {"id": str(user.id), "name": user.name, "phone": user.phone}}
        except IntegrityError:
            db.rollback()
            return {"error": "User already exists"}
        except Exception as e:
            db.rollback()
            return {"error": str(e)}
        finally:
            db.close()

    @staticmethod
    def get_user_profile(phone: str):
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.phone == phone).first()
            if not user:
                return {"error": "User not found"}
                
            group_id = None
            membership = db.query(Membership).filter(Membership.user_id == user.id).first()
            if membership:
                group_id = str(membership.group_id)
                
            return {
                "id": str(user.id), 
                "name": user.name, 
                "phone": user.phone, 
                "group_id": group_id,
                "created_at": user.created_at.isoformat() if user.created_at else None
            }
        finally:
            db.close()

    @staticmethod
    def get_user_profile_by_id(user_id: str):
        db = SessionLocal()
        try:
            try:
                user_uuid = uuid.UUID(str(user_id))
            except Exception:
                return {"error": "Invalid user_id"}
            user = db.query(User).filter(User.id == user_uuid).first()
            if not user:
                return {"error": "User not found"}
            group_id = None
            membership = db.query(Membership).filter(Membership.user_id == user.id).first()
            if membership:
                group_id = str(membership.group_id)
            return {
                "user": {
                    "id": str(user.id),
                    "name": user.name,
                    "phone": user.phone,
                    "group_id": group_id
                }
            }
        finally:
            db.close()

    # authenticate_user removed in simplified flow

    @staticmethod
    def signin(login_data: UserLogin):
        try:
            # Simplified: locate by username (phone field). Create if not exists.
            db = SessionLocal()
            user = db.query(User).filter(User.phone == login_data.phone).first()
            if not user:
                user = User(name=login_data.phone, phone=login_data.phone, password_hash="")
                db.add(user)
                db.commit()
                db.refresh(user)
            return {"user": {"id": str(user.id), "name": user.name, "phone": user.phone}}
        except Exception as e:
            return {"error": str(e)}
