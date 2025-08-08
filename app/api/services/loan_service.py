from app.db.models import LoanRequest, User, Group, Membership, Transaction
from app.models.schemas import TransactionType
from app.db.database import SessionLocal
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
import uuid
from sqlalchemy.orm import joinedload

class LoanService:
    @staticmethod
    def request_loan(user_phone: str, group_id: str, amount: float, due_days: int = 30):
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.phone == user_phone).first()
            if not user:
                return {"error": "User not found"}
            try:
                group_uuid = uuid.UUID(str(group_id))
            except Exception:
                return {"error": "Invalid group_id"}
            group = db.query(Group).filter(Group.id == group_uuid).first()
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
        try:
            loan_uuid = uuid.UUID(str(loan_id))
        except Exception:
            return {"error": "Invalid loan_id"}
        loan = db.query(LoanRequest).options(
            joinedload(LoanRequest.group)
        ).filter(LoanRequest.id == loan_uuid).first()
        db.close()
        
        if not loan:
            return {"error": "Loan not found"}
            
        return {
            "id": str(loan.id),
            "user_id": str(loan.user_id),
            "group_id": str(loan.group_id),
            "group_name": loan.group.name if loan.group else None,
            "amount": float(loan.amount),
            "status": loan.status,
            "created_at": loan.created_at.isoformat(),
            "due_date": loan.due_date.isoformat() if loan.due_date else None,
            "withdrawn_at": loan.withdrawn_at.isoformat() if loan.withdrawn_at else None
        }
        
    @staticmethod
    def get_loans_by_user(user_id: str, status: str = None):
        db = SessionLocal()
        try:
            user_uuid = uuid.UUID(str(user_id))
        except Exception:
            return []
        query = db.query(LoanRequest).options(
            joinedload(LoanRequest.group)
        ).filter(LoanRequest.user_id == user_uuid)
        
        if status:
            query = query.filter(LoanRequest.status == status)
            
        loans = query.order_by(LoanRequest.created_at.desc()).all()
        db.close()
        
        return [{
            "id": str(loan.id),
            "user_id": str(loan.user_id),
            "group_id": str(loan.group_id),
            "group_name": loan.group.name if loan.group else None,
            "amount": float(loan.amount),
            "status": loan.status,
            "created_at": loan.created_at.isoformat(),
            "due_date": loan.due_date.isoformat() if loan.due_date else None,
            "withdrawn_at": loan.withdrawn_at.isoformat() if loan.withdrawn_at else None
        } for loan in loans]

    @staticmethod
    def get_loans_for_user_with_votes(user_id: str, status: str | None = None):
        db = SessionLocal()
        try:
            # Cast to UUID
            try:
                user_uuid = uuid.UUID(str(user_id))
            except Exception:
                return []

            query = db.query(LoanRequest).options(joinedload(LoanRequest.group)).filter(LoanRequest.user_id == user_uuid)
            if status:
                query = query.filter(LoanRequest.status == status)
            loans = query.order_by(LoanRequest.created_at.desc()).all()

            from app.db.models import Vote, Membership

            results = []
            for loan in loans:
                # Count group members
                total_members = db.query(Membership).filter(Membership.group_id == loan.group_id).count()
                # Count yes votes
                yes_votes = db.query(Vote).filter(Vote.loan_id == loan.id, Vote.vote == 'yes').count()
                results.append({
                    'id': str(loan.id),
                    'user_id': str(loan.user_id),
                    'group_id': str(loan.group_id),
                    'group_name': loan.group.name if loan.group else None,
                    'amount': float(loan.amount),
                    'status': loan.status,
                    'created_at': loan.created_at.isoformat(),
                    'due_date': loan.due_date.isoformat() if loan.due_date else None,
                    'withdrawn_at': loan.withdrawn_at.isoformat() if loan.withdrawn_at else None,
                    'yes_votes': int(yes_votes),
                    'total_members': int(total_members)
                })
            return results
        finally:
            db.close()
        
    @staticmethod
    def withdraw_loan(loan_id: str, user_id: str):
        db = SessionLocal()
        try:
            # Start a transaction
            db.begin()
            
            # Get the loan with a row lock to prevent concurrent updates
            # Cast to UUIDs for safety
            loan_uuid = uuid.UUID(str(loan_id)) if not isinstance(loan_id, uuid.UUID) else loan_id
            user_uuid = uuid.UUID(str(user_id)) if not isinstance(user_id, uuid.UUID) else user_id
            loan = db.query(LoanRequest).filter(
                LoanRequest.id == loan_uuid,
                LoanRequest.user_id == user_uuid,
                LoanRequest.status == 'approved'
            ).with_for_update().first()
            
            if not loan:
                db.rollback()
                return {"error": "Loan not found, already withdrawn, or not approved"}
                
            # Update loan status
            loan.status = 'withdrawn'
            loan.withdrawn_at = datetime.utcnow()
            
            # Create a transaction record
            transaction = Transaction(
                id=uuid.uuid4(),
                user_id=user_uuid,
                group_id=loan.group_id,
                amount=loan.amount,
                type=TransactionType.LOAN_WITHDRAWAL,
                reference_id=loan.id,
                status='completed',
                created_at=datetime.utcnow()
            )
            db.add(transaction)
            
            # Commit the transaction
            db.commit()
            
            return {"message": "Loan amount withdrawn successfully"}
            
        except Exception as e:
            db.rollback()
            return {"error": f"Failed to withdraw loan: {str(e)}"}
            
        finally:
            db.close()

    @staticmethod
    def get_pending_loans_for_user(user_id: str):
        db = SessionLocal()
        try:
            # Cast to UUID
            try:
                user_uuid = uuid.UUID(str(user_id))
            except Exception:
                return []

            # Get group_ids where user is a member
            from app.db.models import Membership, User
            memberships = db.query(Membership).filter(Membership.user_id == user_uuid).all()
            group_ids = [m.group_id for m in memberships]
            if not group_ids:
                return []

            # Query pending loans in those groups, exclude user's own loans
            loans = db.query(LoanRequest).options(
                joinedload(LoanRequest.group)
            ).filter(
                LoanRequest.group_id.in_(group_ids),
                LoanRequest.status == 'pending'
            ).order_by(LoanRequest.created_at.desc()).all()

            # Map user names
            user_ids = list({l.user_id for l in loans})
            users_by_id = {}
            if user_ids:
                users = db.query(User).filter(User.id.in_(user_ids)).all()
                users_by_id = {u.id: u for u in users}

            return [{
                "id": str(l.id),
                "user_id": str(l.user_id),
                "user_name": users_by_id.get(l.user_id).name if users_by_id.get(l.user_id) else None,
                "group_id": str(l.group_id),
                "group_name": l.group.name if l.group else None,
                "amount": float(l.amount),
                "status": l.status,
                "created_at": l.created_at.isoformat(),
                "due_date": l.due_date.isoformat() if l.due_date else None
            } for l in loans]
        finally:
            db.close()

    @staticmethod
    def get_all_loans(status: str | None = None, group_id: str | None = None):
        db = SessionLocal()
        try:
            from app.db.models import Vote
            query = db.query(LoanRequest).options(joinedload(LoanRequest.group))
            if status:
                query = query.filter(LoanRequest.status == status)
            if group_id:
                try:
                    group_uuid = uuid.UUID(str(group_id))
                    query = query.filter(LoanRequest.group_id == group_uuid)
                except Exception:
                    return []
            loans = query.order_by(LoanRequest.created_at.desc()).all()

            # Prefetch vote counts per loan
            loan_ids = [l.id for l in loans]
            yes_counts = {}
            if loan_ids:
                for loan in loans:
                    yes_counts[loan.id] = db.query(Vote).filter(Vote.loan_id == loan.id, Vote.vote == 'yes').count()

            # Prefetch total members per group
            group_ids = list({l.group_id for l in loans})
            members_per_group = {}
            if group_ids:
                for gid in group_ids:
                    members_per_group[gid] = db.query(Membership).filter(Membership.group_id == gid).count()

            return [{
                'id': str(l.id),
                'user_id': str(l.user_id),
                'group_id': str(l.group_id),
                'group_name': l.group.name if l.group else None,
                'amount': float(l.amount),
                'status': l.status,
                'created_at': l.created_at.isoformat(),
                'due_date': l.due_date.isoformat() if l.due_date else None,
                'withdrawn_at': l.withdrawn_at.isoformat() if l.withdrawn_at else None,
                'yes_votes': int(yes_counts.get(l.id, 0)),
                'total_members': int(members_per_group.get(l.group_id, 0)),
            } for l in loans]
        finally:
            db.close()