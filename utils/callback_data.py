"""
Callback Data классы для inline кнопок
"""

from aiogram.filters.callback_data import CallbackData

class MenuCallback(CallbackData, prefix="menu"):
    """Callback для навигации по меню"""
    action: str
    cuisine_id: str = ""
    category_id: str = ""
    page: int = 0

class ItemCallback(CallbackData, prefix="item"):
    """Callback для действий с блюдами"""
    action: str
    item_id: str
    page: int = 0

class FavoritesCallback(CallbackData, prefix="fav"):
    """Callback для избранного"""
    action: str
    item_id: str = ""
    page: int = 0

class OrderCallback(CallbackData, prefix="order"):
    """Callback для заказа"""
    action: str
    item_id: str = ""

class NavigationCallback(CallbackData, prefix="nav"):
    """Callback для навигации"""
    action: str
    target: str = ""
