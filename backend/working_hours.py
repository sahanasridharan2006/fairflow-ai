"""
Working Hours Module

Replaces availability_units with working_hours for Amazon-scale logistics reality.
Measures labor intensity per hour, not per shift or attendance.
"""

from typing import Optional


def get_working_hours(status: str, custom_hours: Optional[float] = None) -> float:
    """
    Returns actual working hours based on driver status.
    
    Working hours represent how many hours a driver actually worked.
    This is the denominator for fairness calculations.
    
    Args:
        status: Driver status string ("ACTIVE", "SICK", "ABSENT", "HALF_SHIFT", "CUSTOM")
        custom_hours: Custom hours value when status is "CUSTOM"
    
    Returns:
        float: Actual working hours for that day
        
    Examples:
        - Full working day (ACTIVE) → 8.0 hours
        - Half day / short shift → 4.0 hours
        - Leave / absent → 0.0 hours
        - Sick (reduced hours, protected) → 4.0 hours
        - Long-haul driver → 10-12 hours (set via custom_hours)
    """
    
    working_hours_map = {
        "ACTIVE": 8.0,       # Standard 8-hour shift
        "SICK": 4.0,         # Reduced hours, protected from hard routes
        "ABSENT": 0.0,       # Leave / not available
        "HALF_SHIFT": 4.0,   # Part-time / 4-hour shift
    }
    
    if status == "CUSTOM" and custom_hours is not None:
        # Validate custom hours (reasonable range: 0-16 hours)
        if 0.0 <= custom_hours <= 16.0:
            return custom_hours
        else:
            raise ValueError(f"Custom working hours must be between 0 and 16, got {custom_hours}")
    
    return working_hours_map.get(status, 8.0)  # Default to 8 hours if unknown


def calculate_effort_per_hour(effort: float, working_hours: float) -> Optional[float]:
    """
    Calculate effort per working hour - the KEY fairness metric.
    
    This replaces normalized_effort = effort / availability_units
    with normalized_effort = effort / working_hours
    
    Args:
        effort: Raw effort score for the period
        working_hours: Actual hours worked that day
    
    Returns:
        float: Effort per working hour
        None: If working_hours is 0 (driver was absent)
        
    Examples:
        - Effort 60, Hours 8 → 7.5 per hour (normal intensity)
        - Effort 60, Hours 4 → 15.0 per hour (HIGH intensity! Part-timer overloaded)
        - Effort 90, Hours 12 → 7.5 per hour (long haul but FAIR intensity)
        - Effort 0, Hours 0 → None (driver absent, exclude from calculations)
    """
    
    # Handle absent drivers
    if working_hours == 0:
        return None  # Cannot calculate effort per hour for absent drivers
    
    # Calculate effort per hour
    return effort / working_hours


def is_active_for_fairness(working_hours: float, normalized_effort: Optional[float]) -> bool:
    """
    Determine if a snapshot should be included in fairness calculations.
    
    Args:
        working_hours: Actual hours worked
        normalized_effort: Calculated effort per hour (can be None)
    
    Returns:
        bool: True if should be included in fairness metrics
    """
    
    # Exclude if driver was absent (0 hours)
    if working_hours == 0:
        return False
    
    # Exclude if normalized effort couldn't be calculated
    if normalized_effort is None:
        return False
    
    return True


def format_working_hours_explanation(status: str, working_hours: float) -> str:
    """
    Generate human-readable explanation of working hours for UI display.
    
    Args:
        status: Driver status
        working_hours: Actual hours worked
    
    Returns:
        str: Human-readable explanation
    """
    
    if status == "ABSENT":
        return "On leave (0 hours)"
    elif status == "SICK":
        return f"Sick day ({working_hours:.1f} hours, protected route)"
    elif status == "HALF_SHIFT":
        return f"Part-time shift ({working_hours:.1f} hours)"
    elif working_hours > 8:
        return f"Extended shift ({working_hours:.1f} hours)"
    elif working_hours < 8:
        return f"Reduced hours ({working_hours:.1f} hours)"
    else:
        return f"Standard shift ({working_hours:.1f} hours)"
