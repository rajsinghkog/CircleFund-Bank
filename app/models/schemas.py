from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum
from uuid import UUID

class TransactionType(str, Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    LOAN_REQUEST = "loan_request"
    LOAN_WITHDRAWAL = "loan_withdrawal"
    REPAYMENT = "repayment"

class GroupCycle(str, Enum):
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"

class GroupCreate(BaseModel):
    name: str
    contribution_amount: float = Field(..., gt=0, description="Contribution amount must be greater than 0")
    cycle: GroupCycle

class LoanRequestBase(BaseModel):
    group_id: UUID
    amount: float = Field(..., gt=0, description="Loan amount must be greater than 0")
    due_days: Optional[int] = Field(30, description="Number of days until the loan is due")

class LoanRequestCreate(LoanRequestBase):
    pass

class LoanRequestResponse(LoanRequestBase):
    id: UUID
    user_id: UUID
    status: str
    created_at: datetime
    due_date: Optional[datetime]
    withdrawn_at: Optional[datetime]
    group_name: Optional[str] = None

    class Config:
        from_attributes = True

class LoanWithdrawRequest(BaseModel):
    pass  # No additional fields needed, just the loan ID in the path

class TransactionBase(BaseModel):
    amount: float
    type: TransactionType
    reference_id: UUID
    status: str

class TransactionResponse(TransactionBase):
    id: UUID
    user_id: UUID
    group_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
