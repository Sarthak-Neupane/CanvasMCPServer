from enum import Enum

class WorkflowState(str, Enum):
    UNPUBLISHED = "unpublished"
    AVAILABLE = "available"
    COMPLETED = "completed"
    DELETED = "deleted"
