import sys, os
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
        self.setWindowTitle('Учет финансов')
        self.setFixedSize(1200, 900)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)

        self.left_panel = LeftPanel()
        self.center_panel = CenterPanel()
        self.right_panel = RightPanel()

        # Подключение сигналов
        self.center_panel.submit_button.clicked.connect(self.submit_data)
        self.center_panel.edit_selected_button.clicked.connect(self.edit_selected_transaction)
        self.center_panel.delete_selected_button.clicked.connect(self.delete_selected_transaction)
        self.center_panel.delete_all_button.clicked.connect(self.delete_all_transactions)
        self.left_panel.apply_filter_btn.clicked.connect(self.apply_filter)
        self.left_panel.reset_filter_btn.clicked.connect(self.reset_filter)
        self.right_panel.export_button.clicked.connect(self.export_to_excel)

        main_layout.addWidget(self.left_panel, 1)
        main_layout.addWidget(self.center_panel, 2)
        main_layout.addWidget(self.right_panel, 1)

    def load_initial_data(self):
        self.update_category_filter_options()  # ← загружаем категории в фильтр
        self.update_transactions_table()
        self.update_balance_panel()

    def update_category_filter_options(self):
        """Обновляет выпадающий список категорий в фильтре (если используется QComboBox)"""
        try:
            # Получаем уникальные категории
            categories = self.transaction_manager.get_unique_categories()
            self.left_panel.update_category_filter_options(categories)  # ← метод должен быть реализован в LeftPanel
        except Exception as e:
            print(f"⚠️ Не удалось обновить фильтр категорий: {e}")

    def submit_data(self):
        income_text = self.center_panel.income_input.text().strip()
        expense_text = self.center_panel.expense_input.text().strip()
        category_text = self.center_panel.category_input.text().strip()  # ← новое поле

        if self.center_panel.is_future_datetime():
            QMessageBox.warning(self, 'Ошибка', 'Нельзя создавать транзакции с будущей датой и временем!')
            return

        custom_date, custom_time = self.center_panel.get_selected_date_time()

        transaction = self.transaction_manager.add_transaction(
    income_text, expense_text, category_text, custom_date, custom_time 
)

        if transaction:
            self.update_transactions_table()
            self.update_balance_panel()
            self.update_category_filter_options()  # ← обновляем фильтр после добавления новой категории

            # Очистка полей — включая категорию
            self.center_panel.income_input.clear()
            self.center_panel.expense_input.clear()
            self.center_panel.category_input.clear()
            self.center_panel.income_input.setFocus()

    def edit_selected_transaction(self):
        # Получаем данные из интерфейса (например, через диалог или редактирование в таблице)
        # Предполагается, что center_panel.edit_selected_transaction() возвращает словарь с 'category'
        updated_data = self.center_panel.edit_selected_transaction()
        if updated_data:
            success = self.transaction_manager.db.update_transaction(
                updated_data['id'],
                updated_data['income'],
                updated_data['expense'],
                updated_data.get('category', ''),  # ← новое поле
                updated_data['date'],
                updated_data['time']
            )
            if success:
                self.update_transactions_table()
                self.update_balance_panel()
                self.update_category_filter_options()
                QMessageBox.information(self, 'Успех', 'Транзакция обновлена!')
            else:
                QMessageBox.warning(self, 'Ошибка', 'Не удалось обновить транзакцию')

    def delete_selected_transaction(self):
        transaction_id = self.center_panel.delete_selected_transaction()
        if transaction_id:
            reply = self.center_panel.confirm_delete_transaction(transaction_id)
            if reply == QMessageBox.StandardButton.Yes:
                if self.transaction_manager.delete_transaction(transaction_id):
                    self.update_transactions_table()
                    self.update_balance_panel()
                    self.update_category_filter_options()  # ← категории могли измениться
                    QMessageBox.information(self, 'Успех', 'Транзакция удалена!')

    def delete_all_transactions(self):
        reply = self.center_panel.confirm_delete_all_transactions()
        if reply == QMessageBox.StandardButton.Yes:
            deleted_count = self.transaction_manager.delete_all_transactions()
            if deleted_count > 0:
                self.update_transactions_table()
                self.update_balance_panel()
                self.update_category_filter_options()
                QMessageBox.information(self, 'Успех', f'Удалено {deleted_count} транзакций!')
            else:
                QMessageBox.information(self, 'Информация', 'Нет транзакций для удаления')

    def apply_filter(self):
        filter_type, start_date, end_date = self.left_panel.get_filter_params()
        category_filter = self.left_panel.get_selected_category()  # ← например, строка или None
        self.transaction_manager.set_filter(
            filter_type=filter_type,
            start_date=start_date,
            end_date=end_date,
            category=category_filter  # ← передаём в менеджер
        )
        self.update_transactions_table()
        self.update_balance_panel()

    def reset_filter(self):
        self.left_panel.reset_filters()
        self.transaction_manager.set_filter('all')
        self.update_transactions_table()
        self.update_balance_panel()

    def export_to_excel(self):
        filename, message = self.transaction_manager.db.export_to_excel()

        if filename:
            reply = QMessageBox.information(
                self,
                'Экспорт завершен',
                f'{message}\n\nХотите открыть файл?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    if sys.platform == "win32":
                        os.startfile(filename)
                    else:
                        os.system(f'xdg-open "{filename}"')
                except Exception as e:
                    QMessageBox.warning(self, 'Ошибка', f'Не удалось открыть файл: {str(e)}')
        else:
            QMessageBox.warning(self, 'Ошибка экспорта', message)

    def update_transactions_table(self):
        transactions = self.transaction_manager.get_filtered_transactions()
        self.center_panel.update_table(transactions)

    def update_balance_panel(self):
        summary = self.transaction_manager.get_financial_summary()
        self.right_panel.update_balance(summary)


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    window = FinanceApp()
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()