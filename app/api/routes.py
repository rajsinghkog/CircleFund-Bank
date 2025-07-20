
from fastapi import APIRouter, Depends, Request
from typing import List

router = APIRouter()

# --- Auth ---



from app.api.services.user_service import UserService



@router.post('/signup')
async def signup(request: Request):
    data = await request.json()
    name = data.get('name')
    phone = data.get('phone')
    if not name or not phone:
        return {"error": "Name and phone required"}
    return UserService.signup(name, phone)



@router.get('/me')
async def get_me(request: Request):
    phone = request.query_params.get('phone')
    return UserService.get_user_by_phone(phone)

# --- Group ---
@router.get('/groups')
def list_groups():
    # List available groups
    return {"groups": []}

@router.post('/groups/join')
def join_group():
    # Join group
    return {"message": "Joined group"}

@router.get('/groups/{id}')
def get_group(id: str):
    # Get group details
    return {"group_id": id}

# --- Deposit ---
@router.post('/deposit')
def submit_deposit():
    # Submit ₹5 deposit
    return {"message": "Deposit submitted"}

@router.get('/deposit/history')
def deposit_history():
    # View deposit history
    return {"history": []}

# --- Loan ---
@router.post('/loan/request')
def request_loan():
    # Request a loan
    return {"message": "Loan requested"}

@router.get('/loan/{id}')
def view_loan(id: str):
    # View loan details
    return {"loan_id": id}

@router.post('/loan/{id}/vote')
def vote_on_loan(id: str):
    # Vote on loan request
    return {"loan_id": id, "message": "Vote submitted"}

@router.post('/loan/{id}/repay')
def repay_loan(id: str):
    # Repay loan
    return {"loan_id": id, "message": "Repayment submitted"}
