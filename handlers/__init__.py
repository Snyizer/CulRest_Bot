"""
Обработчики для ресторанного бота
"""

from . import menu_handlers
from . import search_handlers  
from . import order_handlers
from . import favorites_handlers

__all__ = [
    "menu_handlers",
    "search_handlers", 
    "order_handlers",
    "favorites_handlers"
]
