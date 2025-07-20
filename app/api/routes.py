
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
    return UserService.signup(name, phone, password)



@router.get('/me')
async def get_me(request: Request):
    phone = request.query_params.get('phone')
    user_id = request.cookies.get('user_id')
    if not phone and not user_id:
        return {"error": "phone or user_id required"}
    if phone:
        return UserService.get_user_by_phone(phone)
    # If user_id is present, fetch user by id
    from app.db.models import User
    from app.db.database import SessionLocal
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    db.close()
    if not user:
        return {"error": "User not found"}
    return {"user": {"id": str(user.id), "name": user.name, "phone": user.phone}}

@router.post('/signin')
async def signin(request: Request, response: Response):
    data = await request.json()
    phone = data.get('phone')
    password = data.get('password')
    if not phone or not password:
        return {"error": "Phone and password required"}
    result = UserService.signin(phone, password)
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
    return {"groups": GroupService.list_groups()}

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

@router.get('/groups/{id}')
def get_group(id: str):
    return GroupService.get_group(id)

# --- Deposit ---
from app.api.services.deposit_service import DepositService


@router.post('/deposit')
def submit_deposit(request: Request):
    # Expecting JSON: {"phone": ..., "group_id": ..., "amount": ...}
    import asyncio
    async def get_data():
        return await request.json()
    data = asyncio.run(get_data())
    phone = data.get('phone')
    group_id = data.get('group_id')
    amount = data.get('amount')
    if not phone or not group_id or amount is None:
        return {"error": "phone, group_id, and amount required"}
    return DepositService.submit_deposit(phone, group_id, amount)

@router.get('/deposit/history')
def deposit_history(request: Request):
    # Accepts query params: phone, group_id (optional)
    phone = request.query_params.get('phone')
    group_id = request.query_params.get('group_id')
    if not phone:
        return {"error": "phone required"}
    return {"history": DepositService.get_deposit_history(phone, group_id)}

# --- Loan ---
from app.api.services.loan_service import LoanService
from app.api.services.vote_service import VoteService
from app.api.services.repayment_service import RepaymentService


@router.post('/loan/request')
def request_loan(request: Request):
    # Expecting JSON: {"phone": ..., "group_id": ..., "amount": ..., "due_days": ... (optional)}
    import asyncio
    async def get_data():
        return await request.json()
    data = asyncio.run(get_data())
    phone = data.get('phone')
    group_id = data.get('group_id')
    amount = data.get('amount')
    due_days = data.get('due_days', 30)
    if not phone or not group_id or amount is None:
        return {"error": "phone, group_id, and amount required"}
    return LoanService.request_loan(phone, group_id, amount, due_days)

@router.get('/loan/{id}')
def view_loan(id: str):
    return LoanService.get_loan(id)

@router.post('/loan/{id}/vote')
def vote_on_loan(id: str, request: Request):
    # Expecting JSON: {"phone": ..., "vote": ...}
    import asyncio
    async def get_data():
        return await request.json()
    data = asyncio.run(get_data())
    phone = data.get('phone')
    vote_value = data.get('vote')
    if not phone or not vote_value:
        return {"error": "phone and vote required"}
    return VoteService.vote_on_loan(phone, id, vote_value)

@router.post('/loan/{id}/repay')
def repay_loan(id: str, request: Request):
    # Expecting JSON: {"phone": ..., "amount": ...}
    import asyncio
    async def get_data():
        return await request.json()
    data = asyncio.run(get_data())
    phone = data.get('phone')
    amount = data.get('amount')
    if not phone or amount is None:
        return {"error": "phone and amount required"}
    return RepaymentService.repay_loan(phone, id, amount)

# Optionally, add repayments to view_loan
@router.get('/loan/{id}/repayments')
def get_loan_repayments(id: str):
    return {"repayments": RepaymentService.get_repayments(id)}
