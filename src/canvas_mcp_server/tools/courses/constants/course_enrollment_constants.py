from enum import Enum

class EnrollmentType(str, Enum):
    """Canvas enrollment types for filtering courses."""
    TEACHER = "teacher"
    STUDENT = "student" 
    TA = "ta"
    OBSERVER = "observer"
    DESIGNER = "designer"


class EnrollmentState(str, Enum):
    """Canvas enrollment states for filtering active/inactive enrollments."""
    ACTIVE = "active"
    INVITED_OR_PENDING = "invited_or_pending"
    COMPLETED = "completed"