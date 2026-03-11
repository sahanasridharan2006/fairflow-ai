from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String)  # "driver" or "admin"
    status = Column(String, default="ACTIVE") # "ACTIVE", "ABSENT", "SICK"
    
    # Relationships
    driver_stats = relationship("DriverStats", back_populates="user", uselist=False)
    routes = relationship("Route", back_populates="driver")
    fairness_history = relationship("FairnessHistory", back_populates="driver")

class DriverStats(Base):
    __tablename__ = "driver_stats"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    total_balance = Column(Float, default=0.0)  # Total Fairness Balance
    credits_today = Column(Float, default=0.0)
    effort_today = Column(Float, default=0.0)
    
    user = relationship("User", back_populates="driver_stats")

class Route(Base):
    __tablename__ = "routes"

    id = Column(Integer, primary_key=True, index=True)
    driver_id = Column(Integer, ForeignKey("users.id"))
    date = Column(Date, default=datetime.utcnow().date)
    address = Column(String) # Physical destination address
    difficulty = Column(String)  # "Easy", "Medium", "Hard"
    status = Column(String, default="Assigned") # "Assigned", "Completed"
    
    # Mock Effort Factors
    stops = Column(Integer, default=0)
    apartments = Column(Integer, default=0)
    stairs = Column(Boolean, default=False)
    heavy_boxes = Column(Integer, default=0)
    traffic_level = Column(String, default="Normal") # Low, Normal, High
    weather_condition = Column(String, default="Clear") # Clear, Rain, Snow
    
    calculated_effort_score = Column(Float, default=0.0)
    
    # Feedback
    feedback_score = Column(String, nullable=True) # "Easy", "Normal", "Hard"
    feedback_comment = Column(String, nullable=True)

    driver = relationship("User", back_populates="routes")

class FairnessHistory(Base):
    __tablename__ = "fairness_history"
    
    id = Column(Integer, primary_key=True, index=True)
    driver_id = Column(Integer, ForeignKey("users.id"))
    date = Column(Date, default=datetime.utcnow().date)
    daily_effort = Column(Float)
    team_average = Column(Float) # Snapshot of team avg that day
    credits_earned = Column(Float)
    balance_snapshot = Column(Float)
    
    driver = relationship("User", back_populates="fairness_history")

class FairnessSnapshot(Base):
    """Stores daily fairness snapshots for AI drift detection"""
    __tablename__ = "fairness_snapshots"
    
    id = Column(Integer, primary_key=True, index=True)
    driver_id = Column(Integer, ForeignKey("users.id"))
    date = Column(Date, nullable=False)
    effort = Column(Float, nullable=False)  # Raw effort score
    credits = Column(Float, nullable=False)
    balance = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Working-hours based fairness (Amazon-scale logistics)
    working_hours = Column(Float, nullable=False, default=8.0)  # Actual hours worked that day
    normalized_effort = Column(Float, nullable=True)  # effort / working_hours (None if working_hours=0)
    
    # DEPRECATED: Keep for migration compatibility
    availability_units = Column(Float, default=1.0)  # Legacy field, will be removed after migration
    
    driver = relationship("User")
