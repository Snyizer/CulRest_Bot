"""
Обработчики для меню ресторана
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from utils.callback_data import MenuCallback, NavigationCallback
from utils.data_manager import data_manager
from keyboards.navigation_keyboards import main_menu_keyboard
from keyboards.menu_keyboards import (
    cuisines_keyboard, 
    categories_keyboard, 
    all_categories_keyboard,
    items_keyboard
)
from config import EMOJI

router = Router()

@router.message(Command("start"))
async def start_command(message: Message, state: FSMContext):
    """Обработчик команды /start"""
    await state.clear()

    user_name = message.from_user.first_name or "Друг"

    welcome_text = f"""🔥 <b>Добро пожаловать в ресторан Simmer!</b> 🔥

Готовьтесь к незабываемому гастрономическому путешествию! В нашем ресторане вас ждут:

🍽️ Разнообразное меню - итальянская, азиатская и русская кухни
🔍 Удобный поиск блюд по названию  
⭐ Избранные блюда - сохраняйте понравившиеся позиции
🛒 Простое оформление заказов с расчетом стоимости

Выберите нужный раздел из меню ниже, чтобы начать! 👇"""

    await message.answer(
        welcome_text,
        reply_markup=main_menu_keyboard()
    )

@router.callback_query(NavigationCallback.filter(F.action == "main"))
async def show_main_menu(callback: CallbackQuery, state: FSMContext):
    """Показать главное меню"""
    await state.clear()

    welcome_text = f"""
🍽️ <b>Главное меню</b>

Выберите действие:
"""

    await callback.message.edit_text(
        welcome_text,
        reply_markup=main_menu_keyboard()
    )
    await callback.answer()

@router.callback_query(MenuCallback.filter(F.action == "cuisines"))
async def show_cuisines(callback: CallbackQuery):
    """Показать список кухонь"""
    text = f"{EMOJI['menu']} <b>Выберите кухню:</b>"

    await callback.message.edit_text(
        text,
        reply_markup=cuisines_keyboard()
    )
    await callback.answer()

@router.callback_query(MenuCallback.filter(F.action == "categories"))
async def show_categories(callback: CallbackQuery, callback_data: MenuCallback):
    """Показать категории для выбранной кухни"""
    cuisine_id = callback_data.cuisine_id
    cuisines = data_manager.get_cuisines()
    cuisine_name = cuisines.get(cuisine_id, {}).get("name", "Кухня")

    text = f"🍽️ <b>{cuisine_name}</b>\n\nВыберите категорию:"

    await callback.message.edit_text(
        text,
        reply_markup=categories_keyboard(cuisine_id)
    )
    await callback.answer()

@router.callback_query(MenuCallback.filter(F.action == "all_categories"))
async def show_all_categories(callback: CallbackQuery):
    """Показать все категории всех кухонь"""
    text = "🌍 <b>Все категории</b>\n\nВыберите категорию:"

    await callback.message.edit_text(
        text,
        reply_markup=all_categories_keyboard()
    )
    await callback.answer()

@router.callback_query(MenuCallback.filter(F.action == "items"))
async def show_items(callback: CallbackQuery, callback_data: MenuCallback):
    """Показать блюда в категории"""
    cuisine_id = callback_data.cuisine_id
    category_id = callback_data.category_id
    page = callback_data.page

    cuisines = data_manager.get_cuisines()
    cuisine_name = cuisines.get(cuisine_id, {}).get("name", "Кухня")
    categories = data_manager.get_categories(cuisine_id)
    category_name = categories.get(category_id, {}).get("name", "Категория")

    items = data_manager.get_items(cuisine_id, category_id)

    if not items:
        text = f"😔 В категории <b>{category_name}</b> пока нет блюд"
    else:
        text = f"🍽️ <b>{cuisine_name} → {category_name}</b>\n\nВыберите блюдо:"

    await callback.message.edit_text(
        text,
        reply_markup=items_keyboard(cuisine_id, category_id, page)
    )
    await callback.answer()

# Игнорирование пустых callback
@router.callback_query(F.data == "ignore")
async def ignore_callback(callback: CallbackQuery):
    """Игнорировать callback"""
    await callback.answer()
