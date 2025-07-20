from app.db.models import Deposit, User, Group, Membership
from app.db.database import SessionLocal
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import uuid

class DepositService:
    @staticmethod
    def submit_deposit(user_phone: str, group_id: str, amount: float):
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.phone == user_phone).first()
            if not user:
                return {"error": "User not found"}
            group = db.query(Group).filter(Group.id == group_id).first()
            if not group:
                return {"error": "Group not found"}
            membership = db.query(Membership).filter(Membership.user_id == user.id, Membership.group_id == group.id).first()
            if not membership:
                return {"error": "User is not a member of the group"}
            deposit = Deposit(user_id=user.id, group_id=group.id, amount=amount, date=datetime.utcnow())
            db.add(deposit)
            db.commit()
            db.refresh(deposit)
            return {"message": "Deposit submitted", "deposit_id": str(deposit.id)}
        except IntegrityError:
            db.rollback()
            return {"error": "Could not submit deposit"}
        finally:
            db.close()

    @staticmethod
    def get_deposit_history(user_phone: str, group_id: str = None):
        db = SessionLocal()
        user = db.query(User).filter(User.phone == user_phone).first()
        if not user:
            db.close()
            return {"error": "User not found"}
        query = db.query(Deposit).filter(Deposit.user_id == user.id)
        if group_id:
            query = query.filter(Deposit.group_id == group_id)
        deposits = query.order_by(Deposit.date.desc()).all()
        db.close()
        return [{
            "id": str(d.id),
            "group_id": str(d.group_id),
            "amount": d.amount,
            "date": d.date.isoformat()
        } for d in deposits]