from .hcs import HCSClient
from .http import HTTPClient, HTTPRequest
from .model import Board, School
from .user import User
from .utils import *

__version__ = "1.3.1"
__all__ = ("HCSClient", "HTTPClient", "HTTPRequest", "Board", "School", "User")
