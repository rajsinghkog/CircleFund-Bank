from app.db.database import Base
from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

class User(Base):
    __tablename__ = 'users'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)  # New field for password hash
    created_at = Column(DateTime, default=datetime.utcnow)

class Group(Base):
    __tablename__ = 'groups'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    contribution_amount = Column(Float, default=5.0)
    cycle = Column(String, default='daily')

class Membership(Base):
    __tablename__ = 'memberships'
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True)
    group_id = Column(UUID(as_uuid=True), ForeignKey('groups.id'), primary_key=True)
    joined_at = Column(DateTime, default=datetime.utcnow)

class Deposit(Base):
    __tablename__ = 'deposits'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    group_id = Column(UUID(as_uuid=True), ForeignKey('groups.id'))
    amount = Column(Float, nullable=False)
    date = Column(DateTime, default=datetime.utcnow)

class LoanRequest(Base):
    __tablename__ = 'loan_requests'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    group_id = Column(UUID(as_uuid=True), ForeignKey('groups.id'))
    amount = Column(Float, nullable=False)
    status = Column(String, default='pending')
    created_at = Column(DateTime, default=datetime.utcnow)
    due_date = Column(DateTime)

class Vote(Base):
    __tablename__ = 'votes'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    loan_id = Column(UUID(as_uuid=True), ForeignKey('loan_requests.id'))
    voter_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    vote = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

class Repayment(Base):
    __tablename__ = 'repayments'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    loan_id = Column(UUID(as_uuid=True), ForeignKey('loan_requests.id'))
    amount = Column(Float, nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
