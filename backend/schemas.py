from pydantic import BaseModel
from typing import Optional, List
from datetime import date

class Token(BaseModel):
    access_token: str
    token_type: str
    driver_id: int | None = None
    name: str | None = None
    email: str | None = None
    role: str | None = None

class TokenData(BaseModel):
    email: Optional[str] = None

class UserBase(BaseModel):
    email: str

class UserLogin(UserBase):
    password: str

class FilterRequest(BaseModel):
    start_date: str  # ISO format YYYY-MM-DD
    end_date: str

class MockRoute(BaseModel):
    address_id: str
    address: str
    area_type: str
    floors: int
    stairs_present: bool
    distance_km: float
    heavy_packages_count: int
    traffic_level: str
    weather_severity: str
    computed_effort: Optional[float] = None
    difficulty_label: Optional[str] = None

class MLRecommendationRequest(BaseModel):
    route_features: dict # Flexible to accept any route structure
    driver_id: int

class BatchRecommendationRequest(BaseModel):
    route_features: dict

class DriverSignupRequest(BaseModel):
    name: str
    email: str
    password: str  # User's chosen password

class RouteFactors(BaseModel):
    apartments: int = 0
    stairs: bool = False
    heavy_boxes: int = 0
    traffic: bool = False
    rain: bool = False

class AssignRouteRequest(BaseModel):
    driver_id: int  # Use ID for stability
    difficulty: str
    address: Optional[str] = None
    route_factors: RouteFactors

class RouteBase(BaseModel):
    address: Optional[str] = None
    difficulty: str
    stops: int
    apartments: int
    stairs: bool
    heavy_boxes: int
    traffic_level: str
    weather_condition: str
    calculated_effort_score: float

class RouteDisplay(RouteBase):
    id: int
    date: date
    status: str
    
    class Config:
        from_attributes = True

class DriverStatsDisplay(BaseModel):
    effort_today: float
    credits_today: float
    total_balance: float
    user_id: int
    
    class Config:
        from_attributes = True

class DriverDashboard(BaseModel):
    stats: DriverStatsDisplay
    route: Optional[RouteDisplay]
    team_average: float
    message: str
    status: str # "ACTIVE", "SICK", "ABSENT"

    class Config:
        from_attributes = True

class FeedbackCreate(BaseModel):
    route_id: int
    difficulty: str # "Easy", "Normal", "Hard"
    comment: Optional[str] = None

class AdminDriverView(BaseModel):
    id: int
    name: str
    status: str # "ACTIVE", "SICK", "ABSENT"
    stats: DriverStatsDisplay
    current_route_difficulty: Optional[str]
    current_route_address: Optional[str] = None
    alert: Optional[str]
    alert_reason: Optional[str]
    effort_7d: float = 0.0
    credits_7d: float = 0.0
    balance_7d: float = 0.0
    readiness_status: str = "Ready"

    class Config:
        from_attributes = True

class AdminAction(BaseModel):
    driver_id: int
    action: str # "assign_easy", "assign_medium", "assign_hard"

class FairnessHistoryDisplay(BaseModel):
    date: date
    daily_effort: float
    team_average: float
    credits_earned: float
    balance_snapshot: float

    class Config:
        from_attributes = True
