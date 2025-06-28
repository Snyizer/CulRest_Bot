"""
Обработчики для избранного
"""

from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from utils.callback_data import NavigationCallback, FavoritesCallback, ItemCallback
from utils.data_manager import data_manager
from keyboards.navigation_keyboards import back_to_main_keyboard
from config import EMOJI, MAX_ITEMS_PER_PAGE

router = Router()

@router.callback_query(NavigationCallback.filter(F.action == "favorites"))
async def show_favorites(callback: CallbackQuery):
    """Показать избранные блюда"""
    user_id = callback.from_user.id
    favorites = data_manager.get_user_favorites(user_id)

    if not favorites:
        text = f"""
{EMOJI['favorites']} <b>Избранное</b>

У вас пока нет избранных блюд.
Добавляйте блюда в избранное через меню!
"""
        await callback.message.edit_text(
            text,
            reply_markup=back_to_main_keyboard()
        )
    else:
        await show_favorites_page(callback, favorites, 0)

    await callback.answer()

@router.callback_query(FavoritesCallback.filter(F.action == "page"))
async def show_favorites_page_callback(callback: CallbackQuery, callback_data: FavoritesCallback):
    """Показать страницу избранного"""
    user_id = callback.from_user.id
    favorites = data_manager.get_user_favorites(user_id)
    page = callback_data.page

    await show_favorites_page(callback, favorites, page)
    await callback.answer()

async def show_favorites_page(callback: CallbackQuery, favorites: list, page: int = 0):
    """Показать страницу избранного"""
    builder = InlineKeyboardBuilder()

    # Пагинация
    start_idx = page * MAX_ITEMS_PER_PAGE
    end_idx = start_idx + MAX_ITEMS_PER_PAGE
    page_favorites = favorites[start_idx:end_idx]

    text = f"{EMOJI['favorites']} <b>Избранное ({len(favorites)} блюд)</b>\n\n"

    for i, item in enumerate(page_favorites, start_idx + 1):
        emoji = item.get("image", "🍽️")
        name = item.get("name", "Блюдо")
        price = item.get("price", 0)

        text += f"{i}. {emoji} {name} - {price}₽\n"

        builder.button(
            text=f"{emoji} {name}",
            callback_data=ItemCallback(action="view", item_id=item["id"], page=page)
        )

    # Пагинация
    total_pages = (len(favorites) + MAX_ITEMS_PER_PAGE - 1) // MAX_ITEMS_PER_PAGE
    if total_pages > 1:
        pagination_row = []

        if page > 0:
            pagination_row.append(
                builder.button(
                    text="◀️",
                    callback_data=FavoritesCallback(action="page", page=page - 1)
                )
            )

        pagination_row.append(
            builder.button(
                text=f"{page + 1}/{total_pages}",
                callback_data="ignore"
            )
        )

        if page < total_pages - 1:
            pagination_row.append(
                builder.button(
                    text="▶️", 
                    callback_data=FavoritesCallback(action="page", page=page + 1)
                )
            )

    builder.button(
        text=f"{EMOJI['home']} Главное меню",
        callback_data=NavigationCallback(action="main")
    )

    builder.adjust(1)

    await callback.message.edit_text(text, reply_markup=builder.as_markup())

@router.callback_query(FavoritesCallback.filter(F.action == "add"))
async def add_to_favorites(callback: CallbackQuery, callback_data: FavoritesCallback):
    """Добавить в избранное"""
    user_id = callback.from_user.id
    item_id = callback_data.item_id

    item = data_manager.get_item(item_id)
    if not item:
        await callback.answer("❌ Блюдо не найдено")
        return

    if data_manager.add_to_favorites(user_id, item_id):
        name = item.get("name", "Блюдо")
        await callback.answer(f"⭐ {name} добавлено в избранное!")

        # Обновляем клавиатуру блюда
        page = callback_data.page
        from keyboards.menu_keyboards import item_keyboard
        new_keyboard = item_keyboard(item_id, user_id, page)
        await callback.message.edit_reply_markup(reply_markup=new_keyboard)
    else:
        await callback.answer("⚠️ Блюдо уже в избранном")

@router.callback_query(FavoritesCallback.filter(F.action == "remove"))
async def remove_from_favorites(callback: CallbackQuery, callback_data: FavoritesCallback):
    """Удалить из избранного"""
    user_id = callback.from_user.id
    item_id = callback_data.item_id

    item = data_manager.get_item(item_id)
    if not item:
        await callback.answer("❌ Блюдо не найдено")
        return

    if data_manager.remove_from_favorites(user_id, item_id):
        name = item.get("name", "Блюдо")
        await callback.answer(f"🗑️ {name} удалено из избранного")

        # Обновляем клавиатуру блюда
        page = callback_data.page
        from keyboards.menu_keyboards import item_keyboard
        new_keyboard = item_keyboard(item_id, user_id, page)
        await callback.message.edit_reply_markup(reply_markup=new_keyboard)
    else:
        await callback.answer("⚠️ Блюдо не найдено в избранном")
