import sqlite3
from datetime import datetime, timedelta
import pandas as pd
import os
from openpyxl import Workbook
from openpyxl.styles import Font

class FinanceDB:
    def __init__(self, db_name: str = "finance.db"):
        self.db_name = db_name
        self.create_table()
    
    def create_table(self):
        """Создание таблицы для учета финансов"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                income REAL DEFAULT 0.0,
                expense REAL DEFAULT 0.0
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Таблица 'transactions' создана или уже существует")
    
    def add_transaction(self, income: float = 0.0, expense: float = 0.0, 
                       custom_date: str = None, custom_time: str = None) -> int:
        """Добавление новой транзакции"""
        if custom_date and custom_time:
            # Используем пользовательскую дату и время
            date = custom_date
            time = custom_time
        else:
            # Используем текущую дату и время
            current_datetime = datetime.now()
            date = current_datetime.strftime("%Y-%m-%d")
            time = current_datetime.strftime("%H:%M:%S")
        
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO transactions (date, time, income, expense)
            VALUES (?, ?, ?, ?)
        ''', (date, time, income, expense))
        
        transaction_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        print(f"✅ Транзакция добавлена с ID: {transaction_id}")
        return transaction_id
    
    def get_transaction_by_id(self, transaction_id: int) -> dict:
        """Получение транзакции по ID"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM transactions WHERE id = ?', (transaction_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'date': row[1],
                'time': row[2],
                'income': row[3],
                'expense': row[4]
            }
        return None
    
    def get_all_transactions(self) -> list:
        """Получение всех транзакций"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM transactions ORDER BY date DESC, time DESC')
        rows = cursor.fetchall()
        conn.close()
        
        transactions = []
        for row in rows:
            transactions.append({
                'id': row[0],
                'date': row[1],
                'time': row[2],
                'income': row[3],
                'expense': row[4]
            })
        
        return transactions
    
    def get_transactions_by_date_range(self, start_date: str, end_date: str) -> list:
        """Получение транзакций за указанный период"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM transactions 
            WHERE date BETWEEN ? AND ? 
            ORDER BY date DESC, time DESC
        ''', (start_date, end_date))
        
        rows = cursor.fetchall()
        conn.close()
        
        transactions = []
        for row in rows:
            transactions.append({
                'id': row[0],
                'date': row[1],
                'time': row[2],
                'income': row[3],
                'expense': row[4]
            })
        
        print(f"✅ Найдено {len(transactions)} транзакций за период с {start_date} по {end_date}")
        return transactions
    
    def get_transactions_for_export(self) -> list:
        """Получение транзакций в формате для экспорта"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                id as "ID",
                date as "Дата",
                time as "Время",
                income as "Доход",
                expense as "Расход",
                (income - expense) as "Баланс"
            FROM transactions 
            ORDER BY date DESC, time DESC
        ''')
        
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        conn.close()
        
        transactions = []
        for row in rows:
            transaction_dict = {}
            for i, column in enumerate(columns):
                transaction_dict[column] = row[i]
            transactions.append(transaction_dict)
        
        return transactions, columns
    
    def update_transaction(self, transaction_id: int, income: float, expense: float, 
                          date: str = None, time: str = None) -> bool:
        """Обновление транзакции"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        if date and time:
            # Обновляем с новой датой и временем
            cursor.execute('''
                UPDATE transactions 
                SET date = ?, time = ?, income = ?, expense = ?
                WHERE id = ?
            ''', (date, time, income, expense, transaction_id))
        else:
            # Обновляем только суммы
            cursor.execute('''
                UPDATE transactions 
                SET income = ?, expense = ?
                WHERE id = ?
            ''', (income, expense, transaction_id))
        
        updated = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        if updated:
            print(f"✅ Транзакция с ID {transaction_id} обновлена")
        else:
            print(f"❌ Транзакция с ID {transaction_id} не найдена")
        
        return updated
    
    def delete_transaction(self, transaction_id: int) -> bool:
        """Удаление транзакции"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM transactions WHERE id = ?', (transaction_id,))
        
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        if deleted:
            print(f"✅ Транзакция с ID {transaction_id} удалена")
        else:
            print(f"❌ Транзакция с ID {transaction_id} не найдена")
        
        return deleted
    
    def export_to_excel(self, filename: str = None) -> tuple:
        """Экспорт данных в Excel файл (упрощенная версия)"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"finance_export_{timestamp}.xlsx"

        try:
            # Получаем данные для экспорта
            transactions, columns = self.get_transactions_for_export()

            if not transactions:
                return None, "Нет данных для экспорта"

            # Создаем DataFrame
            df = pd.DataFrame(transactions, columns=columns)

            # Добавляем итоговую строку в DataFrame
            total_row = {
                'ID': '',
                'Дата': '',
                'Время': 'ИТОГО:',
                'Доход': df['Доход'].sum(),
                'Расход': df['Расход'].sum(),
                'Баланс': df['Доход'].sum() - df['Расход'].sum()
            }

            # Создаем копию DataFrame и добавляем итоговую строку
            df_export = df.copy()
            df_export = pd.concat([df_export, pd.DataFrame([total_row])], ignore_index=True)

            # Сохраняем в Excel
            df_export.to_excel(filename, sheet_name='Транзакции', index=False)

            return filename, f"Данные успешно экспортированы в {filename}"

        except Exception as e:
            return None, f"Ошибка при экспорте: {str(e)}"