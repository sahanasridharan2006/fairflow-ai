"""
Availability Units Module

Handles calculation of availability units and normalized effort
to ensure fairness calculations are relative to work availability.
"""

from typing import Optional


def get_availability_units(status: str, custom_value: Optional[float] = None) -> float:
    """
    Returns availability units based on driver status.
    
    Availability units represent how much a driver was actually available to work.
    
    Args:
        status: Driver status string ("ACTIVE", "SICK", "ABSENT", "HALF_SHIFT", "CUSTOM")
        custom_value: Custom availability value (0.0-1.0) when status is "CUSTOM"
    
    Returns:
        float: Availability units (0.0 to 1.0)
        
    Examples:
        - Full working day (ACTIVE) → 1.0
        - Half day / short shift → 0.5
        - Leave / absent → 0.0
        - Sick (reduced load, protected) → 0.5
    """
    
    availability_map = {
        "ACTIVE": 1.0,      # Full day
        "SICK": 0.5,        # Reduced capacity, protected from hard routes
        "ABSENT": 0.0,      # Leave / not available
        "HALF_SHIFT": 0.5,  # Part-time / half day
    }
    
    if status == "CUSTOM" and custom_value is not None:
        # Validate custom value
        if 0.0 <= custom_value <= 1.0:
            return custom_value
        else:
            raise ValueError(f"Custom availability must be between 0.0 and 1.0, got {custom_value}")
    
    return availability_map.get(status, 1.0)  # Default to 1.0 if unknown status


def calculate_normalized_effort(effort: float, availability_units: float) -> Optional[float]:
    """
    Calculate normalized effort (effort per availability unit).
    
    This is the KEY metric for fairness - it shows workload intensity
    relative to how much the driver was actually available.
    
    Args:
        effort: Raw effort score for the period
        availability_units: How much the driver was available (0.0-1.0)
    
    Returns:
        float: Normalized effort (effort / availability_units)
        None: If availability_units is 0 (driver was absent)
        
    Examples:
        - Effort 60, Availability 1.0 → Normalized 60.0
        - Effort 60, Availability 0.5 → Normalized 120.0 (high intensity!)
        - Effort 30, Availability 0.5 → Normalized 60.0 (same as full-timer)
        - Effort 0, Availability 0.0 → None (driver was absent, exclude from calculations)
    """
    
    # Handle absent drivers
    if availability_units == 0:
        return None  # Cannot calculate normalized effort for absent drivers
    
    # Calculate normalized effort
    return effort / availability_units


def is_available_for_calculation(availability_units: float, normalized_effort: Optional[float]) -> bool:
    """
    Determine if a snapshot should be included in fairness calculations.
    
    Args:
        availability_units: Driver's availability (0.0-1.0)
        normalized_effort: Calculated normalized effort (can be None)
    
    Returns:
        bool: True if should be included in fairness metrics
    """
    
    # Exclude if driver was absent
    if availability_units == 0:
        return False
    
    # Exclude if normalized effort couldn't be calculated
    if normalized_effort is None:
        return False
    
    return True


def format_availability_explanation(status: str, availability_units: float) -> str:
    """
    Generate human-readable explanation of availability for UI display.
    
    Args:
        status: Driver status
        availability_units: Calculated availability (0.0-1.0)
    
    Returns:
        str: Human-readable explanation
    """
    
    if status == "ABSENT":
        return "On leave (not available)"
    elif status == "SICK":
        return "Sick day (protected, reduced capacity)"
    elif status == "HALF_SHIFT":
        return "Half shift (part-time)"
    elif availability_units < 1.0:
        return f"Partial availability ({int(availability_units * 100)}%)"
    else:
        return "Full day"
