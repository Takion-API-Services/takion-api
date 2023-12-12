
class TakionAPIException(Exception):
    """
    # Takion API Exception
    Base exception for all exceptions raised by the Takion API
    """
    pass

class IpBanException(TakionAPIException):
    """
    # IP Ban Exception
    Exception raised when the IP is banned
    """
    pass

class BadResponseException(TakionAPIException):
    """
    # Bad Response Exception
    Exception raised when the response is invalid
    """
    pass