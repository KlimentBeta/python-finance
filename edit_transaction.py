from PyQt6.QtWidgets import (QLabel, QLineEdit,
                             QDateEdit, QTimeEdit, QMessageBox, QDialog,
                             QDialogButtonBox, QFormLayout)
from PyQt6.QtCore import QDate, QTime, QDateTime
from PyQt6.QtGui import QFont

class EditTransactionDialog(QDialog):
    """Диалог редактирования транзакции (с поддержкой категории)"""
    
    def __init__(self, transaction_data, parent=None):
        super().__init__(parent)
        self.transaction_data = transaction_data
        self.setWindowTitle("Редактирование транзакции")
        self.setFixedSize(400, 330)  # ↑ увеличил высоту на 30px
        self.initUI()
        
    def initUI(self):
        layout = QFormLayout(self)
        
        # ID транзакции (только для информации)
        self.id_label = QLabel(f"ID: {self.transaction_data['id']}")
        self.id_label.setFont(QFont('Arial', 10, QFont.Weight.Bold))
        layout.addRow("ID транзакции:", self.id_label)
        
        # Дата
        self.date_edit = QDateEdit()
        try:
            date_parts = self.transaction_data['date'].split('-')
            if len(date_parts) == 3:
                year, month, day = int(date_parts[0]), int(date_parts[1]), int(date_parts[2])
                self.date_edit.setDate(QDate(year, month, day))
        except:
            self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setMaximumDate(QDate.currentDate())
        layout.addRow("Дата:", self.date_edit)
        
        # Время
        self.time_edit = QTimeEdit()
        try:
            time_parts = self.transaction_data['time'].split(':')
            if len(time_parts) >= 2:
                hour, minute = int(time_parts[0]), int(time_parts[1])
                self.time_edit.setTime(QTime(hour, minute))
        except:
            self.time_edit.setTime(QTime.currentTime())
        layout.addRow("Время:", self.time_edit)
        
        # Доходы
        self.income_edit = QLineEdit()
        self.income_edit.setText(str(self.transaction_data['income']))
        self.income_edit.setPlaceholderText("0.00")
        layout.addRow("Доходы:", self.income_edit)
        
        # Расходы
        self.expense_edit = QLineEdit()
        self.expense_edit.setText(str(self.transaction_data['expense']))
        self.expense_edit.setPlaceholderText("0.00")
        layout.addRow("Расходы:", self.expense_edit)
        
        # 🔹 КАТЕГОРИЯ ← ДОБАВЛЕНО
        self.category_edit = QLineEdit()
        # Извлекаем категорию из данных (если нет — пустая строка)
        self.category_edit.setText(str(self.transaction_data.get('category', '') or ''))
        self.category_edit.setPlaceholderText("Например: Продукты, Зарплата...")
        layout.addRow("Категория:", self.category_edit)
        # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        
        # Кнопки
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.validate_and_accept)
        button_box.rejected.connect(self.reject)
        layout.addRow(button_box)
        
    def validate_and_accept(self):
        """Валидация данных и принятие диалога"""
        income_text = self.income_edit.text().strip()
        expense_text = self.expense_edit.text().strip()
        
        if not income_text and not expense_text:
            QMessageBox.warning(self, "Ошибка", "Заполните хотя бы одно поле: доходы или расходы")
            return
        
        try:
            income = float(income_text) if income_text else 0.0
            expense = float(expense_text) if expense_text else 0.0
            
            if income < 0 or expense < 0:
                QMessageBox.warning(self, "Ошибка", "Значения не могут быть отрицательными")
                return
                
            if income == 0 and expense == 0:
                QMessageBox.warning(self, "Ошибка", "Хотя бы одно значение должно быть больше 0")
                return
                
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Введите корректные числовые значения")
            return
        
        selected_datetime = QDateTime(self.date_edit.date(), self.time_edit.time())
        if selected_datetime > QDateTime.currentDateTime():
            QMessageBox.warning(self, "Ошибка", "Нельзя устанавливать будущую дату и время")
            return
        
        self.accept()
    
    def get_updated_data(self):
        """Возвращает обновленные данные (включая категорию)"""
        return {
            'id': self.transaction_data['id'],
            'date': self.date_edit.date().toString("yyyy-MM-dd"),
            'time': self.time_edit.time().toString("HH:mm:ss"),
            'income': float(self.income_edit.text()) if self.income_edit.text().strip() else 0.0,
            'expense': float(self.expense_edit.text()) if self.expense_edit.text().strip() else 0.0,
            'category': self.category_edit.text().strip()  # ← ДОБАВЛЕНО
        }