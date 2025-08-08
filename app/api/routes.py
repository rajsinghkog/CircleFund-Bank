
from fastapi import APIRouter, Depends, Request, Response
from typing import List

router = APIRouter()

# --- Auth ---



from app.api.services.user_service import UserService



@router.post('/signup')
async def signup(request: Request):
    data = await request.json()
    name = data.get('name')
    phone = data.get('phone')
    password = data.get('password')
    if not name or not phone or not password:
        return {"error": "Name, phone, and password required"}
    from app.models.user import UserCreate
    return UserService.signup(UserCreate(id=None, name=name, phone=phone, password=password))



@router.get('/me')
async def get_me(request: Request):
    phone = request.query_params.get('phone')
    user_id = request.cookies.get('user_id')
    if not phone and not user_id:
        return {"error": "phone or user_id required"}
    if phone:
        return UserService.get_user_by_phone(phone)
    # If user_id is present, fetch user by id
    from app.db.models import User, Membership
    from app.db.database import SessionLocal
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    group_id = None
    if user:
        membership = db.query(Membership).filter(Membership.user_id == user.id).first()
        if membership:
            group_id = str(membership.group_id)
    db.close()
    if not user:
        return {"error": "User not found"}
    return {"user": {"id": str(user.id), "name": user.name, "phone": user.phone, "group_id": group_id}}

@router.post('/signin')
async def signin(request: Request, response: Response):
    data = await request.json()
    phone = data.get('phone')
    password = data.get('password')
    if not phone or not password:
        return {"error": "Phone and password required"}
    from app.models.user import UserLogin
    result = UserService.signin(UserLogin(phone=phone, password=password))
    if result.get('user'):
        # Set a secure cookie with user id
        response.set_cookie(key="user_id", value=result['user']['id'], httponly=True, samesite="lax")
    return result

@router.post('/signout')
async def signout(response: Response):
    response.delete_cookie(key="user_id")
    return {"message": "Signed out"}

# --- Group ---
from app.api.services.group_service import GroupService


@router.get('/groups')
def list_groups():
    return GroupService.list_groups()

@router.post('/groups')
async def create_group(request: Request):
    data = await request.json()
    name = data.get('name')
    contribution_amount = data.get('contribution_amount')
    cycle = data.get('cycle')
    creator_phone = data.get('creator_phone')
    return GroupService.create_group(name=name, contribution_amount=contribution_amount, cycle=cycle, creator_phone=creator_phone)

@router.post('/groups/join')
def join_group(request: Request):
    # Expecting JSON: {"phone": ..., "group_id": ...}
    import asyncio
    async def get_data():
        return await request.json()
    data = asyncio.run(get_data())
    phone = data.get('phone')
    group_id = data.get('group_id')
    if not phone or not group_id:
        return {"error": "phone and group_id required"}
    return GroupService.join_group(phone, group_id)

@router.get('/groups/user')
def get_user_groups(request: Request):
    phone = request.query_params.get('phone')
    if not phone:
        return {"error": "phone required"}
    result = GroupService.get_user_groups(phone)
    return result

@router.get('/groups/{id}')
def get_group(id: str):
    return GroupService.get_group(id)

# --- Deposit ---
from app.api.services.deposit_service import DepositService
from datetime import datetime


@router.post('/deposit')
async def submit_deposit(request: Request):
    data = await request.json()
    user_phone = data.get('phone')
    group_id = data.get('group_id')
    amount = data.get('amount')
    expected_deposit_id = data.get('expected_deposit_id')
    
    if not all([user_phone, group_id, amount]):
        return {"error": "phone, group_id, and amount required"}
    
    # Submit the deposit
    result = DepositService.submit_deposit(user_phone, group_id, amount)
    
    # If we have an expected deposit ID, mark it as completed
    if expected_deposit_id and isinstance(result, dict) and 'deposit_id' in result:
        from app.db.database import SessionLocal
        from app.db.models import ExpectedDeposit, User
        db = SessionLocal()
        try:
            expected = db.query(ExpectedDeposit).filter(
                ExpectedDeposit.id == expected_deposit_id,
                ExpectedDeposit.user_id == db.query(User).filter(User.phone == user_phone).first().id
            ).first()
            
            if expected:
                expected.status = 'completed'
                expected.deposit_id = result['deposit_id']
                expected.updated_at = datetime.utcnow()
                db.commit()
        except Exception as e:
            db.rollback()
            print(f"Error updating expected deposit: {str(e)}")
        finally:
            db.close()
    
    return result

@router.get('/deposit/history')
def deposit_history(request: Request):
    phone = request.query_params.get('phone')
    group_id = request.query_params.get('group_id')
    if not phone:
        return {"error": "phone required"}
    return DepositService.get_deposit_history(phone, group_id)

@router.get('/deposit/pending')
def pending_deposits(request: Request):
    phone = request.query_params.get('phone')
    group_id = request.query_params.get('group_id')
    if not phone:
        return {"error": "phone required"}
    return DepositService.get_pending_deposits(phone, group_id)

@router.get('/balance')
def get_balance(request: Request):
    phone = request.query_params.get('phone')
    if not phone:
        return {"error": "phone required"}
    from app.api.services.deposit_service import DepositService
    return DepositService.get_total_and_available_balance(phone)

@router.get('/statement')
def get_statement(request: Request):
    phone = request.query_params.get('phone')
    if not phone:
        return {"error": "phone required"}
    from app.api.services.deposit_service import DepositService
    return {"statement": DepositService.get_account_statement(phone)}

# --- Loan ---
from app.api.services.loan_service import LoanService
from app.api.services.vote_service import VoteService
from app.api.services.repayment_service import RepaymentService

# Import the new loans router
from app.api.endpoints.loans import router as loans_router

# Include the loans router with the /api/loans prefix
router.include_router(loans_router, prefix="/api/loans", tags=["loans"])

# Keep the old endpoints for backward compatibility
@router.post('/loan/request')
async def request_loan(request: Request):
    data = await request.json()
    phone = data.get('phone')
    group_id = data.get('group_id')
    amount = data.get('amount')
    if not phone or not group_id or not amount:
        return {"error": "phone, group_id, and amount required"}
    return LoanService.request_loan(phone, group_id, amount)

@router.get('/loan/{id}')
def view_loan(id: str):
    return LoanService.get_loan(id)

@router.post('/loan/{id}/vote')
async def vote_on_loan(id: str, request: Request):
    data = await request.json()
    voter_phone = data.get('voter_phone')
    vote = data.get('vote')  # 'approve' or 'reject'
    if not voter_phone or not vote or vote not in ['approve', 'reject']:
        return {"error": "voter_phone and vote ('approve' or 'reject') required"}
    return VoteService.vote_on_loan(id, voter_phone, vote)

@router.post('/loan/{id}/repay')
async def repay_loan(id: str, request: Request):
    data = await request.json()
    amount = data.get('amount')
    if not amount or amount <= 0:
        return {"error": "amount must be greater than 0"}
    return RepaymentService.make_repayment(id, amount)

# Optionally, add repayments to view_loan
@router.get('/loan/{id}/repayments')
def get_loan_repayments(id: str):
    return RepaymentService.get_repayments(id)
