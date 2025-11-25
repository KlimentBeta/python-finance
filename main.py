import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QMessageBox
from PyQt6.QtCore import Qt
from left_panel import LeftPanel
from center_panel import CenterPanel
from right_panel import RightPanel
from transaction_manager import TransactionManager

class FinanceApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.transaction_manager = TransactionManager()
        self.initUI()
        self.load_initial_data()
        
    def initUI(self):
        # Основные настройки окна
        self.setWindowTitle('Учет финансов (SQLite)')
        self.setFixedSize(1200, 900)
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Основной layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Создаем панели
        self.left_panel = LeftPanel()
        self.center_panel = CenterPanel()
        self.right_panel = RightPanel()
        
        # Подключаем сигналы
        self.center_panel.submit_button.clicked.connect(self.submit_data)
        self.center_panel.transactions_table.customContextMenuRequested.connect(self.handle_context_menu)
        self.center_panel.edit_selected_button.clicked.connect(self.edit_selected_transaction)
        self.center_panel.delete_selected_button.clicked.connect(self.delete_selected_transaction)
        self.center_panel.delete_all_button.clicked.connect(self.delete_all_transactions)
        self.left_panel.apply_filter_btn.clicked.connect(self.apply_filter)
        self.left_panel.reset_filter_btn.clicked.connect(self.reset_filter)
        self.right_panel.export_button.clicked.connect(self.export_to_excel)
        
        # Добавляем панели в layout
        main_layout.addWidget(self.left_panel, 1)
        main_layout.addWidget(self.center_panel, 2)
        main_layout.addWidget(self.right_panel, 1)
        
    def load_initial_data(self):
        """Загружает初始数据 из базы при запуске"""
        self.update_transactions_table()
        self.update_balance_panel()
        
    def submit_data(self):
        """Обработчик нажатия кнопки отправки данных"""
        income_text = self.center_panel.income_input.text().strip()
        expense_text = self.center_panel.expense_input.text().strip()
        
        # Проверяем, не является ли дата и время будущими
        if self.center_panel.is_future_datetime():
            QMessageBox.warning(self, 'Ошибка', 'Нельзя создавать транзакции с будущей датой и временем!')
            return
        
        # Получаем выбранные дату и время
        custom_date, custom_time = self.center_panel.get_selected_date_time()
        
        # Используем TransactionManager для добавления транзакции
        transaction = self.transaction_manager.add_transaction(
            income_text, expense_text, custom_date, custom_time
        )
        
        if transaction:
            # Обновление интерфейса
            self.update_transactions_table()
            self.update_balance_panel()
            
            # Очистка полей ввода (кроме даты и времени)
            self.center_panel.income_input.clear()
            self.center_panel.expense_input.clear()
            self.center_panel.income_input.setFocus()
        
    def handle_context_menu(self, position):
        """Обрабатывает контекстное меню таблицы"""
        menu_action = self.center_panel.transactions_table.viewport().mapToGlobal(position)
        # Обработка через отдельные методы
        pass
        
    def edit_selected_transaction(self):
        """Редактирует выбранную транзакцию"""
        updated_data = self.center_panel.edit_selected_transaction()
        if updated_data:
            success = self.transaction_manager.db.update_transaction(
                updated_data['id'],
                updated_data['income'],
                updated_data['expense'],
                updated_data['date'],
                updated_data['time']
            )
            
            if success:
                self.update_transactions_table()
                self.update_balance_panel()
                QMessageBox.information(self, 'Успех', 'Транзакция обновлена!')
            else:
                QMessageBox.warning(self, 'Ошибка', 'Не удалось обновить транзакцию')
    
    def delete_selected_transaction(self):
        """Удаляет выбранную транзакцию"""
        transaction_id = self.center_panel.delete_selected_transaction()
        if transaction_id:
            reply = self.center_panel.confirm_delete_transaction(transaction_id)
            
            if reply == QMessageBox.StandardButton.Yes:
                if self.transaction_manager.delete_transaction(transaction_id):
                    self.update_transactions_table()
                    self.update_balance_panel()
                    QMessageBox.information(self, 'Успех', 'Транзакция удалена!')
    
    def delete_all_transactions(self):
        """Удаляет все транзакции"""
        reply = self.center_panel.confirm_delete_all_transactions()
        
        if reply == QMessageBox.StandardButton.Yes:
            # Получаем все ID транзакций
            transactions = self.transaction_manager.get_all_transactions()
            deleted_count = 0
            
            for transaction in transactions:
                if self.transaction_manager.delete_transaction(transaction['id']):
                    deleted_count += 1
            
            if deleted_count > 0:
                self.update_transactions_table()
                self.update_balance_panel()
                QMessageBox.information(self, 'Успех', f'Удалено {deleted_count} транзакций!')
            else:
                QMessageBox.information(self, 'Информация', 'Нет транзакций для удаления')
        
    def update_transactions_table(self):
        """Обновление таблицы транзакций"""
        transactions = self.transaction_manager.get_filtered_transactions()
        self.center_panel.update_table(transactions)
    
    def update_balance_panel(self):
        """Обновление панели баланса"""
        summary = self.transaction_manager.get_financial_summary()
        self.right_panel.update_balance(summary)
    
    def apply_filter(self):
        """Применение фильтра по дате"""
        filter_type, start_date, end_date = self.left_panel.get_filter_params()
        self.transaction_manager.set_filter(filter_type, start_date, end_date)
        self.update_transactions_table()
        self.update_balance_panel()
    
    def reset_filter(self):
        """Сброс фильтра"""
        self.left_panel.reset_filters()
        self.transaction_manager.set_filter('all')
        self.update_transactions_table()
        self.update_balance_panel()
    
    def export_to_excel(self):
        """Экспорт данных в Excel"""
        filename, message = self.transaction_manager.db.export_to_excel()
        
        if filename:
            # Показываем сообщение об успехе
            reply = QMessageBox.information(self, 'Экспорт завершен', 
                                          f'{message}\n\nХотите открыть файл?',
                                          QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            
            if reply == QMessageBox.StandardButton.Yes:
                # Открываем файл в системе
                try:
                    if sys.platform == "win32":
                        os.startfile(filename)
                    else:
                        os.system(f'xdg-open "{filename}"')
                except Exception as e:
                    QMessageBox.warning(self, 'Ошибка', f'Не удалось открыть файл: {str(e)}')
        else:
            QMessageBox.warning(self, 'Ошибка экспорта', message)

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = FinanceApp()
    window.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()