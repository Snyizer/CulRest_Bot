"""
Обработчики для поиска блюд
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from utils.callback_data import NavigationCallback, ItemCallback
from utils.data_manager import data_manager
from keyboards.navigation_keyboards import back_to_main_keyboard
from keyboards.menu_keyboards import item_keyboard
from states.order_states import SearchStates
from config import EMOJI

router = Router()

@router.callback_query(NavigationCallback.filter(F.action == "search"))
async def start_search(callback: CallbackQuery, state: FSMContext):
    """Начать поиск блюд"""
    await state.set_state(SearchStates.waiting_for_query)

    text = f"""
{EMOJI['search']} <b>Поиск блюд</b>

Введите название блюда или его часть:
"""

    await callback.message.edit_text(
        text,
        reply_markup=back_to_main_keyboard()
    )
    await callback.answer()

@router.message(SearchStates.waiting_for_query)
async def process_search_query(message: Message, state: FSMContext):
    """Обработать поисковый запрос"""
    query = message.text.strip()

    if len(query) < 2:
        await message.answer("❌ Поисковый запрос должен содержать минимум 2 символа")
        return

    results = data_manager.search_items(query)

    if not results:
        text = f"😔 По запросу <b>'{query}'</b> ничего не найдено\n\nПопробуйте другой запрос:"
        await message.answer(text)
        return

    await state.clear()

    text = f"{EMOJI['search']} <b>Результаты поиска по '{query}':</b>\n\n"

    for i, item in enumerate(results[:10], 1):  # Показываем максимум 10 результатов
        emoji = item.get("image", "🍽️")
        name = item.get("name", "Блюдо")
        price = item.get("price", 0)
        text += f"{i}. {emoji} {name} - {price}₽\n"

    if len(results) > 10:
        text += f"\n... и еще {len(results) - 10} блюд"

    keyboard = back_to_main_keyboard()

    # Добавляем кнопки для первых 5 результатов
    if results:
        from aiogram.utils.keyboard import InlineKeyboardBuilder
        builder = InlineKeyboardBuilder()

        for item in results[:5]:
            emoji = item.get("image", "🍽️")
            name = item.get("name", "Блюдо")

            builder.button(
                text=f"{emoji} {name}",
                callback_data=ItemCallback(action="view", item_id=item["id"])
            )

        builder.button(
            text=f"{EMOJI['home']} Главное меню",
            callback_data=NavigationCallback(action="main")
        )

        builder.adjust(1)
        keyboard = builder.as_markup()

    await message.answer(text, reply_markup=keyboard)
