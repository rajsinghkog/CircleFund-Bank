
from fastapi import APIRouter, Request, Response

router = APIRouter()

# --- Auth ---



from app.api.services.user_service import UserService



@router.post('/signup')
async def signup(request: Request):
    data = await request.json()
    name = data.get('name')
    phone = data.get('phone') or data.get('username')
    if not name or not phone:
        return {"error": "Name and phone required"}
    from app.models.user import UserCreate
    return UserService.signup(UserCreate(id=None, name=name, phone=phone, password=""))



@router.get('/me')
async def get_me(request: Request):
    phone = request.query_params.get('phone')
    user_id = request.cookies.get('user_id')
    if not phone and not user_id:
        return {"error": "phone or user_id required"}
    if phone:
        return UserService.get_user_profile(phone)
    # If user_id is present, use centralized helper
    return UserService.get_user_profile_by_id(user_id)

@router.post('/signin')
async def signin(request: Request, response: Response):
    data = await request.json()
    phone = data.get('phone') or data.get('username')
    # Password not required in simplified auth
    if not phone:
        return {"error": "Username/phone required"}
    from app.models.user import UserLogin
    result = UserService.signin(UserLogin(phone=phone, password=""))
    if result.get('user'):
        # Set cookie with user id
        response.set_cookie(key="user_id", value=result['user']['id'], httponly=True, samesite="lax")
    return result

@router.post('/signout')
async def signout(response: Response):
    response.delete_cookie(key="user_id")
    return {"message": "Signed out"}

# --- Group ---
from app.api.services.group_service import GroupService
from app.models.schemas import GroupCreate


@router.get('/groups')
def list_groups():
    return GroupService.list_groups()

@router.post('/groups')
async def create_group(payload: GroupCreate):
    return GroupService.create_group(
        name=payload.name,
        contribution_amount=payload.contribution_amount,
        cycle=payload.cycle.value
    )

@router.post('/groups/join')
async def join_group(request: Request):
    # Expecting JSON: {"phone": ..., "group_id": ...}
    data = await request.json()
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


@router.post('/deposit')
async def submit_deposit(request: Request):
    data = await request.json()
    user_phone = data.get('phone')
    group_id = data.get('group_id')
    amount = data.get('amount')
    expected_deposit_id = data.get('expected_deposit_id')
    
    if not all([user_phone, group_id, amount]):
        return {"error": "phone, group_id, and amount required"}
    # Normalize amount
    try:
        amount = float(amount)
    except Exception:
        return {"error": "amount must be a number"}
    if amount <= 0:
        return {"error": "amount must be greater than 0"}
    
    # Submit the deposit (handles expected deposit internally)
    return DepositService.submit_deposit(user_phone, group_id, amount, expected_deposit_id)

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
# Since this router is mounted at /api from main.py, use relative prefix here
router.include_router(loans_router, prefix="/loans", tags=["loans"])

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

# Define fixed routes BEFORE the dynamic {id} route to avoid collisions
# --- Voting dashboard legacy support ---
@router.get('/loan/pending')
def pending_loans_for_user(request: Request):
    user_id = request.query_params.get('user_id')
    if not user_id:
        return []
    return LoanService.get_pending_loans_for_user(user_id)

# My loans with approvals (legacy for loan_request page sidebar)
@router.get('/loan/my')
def my_loans(request: Request):
    user_id = request.query_params.get('user_id')
    status = request.query_params.get('status')
    if not user_id:
        return []
    return LoanService.get_loans_for_user_with_votes(user_id, status)

# All loans (admin/dashboard helper)
@router.get('/loan/all')
def all_loans(request: Request):
    status = request.query_params.get('status')
    group_id = request.query_params.get('group_id')
    return LoanService.get_all_loans(status=status, group_id=group_id)

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
    # Map frontend values to service values
    mapped_vote = 'yes' if vote == 'approve' else 'no'
    return VoteService.vote_on_loan(voter_phone, id, mapped_vote)

@router.post('/loan/{id}/repay')
async def repay_loan(id: str, request: Request):
    data = await request.json()
    amount = data.get('amount')
    if not amount or amount <= 0:
        return {"error": "amount must be greater than 0"}
    user_id = request.cookies.get('user_id')
    if not user_id:
        return {"error": "Not authenticated"}
    # Resolve user via helper
    user_profile = UserService.get_user_profile_by_id(user_id)
    if isinstance(user_profile, dict) and user_profile.get('error'):
        return user_profile
    user_phone = user_profile['user']['phone']
    return RepaymentService.repay_loan(user_phone, id, amount)

# Optionally, add repayments to view_loan
@router.get('/loan/{id}/repayments')
def get_loan_repayments(id: str):
    return RepaymentService.get_repayments(id)
