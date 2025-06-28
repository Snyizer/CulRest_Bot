"""
Утилиты для ресторанного бота
"""

from .data_manager import data_manager
from .callback_data import (
    MenuCallback, 
    ItemCallback, 
    FavoritesCallback, 
    OrderCallback,
    NavigationCallback
)

__all__ = [
    "data_manager",
    "MenuCallback",
    "ItemCallback", 
    "FavoritesCallback",
    "OrderCallback",
    "NavigationCallback"
]
