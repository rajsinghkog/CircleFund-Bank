from app.db.models import Deposit, User, Group, Membership, ExpectedDeposit
from datetime import datetime, timedelta
from app.db.database import SessionLocal
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import uuid

class DepositService:
    @staticmethod
    def _get_next_deposit_date(last_date: datetime, cycle: str) -> datetime:
        if cycle == 'daily':
            return last_date + timedelta(days=1)
        elif cycle == 'weekly':
            return last_date + timedelta(weeks=1)
        elif cycle == 'monthly':
            # Add approximately one month (30 days)
            return last_date + timedelta(days=30)
        return last_date + timedelta(days=1)  # default to daily

    @classmethod
    def _create_expected_deposits(cls, db, user_id: str, group_id: str, group_cycle: str, amount: float, membership_date: datetime):
        # Get the last expected deposit date for this user and group
        last_expected = db.query(ExpectedDeposit).filter(
            ExpectedDeposit.user_id == user_id,
            ExpectedDeposit.group_id == group_id
        ).order_by(ExpectedDeposit.expected_date.desc()).first()

        start_date = membership_date if not last_expected else last_expected.expected_date
        end_date = datetime.utcnow() + timedelta(days=30)  # Plan for next 30 days
        
        current_date = cls._get_next_deposit_date(start_date, group_cycle)
        
        while current_date <= end_date:
            expected = ExpectedDeposit(
                user_id=user_id,
                group_id=group_id,
                expected_date=current_date,
                amount=amount,
                status='pending'
            )
            db.add(expected)
            current_date = cls._get_next_deposit_date(current_date, group_cycle)
        
        db.commit()

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
                
            membership = db.query(Membership).filter(
                Membership.user_id == user.id, 
                Membership.group_id == group.id
            ).first()
            
            if not membership:
                return {"error": "User is not a member of the group"}

            # Create the deposit
            deposit = Deposit(
                user_id=user.id, 
                group_id=group.id, 
                amount=amount, 
                date=datetime.utcnow()
            )
            db.add(deposit)
            db.flush()  # Get the deposit ID

            # Find and update the expected deposit
            expected_deposit = db.query(ExpectedDeposit).filter(
                ExpectedDeposit.user_id == user.id,
                ExpectedDeposit.group_id == group.id,
                ExpectedDeposit.status == 'pending',
                ExpectedDeposit.expected_date <= datetime.utcnow()
            ).order_by(ExpectedDeposit.expected_date).first()

            if expected_deposit:
                expected_deposit.status = 'completed'
                expected_deposit.deposit_id = deposit.id
            
            # Create future expected deposits if needed
            DepositService._create_expected_deposits(
                db, 
                str(user.id), 
                str(group.id), 
                group.cycle, 
                group.contribution_amount,
                membership.joined_at
            )
            
            db.commit()
            db.refresh(deposit)
            
            return {
                "message": "Deposit submitted", 
                "deposit_id": str(deposit.id),
                "expected_deposit_fulfilled": expected_deposit is not None
            }
            
        except IntegrityError as e:
            db.rollback()
            return {"error": f"Could not submit deposit: {str(e)}"}
        finally:
            db.close()

    @staticmethod
    def get_pending_deposits(user_phone: str, group_id: str = None):
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.phone == user_phone).first()
            if not user:
                return {"error": "User not found"}
                
            query = db.query(
                ExpectedDeposit,
                Group.name.label('group_name'),
                Group.cycle.label('group_cycle')
            ).join(
                Group, Group.id == ExpectedDeposit.group_id
            ).filter(
                ExpectedDeposit.user_id == user.id,
                ExpectedDeposit.status == 'pending',
                ExpectedDeposit.expected_date <= datetime.utcnow()
            )
            
            if group_id:
                query = query.filter(ExpectedDeposit.group_id == group_id)
                
            pending = query.order_by(ExpectedDeposit.expected_date).all()
            
            return [{
                "id": str(ed.ExpectedDeposit.id),
                "group_id": str(ed.ExpectedDeposit.group_id),
                "group_name": ed.group_name,
                "expected_date": ed.ExpectedDeposit.expected_date.isoformat(),
                "amount": ed.ExpectedDeposit.amount,
                "cycle": ed.group_cycle,
                "status": ed.ExpectedDeposit.status,
                "is_overdue": ed.ExpectedDeposit.expected_date < datetime.utcnow()
            } for ed in pending]
            
        except Exception as e:
            return {"error": f"Error fetching pending deposits: {str(e)}"}
        finally:
            db.close()

    @staticmethod
    def get_deposit_history(user_phone: str, group_id: str = None):
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.phone == user_phone).first()
            if not user:
                return {"error": "User not found"}
                
            query = db.query(Deposit).filter(Deposit.user_id == user.id)
            
            if group_id:
                query = query.filter(Deposit.group_id == group_id)
                
            deposits = query.order_by(Deposit.date.desc()).all()
            
            return [{
                "id": str(d.id),
                "group_id": str(d.group_id),
                "amount": d.amount,
                "date": d.date.isoformat(),
                "status": "completed"
            } for d in deposits]
            
        except Exception as e:
            return {"error": f"Error fetching deposit history: {str(e)}"}
        finally:
            db.close()

    @staticmethod
    def get_total_and_available_balance(user_phone: str):
        db = SessionLocal()
        user = db.query(User).filter(User.phone == user_phone).first()
        if not user:
            db.close()
            return {"error": "User not found"}
        # Total deposits
        total_deposits = db.query(Deposit).filter(Deposit.user_id == user.id).with_entities(db.func.sum(Deposit.amount)).scalar() or 0.0
        # Total loans taken (approved only)
        from app.db.models import LoanRequest, Repayment
        total_loans = db.query(LoanRequest).filter(LoanRequest.user_id == user.id, LoanRequest.status == "approved").with_entities(db.func.sum(LoanRequest.amount)).scalar() or 0.0
        # Total repayments made by user (for their loans)
        user_loans = db.query(LoanRequest).filter(LoanRequest.user_id == user.id, LoanRequest.status == "approved").all()
        loan_ids = [loan.id for loan in user_loans]
        total_repaid = 0.0
        if loan_ids:
            total_repaid = db.query(Repayment).filter(Repayment.loan_id.in_(loan_ids)).with_entities(db.func.sum(Repayment.amount)).scalar() or 0.0
        # Outstanding loans = total_loans - total_repaid
        outstanding_loans = total_loans - total_repaid
        # Total balance = deposits - (loans - repayments)
        total_balance = total_deposits - outstanding_loans
        # Available balance = total_balance (could add more rules if needed)
        available_balance = total_balance
        db.close()
        return {
            "total_balance": total_balance,
            "available_balance": available_balance,
            "outstanding_loans": outstanding_loans
        }

    @staticmethod
    def get_account_statement(user_phone: str):
        db = SessionLocal()
        user = db.query(User).filter(User.phone == user_phone).first()
        if not user:
            db.close()
            return {"error": "User not found"}
        # Deposits
        deposits = db.query(Deposit).filter(Deposit.user_id == user.id).all()
        deposit_entries = [{
            "type": "deposit",
            "amount": d.amount,
            "group_id": str(d.group_id),
            "date": d.date.isoformat()
        } for d in deposits]
        # Loans
        from app.db.models import LoanRequest, Repayment
        loans = db.query(LoanRequest).filter(LoanRequest.user_id == user.id).all()
        loan_entries = [{
            "type": "loan",
            "amount": l.amount,
            "group_id": str(l.group_id),
            "status": l.status,
            "date": l.created_at.isoformat()
        } for l in loans]
        # Repayments (for user's loans)
        loan_ids = [l.id for l in loans]
        repayments = []
        if loan_ids:
            repayments = db.query(Repayment).filter(Repayment.loan_id.in_(loan_ids)).all()
        repayment_entries = [{
            "type": "repayment",
            "amount": r.amount,
            "loan_id": str(r.loan_id),
            "date": r.date.isoformat()
        } for r in repayments]
        # Combine and sort by date
        statement = deposit_entries + loan_entries + repayment_entries
        statement.sort(key=lambda x: x["date"], reverse=True)
        db.close()
        return statement