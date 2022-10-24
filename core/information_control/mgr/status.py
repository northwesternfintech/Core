from enum import Enum


class WebSocketStatus(Enum):
    """Enumeration for web socket statuses"""
    WORKING = "working"
    FAILED = "failed"
    NOT_RUNNING = "not running"


class BacktestStatus(Enum):
    """Enumeration for backtest statuses"""
    WORKING = "working"
    FAILED = "failed"
