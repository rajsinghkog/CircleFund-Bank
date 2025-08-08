from app.db.models import Group, Membership, User, ExpectedDeposit
from app.db.database import SessionLocal
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
import uuid

class GroupService:
    @staticmethod
    def create_group(name: str, contribution_amount: float, cycle: str, creator_phone: str | None = None):
        db = SessionLocal()
        try:
            # Basic validation
            if not name or not cycle:
                return {"error": "name and cycle are required"}
            try:
                amount = float(contribution_amount)
            except Exception:
                return {"error": "contribution_amount must be a number"}
            if amount <= 0:
                return {"error": "contribution_amount must be greater than 0"}
            allowed_cycles = {"daily", "weekly", "monthly"}
            if cycle not in allowed_cycles:
                return {"error": f"cycle must be one of {', '.join(sorted(allowed_cycles))}"}

            group = Group(name=name, contribution_amount=amount, cycle=cycle)
            db.add(group)
            db.commit()
            db.refresh(group)

            # creator_phone is now ignored to align with API requirements

            return {
                "message": "Group created successfully",
                "group": {
                    "id": str(group.id),
                    "name": group.name,
                    "contribution_amount": group.contribution_amount,
                    "cycle": group.cycle,
                },
            }
        except IntegrityError as e:
            db.rollback()
            print(f"Integrity error creating group: {str(e)}")
            return {"error": "Could not create group. Please try again."}
        except Exception as e:
            db.rollback()
            print(f"Unexpected error in create_group: {str(e)}")
            return {"error": "An unexpected error occurred. Please try again."}
        finally:
            db.close()
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
    def _get_next_deposit_date(start_date: datetime, cycle: str) -> datetime:
        """Calculate the next deposit date based on the cycle"""
        if cycle == 'daily':
            return start_date + timedelta(days=1)
        elif cycle == 'weekly':
            return start_date + timedelta(weeks=1)
        elif cycle == 'monthly':
            # Add approximately one month (30 days)
            return start_date + timedelta(days=30)
        return start_date + timedelta(days=1)  # default to daily

    @classmethod
    def _create_expected_deposits(cls, db, user_id, group_id, group_cycle: str, amount: float, start_date: datetime):
        """Create expected deposits for the next 30 days"""
        end_date = datetime.utcnow() + timedelta(days=30)
        current_date = start_date
        
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

    @classmethod
    def join_group(cls, user_phone: str, group_id: str):
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.phone == user_phone).first()
            if not user:
                return {"error": "User not found"}
                
            # Ensure UUID types when querying
            try:
                group_uuid = uuid.UUID(str(group_id))
            except Exception:
                return {"error": "Invalid group_id"}
            group = db.query(Group).filter(Group.id == group_uuid).first()
            if not group:
                return {"error": "Group not found"}
                
            existing = db.query(Membership).filter(
                Membership.user_id == user.id, 
                Membership.group_id == group.id
            ).first()
            
            if existing:
                return {"message": "Already a member"}
                
            # Create the membership
            joined_at = datetime.utcnow()
            membership = Membership(
                user_id=user.id, 
                group_id=group.id, 
                joined_at=joined_at
            )
            db.add(membership)
            
            # Create expected deposits
            cls._create_expected_deposits(
                db=db,
                user_id=user.id,
                group_id=group.id,
                group_cycle=group.cycle,
                amount=group.contribution_amount,
                start_date=joined_at
            )
            
            db.commit()
            return {"message": "Successfully joined group"}
            
        except IntegrityError as e:
            db.rollback()
            print(f"Error joining group: {str(e)}")
            return {"error": "Could not join group. Please try again."}
            
        except Exception as e:
            db.rollback()
            print(f"Unexpected error in join_group: {str(e)}")
            return {"error": f"Unexpected error in join_group: {str(e)}"}
            
        finally:
            db.close()

    @staticmethod
    def get_group(group_id: str):
        db = SessionLocal()
        try:
            group_uuid = uuid.UUID(str(group_id))
        except Exception:
            db.close()
            return {"error": "Invalid group_id"}
        group = db.query(Group).filter(Group.id == group_uuid).first()
        db.close()
        if not group:
            return {"error": "Group not found"}
        return {
            "id": str(group.id),
            "name": group.name,
            "contribution_amount": group.contribution_amount,
            "cycle": group.cycle
        }

    @staticmethod
    def get_user_groups(user_phone: str):
        db = SessionLocal()
        user = db.query(User).filter(User.phone == user_phone).first()
        if not user:
            db.close()
            return []
        memberships = db.query(Membership).filter(Membership.user_id == user.id).all()
        group_ids = [m.group_id for m in memberships]
        groups = db.query(Group).filter(Group.id.in_(group_ids)).all() if group_ids else []
        db.close()
        return [{
            "id": str(g.id),
            "name": g.name,
            "contribution_amount": g.contribution_amount,
            "cycle": g.cycle
        } for g in groups]