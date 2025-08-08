from fastapi import APIRouter, HTTPException, Query, Request
from typing import List, Optional
from app.api.services.loan_service import LoanService
from app.api.services.user_service import UserService
from app.models.schemas import LoanRequestCreate, LoanRequestResponse, LoanWithdrawRequest

router = APIRouter()

@router.get("", response_model=List[LoanRequestResponse])
async def get_loans(
    request: Request,
    status: Optional[str] = Query(None, description="Filter by status (pending/approved/withdrawn/rejected)")
):
    """
    Get all loan requests for the current user, optionally filtered by status.
    """
    try:
        user_id = request.cookies.get('user_id') or request.query_params.get('user_id')
        if not user_id:
            return []
        loans = LoanService.get_loans_by_user(user_id, status)
        if isinstance(loans, dict) and 'error' in loans:
            raise HTTPException(status_code=400, detail=loans['error'])
        return loans
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/request", response_model=dict)
async def request_loan(
    request: LoanRequestCreate,
    req: Request
):
    """
    Create a new loan request.
    """
    try:
        # Resolve phone from cookie user_id
        user_id = req.cookies.get('user_id') or req.query_params.get('user_id')
        if not user_id:
            raise HTTPException(status_code=400, detail="user_id required")
        user = UserService.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        result = LoanService.request_loan(
            user_phone=user.phone,
            group_id=str(request.group_id),
            amount=request.amount,
            due_days=request.due_days or 30
        )
        if 'error' in result:
            raise HTTPException(status_code=400, detail=result['error'])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{loan_id}/withdraw", response_model=dict)
async def withdraw_loan(
    loan_id: str,
    request: LoanWithdrawRequest,
    req: Request
):
    """
    Withdraw an approved loan amount.
    """
    try:
        user_id = req.cookies.get('user_id') or req.query_params.get('user_id')
        if not user_id:
            raise HTTPException(status_code=400, detail="user_id required")
        result = LoanService.withdraw_loan(loan_id=loan_id, user_id=user_id)
        if 'error' in result:
            raise HTTPException(status_code=400, detail=result['error'])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
