from app.db.models import Repayment, LoanRequest, User
from app.db.database import SessionLocal
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import uuid

class RepaymentService:
    @staticmethod
    def repay_loan(user_phone: str, loan_id: str, amount: float):
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.phone == user_phone).first()
            if not user:
                return {"error": "User not found"}
            loan = db.query(LoanRequest).filter(LoanRequest.id == loan_id).first()
            if not loan:
                return {"error": "Loan not found"}
            if loan.user_id != user.id:
                return {"error": "User is not the borrower"}
            repayment = Repayment(loan_id=loan.id, amount=amount, date=datetime.utcnow())
            db.add(repayment)
            db.commit()
            db.refresh(repayment)
            return {"message": "Repayment submitted", "repayment_id": str(repayment.id)}
        except IntegrityError:
            db.rollback()
            return {"error": "Could not submit repayment"}
        finally:
            db.close()

    @staticmethod
    def get_repayments(loan_id: str):
        db = SessionLocal()
        repayments = db.query(Repayment).filter(Repayment.loan_id == loan_id).order_by(Repayment.date.desc()).all()
        db.close()
        return [{
            "id": str(r.id),
            "amount": r.amount,
            "date": r.date.isoformat()
        } for r in repayments]