from app.db.models import LoanRequest, User, Group, Membership
from app.db.database import SessionLocal
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
import uuid

class LoanService:
    @staticmethod
    def request_loan(user_phone: str, group_id: str, amount: float, due_days: int = 30):
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
            loan = LoanRequest(user_id=user.id, group_id=group.id, amount=amount, status="pending", created_at=datetime.utcnow(), due_date=datetime.utcnow() + timedelta(days=due_days))
            db.add(loan)
            db.commit()
            db.refresh(loan)
            return {"message": "Loan requested", "loan_id": str(loan.id)}
        except IntegrityError:
            db.rollback()
            return {"error": "Could not request loan"}
        finally:
            db.close()

    @staticmethod
    def get_loan(loan_id: str):
        db = SessionLocal()
        loan = db.query(LoanRequest).filter(LoanRequest.id == loan_id).first()
        db.close()
        if not loan:
            return {"error": "Loan not found"}
        return {
            "id": str(loan.id),
            "user_id": str(loan.user_id),
            "group_id": str(loan.group_id),
            "amount": loan.amount,
            "status": loan.status,
            "created_at": loan.created_at.isoformat(),
            "due_date": loan.due_date.isoformat() if loan.due_date else None
        }