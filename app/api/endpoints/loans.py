from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from app.api.services.loan_service import LoanService
from app.api.auth.auth_bearer import JWTBearer
from app.models.schemas import LoanRequestCreate, LoanRequestResponse, LoanWithdrawRequest

router = APIRouter()

@router.get("/_verify")
async def verify(current_user: Dict[str, Any] = Depends(JWTBearer())):
    return current_user

@router.get("", response_model=List[LoanRequestResponse])
async def get_loans(
    current_user: Dict[str, Any] = Depends(JWTBearer()),
    status: Optional[str] = Query(None, description="Filter by status (pending/approved/withdrawn/rejected)")
):
    """
    Get all loan requests for the current user, optionally filtered by status.
    """
    try:
        user_id = str(current_user.get('sub'))
        loans = LoanService.get_loans_by_user(user_id, status)
        if isinstance(loans, dict) and 'error' in loans:
            raise HTTPException(status_code=400, detail=loans['error'])
        return loans
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/request", response_model=dict)
async def request_loan(
    request: LoanRequestCreate,
    current_user: Dict[str, Any] = Depends(JWTBearer())
):
    """
    Create a new loan request.
    """
    try:
        result = LoanService.request_loan(
            user_phone=current_user.get('phone'),
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
    current_user: Dict[str, Any] = Depends(JWTBearer())
):
    """
    Withdraw an approved loan amount.
    """
    try:
        result = LoanService.withdraw_loan(
            loan_id=loan_id,
            user_id=str(current_user.get('sub'))
        )
        if 'error' in result:
            raise HTTPException(status_code=400, detail=result['error'])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
