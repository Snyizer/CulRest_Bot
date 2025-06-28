"""
Клавиатуры для навигации
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from utils.callback_data import NavigationCallback, MenuCallback
from config import EMOJI

def main_menu_keyboard() -> InlineKeyboardMarkup:
    """Главное меню бота"""
    builder = InlineKeyboardBuilder()

    builder.button(
        text=f"{EMOJI['menu']} Меню",
        callback_data=MenuCallback(action="cuisines")
    )
    builder.button(
        text=f"{EMOJI['search']} Поиск блюд",
        callback_data=NavigationCallback(action="search")
    )
    builder.button(
        text=f"{EMOJI['favorites']} Избранное",
        callback_data=NavigationCallback(action="favorites")
    )
    builder.button(
        text=f"{EMOJI['cart']} Мой заказ",
        callback_data=NavigationCallback(action="order")
    )

    builder.adjust(2, 2)
    return builder.as_markup()

def back_to_main_keyboard() -> InlineKeyboardMarkup:
    """Кнопка назад в главное меню"""
    builder = InlineKeyboardBuilder()

    builder.button(
        text=f"{EMOJI['home']} Главное меню",
        callback_data=NavigationCallback(action="main")
    )

    return builder.as_markup()

def back_keyboard(callback_data) -> InlineKeyboardMarkup:
    """Универсальная кнопка назад"""
    builder = InlineKeyboardBuilder()

    builder.button(
        text=f"{EMOJI['back']} Назад",
        callback_data=callback_data
    )
    builder.button(
        text=f"{EMOJI['home']} Главное меню",
        callback_data=NavigationCallback(action="main")
    )

    builder.adjust(1, 1)
    return builder.as_markup()

def pagination_keyboard(current_page: int, total_pages: int, callback_prefix: str, **kwargs) -> InlineKeyboardMarkup:
    """Клавиатура с пагинацией"""
    builder = InlineKeyboardBuilder()

    # Кнопки пагинации
    pagination_row = []

    if current_page > 0:
        if callback_prefix == "menu":
            prev_callback = MenuCallback(action="page", page=current_page - 1, **kwargs)
        elif callback_prefix == "fav":
            from utils.callback_data import FavoritesCallback
            prev_callback = FavoritesCallback(action="page", page=current_page - 1)
        else:
            prev_callback = NavigationCallback(action="page", target=str(current_page - 1))

        pagination_row.append(InlineKeyboardButton(text="◀️", callback_data=prev_callback.pack()))

    pagination_row.append(InlineKeyboardButton(
        text=f"{current_page + 1}/{total_pages}",
        callback_data="ignore"
    ))

    if current_page < total_pages - 1:
        if callback_prefix == "menu":
            next_callback = MenuCallback(action="page", page=current_page + 1, **kwargs)
        elif callback_prefix == "fav":
            from utils.callback_data import FavoritesCallback
            next_callback = FavoritesCallback(action="page", page=current_page + 1)
        else:
            next_callback = NavigationCallback(action="page", target=str(current_page + 1))

        pagination_row.append(InlineKeyboardButton(text="▶️", callback_data=next_callback.pack()))

    for btn in pagination_row:
        builder.row(btn)

    return builder.as_markup()
