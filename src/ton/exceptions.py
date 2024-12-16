# src/ton/exceptions.py
class TonError(Exception):
    """Base exception for TON-related errors"""
    pass

class TonAPIError(TonError):
    """API-related errors"""
    pass

class TonDataError(TonError):
    """Data processing errors"""
    pass