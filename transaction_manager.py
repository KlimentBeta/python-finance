from finance_db import FinanceDB
from PyQt6.QtCore import QDateTime
from datetime import datetime, timedelta

class TransactionManager:
    def __init__(self):
        self.db = FinanceDB()
        self.current_filter_type = 'all'  # 'all', 'today', 'week', 'month', 'custom'
        self.filter_start_date = None
        self.filter_end_date = None
    
    def add_transaction(self, income_text: str, expense_text: str, 
                       custom_date: str = None, custom_time: str = None) -> dict:
        """
        Добавляет новую транзакцию
        
        Args:
            income_text: текст дохода
            expense_text: текст расхода
            custom_date: пользовательская дата (YYYY-MM-DD)
            custom_time: пользовательское время (HH:MM:SS)
            
        Returns:
            dict: добавленная транзакция или None при ошибке
        """
        # Проверка введенных данных
        if not income_text and not expense_text:
            return None
        
        # Валидация числовых данных
        try:
            income = float(income_text) if income_text else 0.0
            expense = float(expense_text) if expense_text else 0.0
            
            if income < 0 or expense < 0:
                raise ValueError("Отрицательные значения не допускаются")
                
        except ValueError:
            return None
        
        # Добавляем транзакцию в базу данных
        transaction_id = self.db.add_transaction(income, expense, custom_date, custom_time)
        
        # Получаем добавленную транзакцию для отображения
        transactions = self.get_filtered_transactions()
        added_transaction = next((t for t in transactions if t['id'] == transaction_id), None)
        
        return added_transaction
    
    def get_all_transactions(self) -> list:
        """Возвращает все транзакции из базы данных"""
        return self.db.get_all_transactions()
    
    def get_filtered_transactions(self) -> list:
        """Возвращает транзакции с учетом текущего фильтра"""
        if self.current_filter_type == 'all':
            return self.db.get_all_transactions()
        elif self.current_filter_type == 'today':
            today = datetime.now().strftime("%Y-%m-%d")
            return self.db.get_transactions_by_date_range(today, today)
        elif self.current_filter_type == 'week':
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=6)).strftime("%Y-%m-%d")
            return self.db.get_transactions_by_date_range(start_date, end_date)
        elif self.current_filter_type == 'month':
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = datetime.now().replace(day=1).strftime("%Y-%m-%d")
            return self.db.get_transactions_by_date_range(start_date, end_date)
        elif self.current_filter_type == 'custom' and self.filter_start_date and self.filter_end_date:
            return self.db.get_transactions_by_date_range(self.filter_start_date, self.filter_end_date)
        else:
            return self.db.get_all_transactions()
    
    def set_filter(self, filter_type: str, start_date: str = None, end_date: str = None):
        """Устанавливает фильтр для транзакций"""
        self.current_filter_type = filter_type
        self.filter_start_date = start_date
        self.filter_end_date = end_date
    
    def get_transactions_count(self) -> int:
        """Возвращает количество транзакций"""
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
        
        return {
            'total_income': total_income,
            'total_expense': total_expense,
            'balance': balance,
            'total_transactions': total_transactions,
            'avg_income': avg_income,
            'avg_expense': avg_expense
        }
    
    def update_transaction(self, transaction_id: int, income: float, expense: float) -> bool:
        """Обновляет транзакцию в базе данных"""
        return self.db.update_transaction(transaction_id, income, expense)
    
    def delete_transaction(self, transaction_id: int) -> bool:
        """Удаляет транзакцию из базы данных"""
        return self.db.delete_transaction(transaction_id)
    
    def clear_all_transactions(self):
        """Очищает все транзакции (для тестирования)"""
        transactions = self.db.get_all_transactions()
        for transaction in transactions:
            self.db.delete_transaction(transaction['id'])


    