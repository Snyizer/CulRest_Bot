"""
Обработчики для заказов
"""

from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from utils.callback_data import NavigationCallback, OrderCallback, ItemCallback
from utils.data_manager import data_manager
from keyboards.navigation_keyboards import back_to_main_keyboard
from config import EMOJI

router = Router()

@router.callback_query(NavigationCallback.filter(F.action == "order"))
async def show_order(callback: CallbackQuery):
    """Показать текущий заказ"""
    user_id = callback.from_user.id
    order = data_manager.get_order(user_id)
    order_items = data_manager.get_order_items_list(user_id)

    if not order_items:
        text = f"""
{EMOJI['cart']} <b>Мой заказ</b>

Ваш заказ пуст.
Добавляйте блюда через меню!
"""
        await callback.message.edit_text(
            text,
            reply_markup=back_to_main_keyboard()
        )
    else:
        text = f"{EMOJI['cart']} <b>Мой заказ</b>\n\n"

        for i, item in enumerate(order_items, 1):
            emoji = item.get("image", "🍽️")
            name = item.get("name", "Блюдо")
            quantity = item.get("quantity", 1)
            price = item.get("price", 0)
            subtotal = item.get("subtotal", 0)

            text += f"{i}. {emoji} {name}\n"
            text += f"   Количество: {quantity} × {price}₽ = {subtotal}₽\n\n"

        total = order.get("total", 0)
        text += f"💰 <b>Итого: {total}₽</b>"

        # Создаем клавиатуру для управления заказом
        builder = InlineKeyboardBuilder()

        # Кнопки для изменения количества каждого товара
        for item in order_items:
            emoji = item.get("image", "🍽️")
            name = item.get("name", "Блюдо")
            item_id = item.get("id")

            builder.button(
                text=f"➖ {emoji} {name}",
                callback_data=OrderCallback(action="remove", item_id=item_id)
            )
            builder.button(
                text=f"➕ {emoji} {name}",
                callback_data=OrderCallback(action="add", item_id=item_id)
            )

        builder.button(
            text=f"{EMOJI['confirm']} Оформить заказ",
            callback_data=OrderCallback(action="confirm")
        )
        builder.button(
            text=f"{EMOJI['delete']} Очистить заказ",
            callback_data=OrderCallback(action="clear")
        )
        builder.button(
            text=f"{EMOJI['home']} Главное меню",
            callback_data=NavigationCallback(action="main")
        )

        builder.adjust(2)

        await callback.message.edit_text(text, reply_markup=builder.as_markup())

    await callback.answer()

@router.callback_query(OrderCallback.filter(F.action == "add"))
async def add_to_order(callback: CallbackQuery, callback_data: OrderCallback):
    """Добавить товар в заказ"""
    user_id = callback.from_user.id
    item_id = callback_data.item_id

    item = data_manager.get_item(item_id)
    if not item:
        await callback.answer("❌ Блюдо не найдено")
        return

    data_manager.add_to_order(user_id, item_id)

    name = item.get("name", "Блюдо")
    await callback.answer(f"➕ {name} добавлено в заказ!")

    # Обновляем отображение заказа если мы на странице заказа
    if "Мой заказ" in callback.message.text:
        await show_order(callback)

@router.callback_query(OrderCallback.filter(F.action == "remove"))
async def remove_from_order(callback: CallbackQuery, callback_data: OrderCallback):
    """Удалить товар из заказа"""
    user_id = callback.from_user.id
    item_id = callback_data.item_id

    item = data_manager.get_item(item_id)
    if not item:
        await callback.answer("❌ Блюдо не найдено")
        return

    data_manager.remove_from_order(user_id, item_id)

    name = item.get("name", "Блюдо")
    await callback.answer(f"➖ {name} убрано из заказа")

    # Обновляем отображение заказа
    await show_order(callback)

@router.callback_query(OrderCallback.filter(F.action == "clear"))
async def clear_order(callback: CallbackQuery):
    """Очистить весь заказ"""
    user_id = callback.from_user.id
    data_manager.clear_order(user_id)

    await callback.answer("🗑️ Заказ очищен")
    await show_order(callback)

@router.callback_query(OrderCallback.filter(F.action == "confirm"))
async def confirm_order(callback: CallbackQuery):
    """Подтвердить заказ"""
    user_id = callback.from_user.id
    order = data_manager.get_order(user_id)
    order_items = data_manager.get_order_items_list(user_id)

    if not order_items:
        await callback.answer("❌ Заказ пуст")
        return

    # Формируем чек
    receipt_text = f"🧾 <b>Чек заказа</b>\n\n"
    receipt_text += f"👤 Пользователь: {callback.from_user.first_name or 'Клиент'}\n"
    receipt_text += f"🆔 ID заказа: {user_id}{len(order_items):03d}\n\n"

    for i, item in enumerate(order_items, 1):
        name = item.get("name", "Блюдо")
        quantity = item.get("quantity", 1)
        price = item.get("price", 0)
        subtotal = item.get("subtotal", 0)

        receipt_text += f"{i}. {name}\n"
        receipt_text += f"   {quantity} × {price}₽ = {subtotal}₽\n"

    total = order.get("total", 0)
    receipt_text += f"\n💰 <b>К оплате: {total}₽</b>\n\n"
    receipt_text += "✅ <b>Заказ принят!</b>\n"
    receipt_text += "⏰ Время приготовления: 15-30 минут\n"
    receipt_text += "📞 Мы свяжемся с вами для уточнения деталей"

    # Очищаем заказ после оформления
    data_manager.clear_order(user_id)

    await callback.message.edit_text(
        receipt_text,
        reply_markup=back_to_main_keyboard()
    )
    await callback.answer("✅ Заказ успешно оформлен!")

# Обработчик для просмотра отдельного блюда
@router.callback_query(ItemCallback.filter(F.action == "view"))
async def view_item(callback: CallbackQuery, callback_data: ItemCallback):
    """Показать детали блюда"""
    item_id = callback_data.item_id
    user_id = callback.from_user.id
    page = callback_data.page

    item = data_manager.get_item(item_id)
    if not item:
        await callback.answer("❌ Блюдо не найдено")
        return

    emoji = item.get("image", "🍽️")
    name = item.get("name", "Блюдо")
    description = item.get("description", "Описание отсутствует")
    price = item.get("price", 0)
    ingredients = item.get("ingredients", [])

    text = f"{emoji} <b>{name}</b>\n\n"
    text += f"📋 {description}\n\n"
    text += f"💰 Цена: <b>{price}₽</b>\n\n"

    if ingredients:
        text += f"🍽️ Состав: {', '.join(ingredients)}"

    from keyboards.menu_keyboards import item_keyboard
    keyboard = item_keyboard(item_id, user_id, page)

    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()

@router.callback_query(ItemCallback.filter(F.action == "back"))
async def back_from_item(callback: CallbackQuery, callback_data: ItemCallback):
    """Вернуться назад из просмотра блюда"""
    # Это заглушка - в реальной реализации нужно запомнить, откуда пришли
    from utils.callback_data import NavigationCallback

    back_callback = NavigationCallback(action="main")
    await callback.message.edit_text(
        "🏠 Возвращаемся в главное меню...",
        reply_markup=back_to_main_keyboard()
    )
    await callback.answer()
