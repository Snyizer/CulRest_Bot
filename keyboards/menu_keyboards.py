"""
Клавиатуры для меню ресторана
"""

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from utils.callback_data import MenuCallback, ItemCallback, FavoritesCallback, OrderCallback, NavigationCallback
from utils.data_manager import data_manager
from config import EMOJI, MAX_ITEMS_PER_PAGE

def cuisines_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора кухни"""
    builder = InlineKeyboardBuilder()

    cuisines = data_manager.get_cuisines()

    # Добавляем кнопку "Все кухни"
    builder.button(
        text="🌍 Все кухни",
        callback_data=MenuCallback(action="all_categories")
    )

    # Добавляем кнопки кухонь
    for cuisine_id, cuisine_data in cuisines.items():
        emoji = cuisine_data.get("emoji", "🍽️")
        name = cuisine_data.get("name", "Кухня")

        builder.button(
            text=f"{emoji} {name}",
            callback_data=MenuCallback(action="categories", cuisine_id=cuisine_id)
        )

    builder.button(
        text=f"{EMOJI['home']} Главное меню",
        callback_data=NavigationCallback(action="main")
    )

    builder.adjust(1)
    return builder.as_markup()

def categories_keyboard(cuisine_id: str) -> InlineKeyboardMarkup:
    """Клавиатура категорий для кухни"""
    builder = InlineKeyboardBuilder()

    categories = data_manager.get_categories(cuisine_id)

    for category_id, category_data in categories.items():
        emoji = category_data.get("emoji", "🍽️")
        name = category_data.get("name", "Категория")

        builder.button(
            text=f"{emoji} {name}",
            callback_data=MenuCallback(action="items", cuisine_id=cuisine_id, category_id=category_id)
        )

    builder.button(
        text=f"{EMOJI['back']} Назад",
        callback_data=MenuCallback(action="cuisines")
    )
    builder.button(
        text=f"{EMOJI['home']} Главное меню", 
        callback_data=NavigationCallback(action="main")
    )

    builder.adjust(1)
    return builder.as_markup()

def all_categories_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура всех категорий"""
    builder = InlineKeyboardBuilder()

    cuisines = data_manager.get_cuisines()

    for cuisine_id, cuisine_data in cuisines.items():
        categories = cuisine_data.get("categories", {})

        for category_id, category_data in categories.items():
            emoji = category_data.get("emoji", "🍽️")
            name = category_data.get("name", "Категория")
            cuisine_name = cuisine_data.get("name", "")

            builder.button(
                text=f"{emoji} {name} ({cuisine_name})",
                callback_data=MenuCallback(action="items", cuisine_id=cuisine_id, category_id=category_id)
            )

    builder.button(
        text=f"{EMOJI['back']} Назад",
        callback_data=MenuCallback(action="cuisines")
    )
    builder.button(
        text=f"{EMOJI['home']} Главное меню",
        callback_data=NavigationCallback(action="main")
    )

    builder.adjust(1)
    return builder.as_markup()

def items_keyboard(cuisine_id: str, category_id: str, page: int = 0) -> InlineKeyboardMarkup:
    """Клавиатура блюд в категории"""
    builder = InlineKeyboardBuilder()

    items = data_manager.get_items(cuisine_id, category_id)

    # Пагинация
    start_idx = page * MAX_ITEMS_PER_PAGE
    end_idx = start_idx + MAX_ITEMS_PER_PAGE
    page_items = items[start_idx:end_idx]

    for item in page_items:
        emoji = item.get("image", "🍽️")
        name = item.get("name", "Блюдо")
        price = item.get("price", 0)

        builder.button(
            text=f"{emoji} {name} - {price}₽",
            callback_data=ItemCallback(action="view", item_id=item["id"], page=page)
        )

    # Пагинация
    total_pages = (len(items) + MAX_ITEMS_PER_PAGE - 1) // MAX_ITEMS_PER_PAGE
    if total_pages > 1:
        pagination_row = []

        if page > 0:
            pagination_row.append(builder.button(
                text="◀️",
                callback_data=MenuCallback(
                    action="items", 
                    cuisine_id=cuisine_id, 
                    category_id=category_id,
                    page=page - 1
                )
            ))

        pagination_row.append(builder.button(
            text=f"{page + 1}/{total_pages}",
            callback_data="ignore"
        ))

        if page < total_pages - 1:
            pagination_row.append(builder.button(
                text="▶️",
                callback_data=MenuCallback(
                    action="items",
                    cuisine_id=cuisine_id,
                    category_id=category_id, 
                    page=page + 1
                )
            ))

    builder.button(
        text=f"{EMOJI['back']} Назад",
        callback_data=MenuCallback(action="categories", cuisine_id=cuisine_id)
    )
    builder.button(
        text=f"{EMOJI['home']} Главное меню",
        callback_data=NavigationCallback(action="main")
    )

    builder.adjust(1)
    return builder.as_markup()

def item_keyboard(item_id: str, user_id: int, page: int = 0) -> InlineKeyboardMarkup:
    """Клавиатура для отдельного блюда"""
    builder = InlineKeyboardBuilder()

    # Кнопка добавления в заказ
    builder.button(
        text=f"{EMOJI['add']} Добавить в заказ",
        callback_data=OrderCallback(action="add", item_id=item_id)
    )

    # Кнопка добавления/удаления из избранного
    is_favorite = data_manager.is_in_favorites(user_id, item_id)
    if is_favorite:
        builder.button(
            text=f"{EMOJI['remove']} Убрать из избранного",
            callback_data=FavoritesCallback(action="remove", item_id=item_id, page=page)
        )
    else:
        builder.button(
            text=f"{EMOJI['favorites']} В избранное",
            callback_data=FavoritesCallback(action="add", item_id=item_id, page=page)
        )

    builder.button(
        text=f"{EMOJI['back']} Назад",
        callback_data=ItemCallback(action="back", item_id=item_id, page=page)
    )
    builder.button(
        text=f"{EMOJI['home']} Главное меню",
        callback_data=NavigationCallback(action="main")
    )

    builder.adjust(2, 2)
    return builder.as_markup()
