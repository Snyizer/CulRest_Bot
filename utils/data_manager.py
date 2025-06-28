"""
Менеджер данных для работы с меню ресторана
"""

import json
import os
from typing import Dict, List, Optional, Any

class DataManager:
    """Класс для управления данными меню"""

    def __init__(self, data_file: str = "data/menu.json"):
        self.data_file = data_file
        self.menu_data = self._load_menu()

        # Данные пользователей (в продакшене использовать БД)
        self.user_favorites = {}  # {user_id: [item_ids]}
        self.user_orders = {}     # {user_id: {items: {item_id: quantity}, total: int}}

    def _load_menu(self) -> Dict:
        """Загрузка данных меню из JSON файла"""
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {"cuisines": {}}

    def get_cuisines(self) -> Dict[str, Dict]:
        """Получить список кухонь"""
        return self.menu_data.get("cuisines", {})

    def get_categories(self, cuisine_id: str) -> Dict[str, Dict]:
        """Получить категории для указанной кухни"""
        cuisine = self.menu_data.get("cuisines", {}).get(cuisine_id, {})
        return cuisine.get("categories", {})

    def get_items(self, cuisine_id: str, category_id: str) -> List[Dict]:
        """Получить блюда в категории"""
        categories = self.get_categories(cuisine_id)
        category = categories.get(category_id, {})
        return category.get("items", [])

    def get_item(self, item_id: str) -> Optional[Dict]:
        """Найти блюдо по ID"""
        for cuisine in self.menu_data.get("cuisines", {}).values():
            for category in cuisine.get("categories", {}).values():
                for item in category.get("items", []):
                    if item.get("id") == item_id:
                        return item
        return None

    def search_items(self, query: str) -> List[Dict]:
        """Поиск блюд по названию"""
        results = []
        query_lower = query.lower()

        for cuisine in self.menu_data.get("cuisines", {}).values():
            for category in cuisine.get("categories", {}).values():
                for item in category.get("items", []):
                    item_name = item.get("name", "").lower()
                    if query_lower in item_name:
                        results.append(item)

        return results

    # Управление избранным
    def add_to_favorites(self, user_id: int, item_id: str) -> bool:
        """Добавить в избранное"""
        if user_id not in self.user_favorites:
            self.user_favorites[user_id] = []

        if item_id not in self.user_favorites[user_id]:
            self.user_favorites[user_id].append(item_id)
            return True
        return False

    def remove_from_favorites(self, user_id: int, item_id: str) -> bool:
        """Удалить из избранного"""
        if user_id in self.user_favorites:
            if item_id in self.user_favorites[user_id]:
                self.user_favorites[user_id].remove(item_id)
                return True
        return False

    def get_user_favorites(self, user_id: int) -> List[Dict]:
        """Получить избранные блюда пользователя"""
        favorite_ids = self.user_favorites.get(user_id, [])
        favorites = []

        for item_id in favorite_ids:
            item = self.get_item(item_id)
            if item:
                favorites.append(item)

        return favorites

    def is_in_favorites(self, user_id: int, item_id: str) -> bool:
        """Проверить, в избранном ли блюдо"""
        return item_id in self.user_favorites.get(user_id, [])

    # Управление заказом
    def create_order(self, user_id: int):
        """Создать новый заказ"""
        self.user_orders[user_id] = {"items": {}, "total": 0}

    def add_to_order(self, user_id: int, item_id: str, quantity: int = 1):
        """Добавить товар в заказ"""
        if user_id not in self.user_orders:
            self.create_order(user_id)

        if item_id in self.user_orders[user_id]["items"]:
            self.user_orders[user_id]["items"][item_id] += quantity
        else:
            self.user_orders[user_id]["items"][item_id] = quantity

        self._recalculate_total(user_id)

    def remove_from_order(self, user_id: int, item_id: str, quantity: int = 1):
        """Удалить товар из заказа"""
        if user_id not in self.user_orders:
            return

        if item_id in self.user_orders[user_id]["items"]:
            self.user_orders[user_id]["items"][item_id] -= quantity
            if self.user_orders[user_id]["items"][item_id] <= 0:
                del self.user_orders[user_id]["items"][item_id]

        self._recalculate_total(user_id)

    def get_order(self, user_id: int) -> Dict:
        """Получить текущий заказ"""
        return self.user_orders.get(user_id, {"items": {}, "total": 0})

    def clear_order(self, user_id: int):
        """Очистить заказ"""
        self.user_orders[user_id] = {"items": {}, "total": 0}

    def _recalculate_total(self, user_id: int):
        """Пересчитать общую стоимость заказа"""
        order = self.user_orders.get(user_id, {"items": {}, "total": 0})
        total = 0

        for item_id, quantity in order["items"].items():
            item = self.get_item(item_id)
            if item:
                total += item.get("price", 0) * quantity

        self.user_orders[user_id]["total"] = total

    def get_order_items_list(self, user_id: int) -> List[Dict]:
        """Получить список товаров в заказе с деталями"""
        order = self.get_order(user_id)
        items_list = []

        for item_id, quantity in order["items"].items():
            item = self.get_item(item_id)
            if item:
                item_copy = item.copy()
                item_copy["quantity"] = quantity
                item_copy["subtotal"] = item["price"] * quantity
                items_list.append(item_copy)

        return items_list

# Глобальный экземпляр менеджера данных
data_manager = DataManager()
