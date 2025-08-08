from datetime import datetime, timedelta
import os
from typing import Optional
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError

from app.db.models import User, Membership
from app.db.database import SessionLocal
from app.models.user import UserCreate, UserLogin, Token
from app.api.auth.auth_bearer import SECRET_KEY, ALGORITHM, create_access_token

class UserService:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        return create_access_token(data, expires_delta)
        
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
            return db.query(User).filter(User.id == user_id).first()
        finally:
            db.close()

    @staticmethod
    def signup(user_data: UserCreate):
        db = SessionLocal()
        try:
            existing = db.query(User).filter(User.phone == user_data.phone).first()
            if existing:
                return {"error": "User already exists"}
                
            password_hash = UserService.pwd_context.hash(user_data.password)
            user = User(
                name=user_data.name,
                phone=user_data.phone,
                password_hash=password_hash
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            
            # Generate access token
            access_token_expires = timedelta(minutes=30)
            access_token = UserService.create_access_token(
                data={"sub": str(user.id), "phone": user.phone},
                expires_delta=access_token_expires
            )
            
            return {
                "message": "Signup successful", 
                "access_token": access_token,
                "token_type": "bearer",
                "user": {
                    "id": str(user.id), 
                    "name": user.name, 
                    "phone": user.phone
                }
            }
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
    def authenticate_user(phone: str, password: str):
        user = UserService.get_user_by_phone(phone)
        if not user:
            return None
        if not UserService.pwd_context.verify(password, user.password_hash):
            return None
        return user

    @staticmethod
    def signin(login_data: UserLogin):
        try:
            user = UserService.authenticate_user(login_data.phone, login_data.password)
            if not user:
                return {"error": "Incorrect phone or password"}
                
            # Generate access token
            access_token_expires = timedelta(minutes=30)
            access_token = UserService.create_access_token(
                data={"sub": str(user.id), "phone": user.phone},
                expires_delta=access_token_expires
            )
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user": {
                    "id": str(user.id),
                    "name": user.name,
                    "phone": user.phone
                }
            }
        except Exception as e:
            return {"error": str(e)}
