from email.policy import default
from sqlalchemy import Boolean, Column, Integer, String,DateTime,Float
from owndatabase import Base
from sqlalchemy.sql import func


class bank(Base):
    __tablename__ = 'Ban'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
   
    amount = Column(Integer)  
    interest_rate = Column(Float, default=0.05) 
    timestamp = Column(DateTime, default=func.now(), onupdate=func.now())  
