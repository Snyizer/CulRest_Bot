"""
Клавиатуры для ресторанного бота
"""

from .navigation_keyboards import (
    main_menu_keyboard,
    back_to_main_keyboard,
    back_keyboard,
    pagination_keyboard
)

from .menu_keyboards import (
    cuisines_keyboard,
    categories_keyboard,
    all_categories_keyboard,
    items_keyboard,
    item_keyboard
)

__all__ = [
    "main_menu_keyboard",
    "back_to_main_keyboard", 
    "back_keyboard",
    "pagination_keyboard",
    "cuisines_keyboard",
    "categories_keyboard",
    "all_categories_keyboard",
    "items_keyboard",
    "item_keyboard"
]
