from app.db.models import Group, Membership, User
from app.db.database import SessionLocal
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import uuid

class GroupService:
    @staticmethod
    def list_groups():
        db = SessionLocal()
        groups = db.query(Group).all()
        db.close()
        return [{
            "id": str(g.id),
            "name": g.name,
            "contribution_amount": g.contribution_amount,
            "cycle": g.cycle
        } for g in groups]

    @staticmethod
    def join_group(user_phone: str, group_id: str):
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.phone == user_phone).first()
            if not user:
                return {"error": "User not found"}
            group = db.query(Group).filter(Group.id == group_id).first()
            if not group:
                return {"error": "Group not found"}
            existing = db.query(Membership).filter(Membership.user_id == user.id, Membership.group_id == group.id).first()
            if existing:
                return {"message": "Already a member"}
            membership = Membership(user_id=user.id, group_id=group.id, joined_at=datetime.utcnow())
            db.add(membership)
            db.commit()
            return {"message": "Joined group"}
        except IntegrityError:
            db.rollback()
            return {"error": "Could not join group"}
        finally:
            db.close()

    @staticmethod
    def get_group(group_id: str):
        db = SessionLocal()
        group = db.query(Group).filter(Group.id == group_id).first()
        db.close()
        if not group:
            return {"error": "Group not found"}
        return {
            "id": str(group.id),
            "name": group.name,
            "contribution_amount": group.contribution_amount,
            "cycle": group.cycle
        }