import sqlite3
from datetime import datetime
import pandas as pd

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
                expense REAL DEFAULT 0.0,
                category TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Таблица 'transactions' создана или уже существует")
    
    def add_transaction(self, income: float = 0.0, expense: float = 0.0,
                       category: str = "",  # ← добавлен параметр
                       custom_date: str = None, custom_time: str = None) -> int:
        """Добавление новой транзакции"""
        if custom_date and custom_time:
            date = custom_date
            time = custom_time
        else:
            now = datetime.now()
            date = now.strftime("%Y-%m-%d")
            time = now.strftime("%H:%M:%S")
        
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO transactions (date, time, income, expense, category)
            VALUES (?, ?, ?, ?, ?)
        ''', (date, time, income, expense, category))
        
        transaction_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        print(f"✅ Транзакция добавлена с ID: {transaction_id} (категория: '{category}')")
        return transaction_id
    
    def get_transaction_by_id(self, transaction_id: int) -> dict | None:
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
                'expense': row[4],
                'category': row[5]  # ← добавлено
            }
        return None
    
    def get_all_transactions(self) -> list[dict]:
        """Получение всех транзакций"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM transactions ORDER BY date DESC, time DESC')
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': r[0],
                'date': r[1],
                'time': r[2],
                'income': r[3],
                'expense': r[4],
                'category': r[5]
            }
            for r in rows
        ]
    
    def get_transactions_by_date_range(self, start_date: str, end_date: str) -> list[dict]:
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
        
        transactions = [
            {
                'id': r[0],
                'date': r[1],
                'time': r[2],
                'income': r[3],
                'expense': r[4],
                'category': r[5]
            }
            for r in rows
        ]
        
        print(f"✅ Найдено {len(transactions)} транзакций за период с {start_date} по {end_date}")
        return transactions
    
    def get_transactions_for_export(self) -> tuple[list[dict], list[str]]:
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
                category as "Категория",
                (income - expense) as "Баланс"
            FROM transactions 
            ORDER BY date DESC, time DESC
        ''')
        
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        conn.close()
        
        transactions = []
        for row in rows:
            transaction_dict = dict(zip(columns, row))
            transactions.append(transaction_dict)
        
        return transactions, columns
    
    def update_transaction(self, transaction_id: int, income: float, expense: float,
                          category: str = "",  # ← добавлен параметр
                          date: str = None, time: str = None) -> bool:
        """Обновление транзакции"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        if date and time:
            cursor.execute('''
                UPDATE transactions 
                SET date = ?, time = ?, income = ?, expense = ?, category = ?
                WHERE id = ?
            ''', (date, time, income, expense, category, transaction_id))
        else:
            cursor.execute('''
                UPDATE transactions 
                SET income = ?, expense = ?, category = ?
                WHERE id = ?
            ''', (income, expense, category, transaction_id))
        
        updated = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        if updated:
            print(f"✅ Транзакция с ID {transaction_id} обновлена (категория: '{category}')")
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
    
    def export_to_excel(self, filename: str = None) -> tuple[str | None, str]:
        """Экспорт данных в Excel файл"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"finance_export_{timestamp}.xlsx"

        try:
            transactions, columns = self.get_transactions_for_export()

            if not transactions:
                return None, "Нет данных для экспорта"

            df = pd.DataFrame(transactions, columns=columns)

            # Итоговая строка (без категории)
            total_row = {
                'ID': '',
                'Дата': '',
                'Время': 'ИТОГО:',
                'Доход': df['Доход'].sum(),
                'Расход': df['Расход'].sum(),
                'Категория': '',  # ← добавлено
                'Баланс': df['Доход'].sum() - df['Расход'].sum()
            }

            df_export = pd.concat([df, pd.DataFrame([total_row])], ignore_index=True)
            df_export.to_excel(filename, sheet_name='Транзакции', index=False)

            return filename, f"✅ Данные успешно экспортированы в {filename}"

        except Exception as e:
            return None, f"❌ Ошибка при экспорте: {str(e)}"