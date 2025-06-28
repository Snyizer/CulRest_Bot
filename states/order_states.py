"""
Состояния для FSM заказа
"""

from aiogram.fsm.state import State, StatesGroup

class OrderStates(StatesGroup):
    """Состояния процесса заказа"""
    waiting_for_confirmation = State()

class SearchStates(StatesGroup):
    """Состояния поиска"""
    waiting_for_query = State()
