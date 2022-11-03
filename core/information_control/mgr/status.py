from enum import Enum


class WebSocketStatus(Enum):
    """Enumeration for web socket statuses"""
    WORKING = "working"
    FAILED = "failed"
    STOPPED = "stopped"


class BacktestStatus(Enum):
    """Enumeration for backtest statuses"""
    WORKING = "working"
    FAILED = "failed"
