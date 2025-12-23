from finance_db import FinanceDB
from datetime import datetime, timedelta

class TransactionManager:
    def __init__(self):
        self.db = FinanceDB()
        self.current_filter_type = 'all'  # 'all', 'today', 'week', 'month', 'custom'
        self.filter_start_date = None
        self.filter_end_date = None
        self.filter_category = None  # ← ДОБАВЛЕНО: фильтр по категории

    def add_transaction(self, income_text: str, expense_text: str,
                       category_text: str = "",  # ← НОВЫЙ параметр
                       custom_date: str = None, custom_time: str = None) -> dict | None:
        """
        Добавляет новую транзакцию

        Args:
            income_text: текст дохода
            expense_text: текст расхода
            category_text: категория (необязательно)
            custom_date: пользовательская дата (YYYY-MM-DD)
            custom_time: пользовательское время (HH:MM:SS)

        Returns:
            dict: добавленная транзакция или None при ошибке
        """
        # Валидация дохода/расхода
        if not income_text.strip() and not expense_text.strip():
            return None

        try:
            income = float(income_text) if income_text.strip() else 0.0
            expense = float(expense_text) if expense_text.strip() else 0.0

            if income < 0 or expense < 0:
                return None
            if income == 0 and expense == 0:
                return None

        except (ValueError, TypeError):
            return None

        # Добавляем в БД — передаём категорию!
        transaction_id = self.db.add_transaction(
            income=income,
            expense=expense,
            category=category_text.strip(),  # ← ПЕРЕДАЁМ!
            custom_date=custom_date,
            custom_time=custom_time
        )

        if not transaction_id:
            return None

        # Получаем свежую транзакцию для возврата
        added_transaction = self.db.get_transaction_by_id(transaction_id)
        return added_transaction

    def get_all_transactions(self) -> list[dict]:
        """Возвращает все транзакции из базы данных"""
        return self.db.get_all_transactions()

    def get_filtered_transactions(self) -> list[dict]:
        """Возвращает транзакции с учетом текущего фильтра (дата + категория)"""
        # Получаем по дате
        if self.current_filter_type == 'all':
            transactions = self.db.get_all_transactions()
        elif self.current_filter_type == 'today':
            today = datetime.now().strftime("%Y-%m-%d")
            transactions = self.db.get_transactions_by_date_range(today, today)
        elif self.current_filter_type == 'week':
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=6)).strftime("%Y-%m-%d")
            transactions = self.db.get_transactions_by_date_range(start_date, end_date)
        elif self.current_filter_type == 'month':
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = datetime.now().replace(day=1).strftime("%Y-%m-%d")
            transactions = self.db.get_transactions_by_date_range(start_date, end_date)
        elif self.current_filter_type == 'custom' and self.filter_start_date and self.filter_end_date:
            transactions = self.db.get_transactions_by_date_range(self.filter_start_date, self.filter_end_date)
        else:
            transactions = self.db.get_all_transactions()

        # Фильтр по категории
        if self.filter_category:
            cat = self.filter_category.strip()
            transactions = [
                t for t in transactions
                if t.get('category', '').strip().lower() == cat.lower()
            ]

        return transactions

    def set_filter(self, filter_type: str, start_date: str = None, end_date: str = None, category: str = None):
        """Устанавливает фильтр для транзакций"""
        self.current_filter_type = filter_type
        self.filter_start_date = start_date
        self.filter_end_date = end_date
        self.filter_category = category  # ← ДОБАВЛЕНО

    def get_transactions_count(self) -> int:
        """Возвращает количество отфильтрованных транзакций"""
        return len(self.get_filtered_transactions())

    def get_financial_summary(self) -> dict:
        """Возвращает финансовую сводку на основе отфильтрованных данных"""
        transactions = self.get_filtered_transactions()
        total_income = sum(t['income'] for t in transactions)
        total_expense = sum(t['expense'] for t in transactions)
        balance = total_income - total_expense
        total_transactions = len(transactions)

        avg_income = total_income / total_transactions if total_transactions > 0 else 0
        avg_expense = total_expense / total_transactions if total_transactions > 0 else 0

        # 🔹 Опционально: сводка по категориям (раскомментируй, если нужно)
        # category_summary = {}
        # for t in transactions:
        #     cat = t.get('category', '—') or '—'
        #     if cat not in category_summary:
        #         category_summary[cat] = {'income': 0.0, 'expense': 0.0, 'count': 0}
        #     category_summary[cat]['income'] += t['income']
        #     category_summary[cat]['expense'] += t['expense']
        #     category_summary[cat]['count'] += 1

        return {
            'total_income': total_income,
            'total_expense': total_expense,
            'balance': balance,
            'total_transactions': total_transactions,
            'avg_income': avg_income,
            'avg_expense': avg_expense,
            # 'by_category': category_summary  # ← можно добавить
        }

    def update_transaction(self, transaction_id: int, income: float, expense: float, category: str = "") -> bool:
        """Обновляет транзакцию в базе данных"""
        return self.db.update_transaction(
            transaction_id=transaction_id,
            income=income,
            expense=expense,
            category=category.strip()  # ← ДОБАВЛЕНО
        )

    def delete_transaction(self, transaction_id: int) -> bool:
        """Удаляет транзакцию из базы данных"""
        return self.db.delete_transaction(transaction_id)

    def delete_all_transactions(self) -> int:
        """Удаляет все транзакции, возвращает количество удалённых"""
        transactions = self.db.get_all_transactions()
        count = 0
        for t in transactions:
            if self.db.delete_transaction(t['id']):
                count += 1
        return count

    # 🔹 Уже есть, но улучшим:
    def get_unique_categories(self) -> list[str]:
        """Возвращает список уникальных категорий (непустых)"""
        transactions = self.db.get_all_transactions()
        categories = {t.get('category', '').strip() for t in transactions}
        # Убираем пустые и сортируем
        return sorted([cat for cat in categories if cat])