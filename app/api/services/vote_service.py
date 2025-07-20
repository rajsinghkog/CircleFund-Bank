from app.db.models import Vote, LoanRequest, User, Group, Membership
from app.db.database import SessionLocal
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
import uuid

class VoteService:
    @staticmethod
    def vote_on_loan(user_phone: str, loan_id: str, vote_value: str):
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.phone == user_phone).first()
            if not user:
                return {"error": "User not found"}
            loan = db.query(LoanRequest).filter(LoanRequest.id == loan_id).first()
            if not loan:
                return {"error": "Loan not found"}
            if loan.status != "pending":
                return {"error": f"Loan voting closed (status: {loan.status})"}
            # Check if user is a member of the group
            membership = db.query(Membership).filter(Membership.user_id == user.id, Membership.group_id == loan.group_id).first()
            if not membership:
                return {"error": "User is not a member of the group"}
            # Check if user already voted
            existing_vote = db.query(Vote).filter(Vote.loan_id == loan.id, Vote.voter_id == user.id).first()
            if existing_vote:
                return {"message": "Already voted"}
            if vote_value not in ["yes", "no"]:
                return {"error": "Vote must be 'yes' or 'no'"}
            vote = Vote(loan_id=loan.id, voter_id=user.id, vote=vote_value, timestamp=datetime.utcnow())
            db.add(vote)
            db.commit()
            # After voting, check if loan should be approved/rejected
            VoteService._update_loan_status(db, loan)
            return {"message": "Vote submitted"}
        except IntegrityError:
            db.rollback()
            return {"error": "Could not submit vote"}
        finally:
            db.close()

    @staticmethod
    def _update_loan_status(db, loan):
        # Get all group members
        total_members = db.query(Membership).filter(Membership.group_id == loan.group_id).count()
        votes = db.query(Vote).filter(Vote.loan_id == loan.id).all()
        yes_votes = sum(1 for v in votes if v.vote == "yes")
        no_votes = sum(1 for v in votes if v.vote == "no")
        # Approve if >50% yes
        if yes_votes > total_members / 2:
            loan.status = "approved"
            db.commit()
        # Reject if >50% no or voting window expired (not handled here)
        elif no_votes >= total_members / 2:
            loan.status = "rejected"
            db.commit()