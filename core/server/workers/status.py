from enum import Enum


class WorkerStatus(Enum):
    """Enumeration for worker statuses"""
    WORKING = "working"
    FAILED = "failed"
    STOPPED = "stopped"
