from PyQt6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
                             QMenu, QDateEdit, QTimeEdit, QMessageBox, QDialog, 
                             QDialogButtonBox, QFormLayout)
from PyQt6.QtCore import Qt, QDate, QTime, QDateTime
from PyQt6.QtGui import QFont, QAction, QColor, QDoubleValidator

class EditTransactionDialog(QDialog):
    """Диалог редактирования транзакции"""
    
    def __init__(self, transaction_data, parent=None):
        super().__init__(parent)
        self.transaction_data = transaction_data
        self.setWindowTitle("Редактирование транзакции")
        self.setFixedSize(400, 300)
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
            # Парсим дату из формата YYYY-MM-DD
            date_parts = self.transaction_data['date'].split('-')
            if len(date_parts) == 3:
                year, month, day = int(date_parts[0]), int(date_parts[1]), int(date_parts[2])
                self.date_edit.setDate(QDate(year, month, day))
        except:
            self.date_edit.setDate(QDate.currentDate())
        
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setMaximumDate(QDate.currentDate())  # Запрещаем будущие даты
        layout.addRow("Дата:", self.date_edit)
        
        # Время
        self.time_edit = QTimeEdit()
        try:
            # Парсим время из формата HH:MM:SS
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
        # self.income_edit.setValidator(QDoubleValidator(0, 9999999.99, 2))
        self.income_edit.setPlaceholderText("0.00")
        layout.addRow("Доходы:", self.income_edit)
        
        # Расходы
        self.expense_edit = QLineEdit()
        self.expense_edit.setText(str(self.transaction_data['expense']))
        # self.expense_edit.setValidator(QDoubleValidator(0, 9999999.99, 2))
        self.expense_edit.setPlaceholderText("0.00")
        layout.addRow("Расходы:", self.expense_edit)
        
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
        
        # Проверка на пустые поля
        if not income_text and not expense_text:
            QMessageBox.warning(self, "Ошибка", "Заполните хотя бы одно поле: доходы или расходы")
            return
        
        # Валидация числовых данных
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
        
        # Проверка даты и времени
        selected_date = self.date_edit.date()
        selected_time = self.time_edit.time()
        current_datetime = QDateTime.currentDateTime()
        selected_datetime = QDateTime(selected_date, selected_time)
        
        if selected_datetime > current_datetime:
            QMessageBox.warning(self, "Ошибка", "Нельзя устанавливать будущую дату и время")
            return
        
        self.accept()
    
    def get_updated_data(self):
        """Возвращает обновленные данные"""
        return {
            'id': self.transaction_data['id'],
            'date': self.date_edit.date().toString("yyyy-MM-dd"),
            'time': self.time_edit.time().toString("HH:mm:ss"),
            'income': float(self.income_edit.text()) if self.income_edit.text().strip() else 0.0,
            'expense': float(self.expense_edit.text()) if self.expense_edit.text().strip() else 0.0
        }

class CenterPanel(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout(self)
        
        # Заголовок
        title_label = QLabel('Учет доходов и расходов')
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont('Arial', 16, QFont.Weight.Bold))
        layout.addWidget(title_label)
        
        layout.addSpacing(15)
        
        # Панель ввода данных
        input_frame = QFrame()
        input_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        input_frame.setStyleSheet("""
            QFrame {
                background-color: #f0f0f0;
                border: 2px solid #cccccc;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        
        input_layout = QVBoxLayout(input_frame)
        input_layout.setSpacing(10)
        
        # Верхняя строка - дата и время
        datetime_layout = QHBoxLayout()
        
        # Дата
        date_layout = QVBoxLayout()
        date_label = QLabel('Дата:')
        date_label.setFont(QFont('Arial', 10, QFont.Weight.Bold))
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        self.date_input.setMaximumDate(QDate.currentDate())  # Запрещаем будущие даты
        self.date_input.setStyleSheet("""
            QDateEdit {
                padding: 6px;
                font-size: 11px;
                border: 1px solid #ced4da;
                border-radius: 4px;
                background-color: white;
            }
        """)
        date_layout.addWidget(date_label)
        date_layout.addWidget(self.date_input)
        
        # Время
        time_layout = QVBoxLayout()
        time_label = QLabel('Время:')
        time_label.setFont(QFont('Arial', 10, QFont.Weight.Bold))
        self.time_input = QTimeEdit()
        self.time_input.setTime(QTime.currentTime())
        self.time_input.setStyleSheet("""
            QTimeEdit {
                padding: 6px;
                font-size: 11px;
                border: 1px solid #ced4da;
                border-radius: 4px;
                background-color: white;
            }
        """)
        time_layout.addWidget(time_label)
        time_layout.addWidget(self.time_input)
        
        datetime_layout.addLayout(date_layout)
        datetime_layout.addLayout(time_layout)
        datetime_layout.addStretch()
        
        input_layout.addLayout(datetime_layout)
        
        # Нижняя строка - доходы, расходы и кнопка
        amounts_layout = QHBoxLayout()
        
        # Поле для доходов
        income_layout = QVBoxLayout()
        income_label = QLabel('Доходы:')
        income_label.setFont(QFont('Arial', 10, QFont.Weight.Bold))
        self.income_input = QLineEdit()
        self.income_input.setPlaceholderText('Введите сумму доходов...')
        self.income_input.setValidator(QDoubleValidator(0, 9999999.99, 2))
        self.income_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                font-size: 12px;
                border: 2px solid #4CAF50;
                border-radius: 4px;
                background-color: white;
            }
        """)
        income_layout.addWidget(income_label)
        income_layout.addWidget(self.income_input)
        
        # Поле для расходов
        expense_layout = QVBoxLayout()
        expense_label = QLabel('Расходы:')
        expense_label.setFont(QFont('Arial', 10, QFont.Weight.Bold))
        self.expense_input = QLineEdit()
        self.expense_input.setPlaceholderText('Введите сумму расходов...')
        self.expense_input.setValidator(QDoubleValidator(0, 9999999.99, 2))
        self.expense_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                font-size: 12px;
                border: 2px solid #f44336;
                border-radius: 4px;
                background-color: white;
            }
        """)
        expense_layout.addWidget(expense_label)
        expense_layout.addWidget(self.expense_input)
        
        # Кнопка отправки
        self.submit_button = QPushButton('Добавить')
        self.submit_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 12px 20px;
                font-size: 12px;
                font-weight: bold;
                border-radius: 4px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        
        amounts_layout.addLayout(income_layout)
        amounts_layout.addLayout(expense_layout)
        amounts_layout.addWidget(self.submit_button)
        
        input_layout.addLayout(amounts_layout)
        
        layout.addWidget(input_frame)
        
        layout.addSpacing(15)
        
        # Панель управления таблицей
        table_controls_layout = QHBoxLayout()
        
        # Заголовок таблицы
        table_label = QLabel('История транзакций')
        table_label.setFont(QFont('Arial', 12, QFont.Weight.Bold))
        table_controls_layout.addWidget(table_label)
        
        table_controls_layout.addStretch()
        
        # Кнопка редактирования выбранной записи
        self.edit_selected_button = QPushButton('✏️ Редактировать')
        self.edit_selected_button.setStyleSheet("""
            QPushButton {
                background-color: #ffc107;
                color: #212529;
                border: none;
                padding: 8px 12px;
                font-size: 11px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #e0a800;
            }
            QPushButton:disabled {
                background-color: #6c757d;
                color: #adb5bd;
            }
        """)
        self.edit_selected_button.setEnabled(False)
        table_controls_layout.addWidget(self.edit_selected_button)
        
        # Кнопка удаления выбранной записи
        self.delete_selected_button = QPushButton('🗑️ Удалить')
        self.delete_selected_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 8px 12px;
                font-size: 11px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:disabled {
                background-color: #6c757d;
                color: #adb5bd;
            }
        """)
        self.delete_selected_button.setEnabled(False)
        table_controls_layout.addWidget(self.delete_selected_button)
        
        layout.addLayout(table_controls_layout)
        
        # Таблица транзакций
        self.transactions_table = QTableWidget()
        self.transactions_table.setColumnCount(5)  # Добавляем столбец для ID
        self.transactions_table.setHorizontalHeaderLabels(['ID', 'Дата', 'Время', 'Доходы', 'Расходы'])
        
        # Настройка таблицы
        header = self.transactions_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Дата
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Время
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Доходы
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Расходы
        
        self.transactions_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
                gridline-color: #ddd;
                font-size: 11px;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 6px;
                border: 1px solid #ddd;
                font-weight: bold;
                font-size: 11px;
            }
            QTableWidget::item:selected {
                background-color: #007bff;
                color: white;
            }
        """)
        
        # Включаем контекстное меню для таблицы
        self.transactions_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.transactions_table.customContextMenuRequested.connect(self.show_context_menu)
        
        # Подключаем сигнал выбора строки
        self.transactions_table.itemSelectionChanged.connect(self.on_selection_changed)
        
        # Подключаем двойной клик для быстрого редактирования
        self.transactions_table.doubleClicked.connect(self.on_double_click)
        
        layout.addWidget(self.transactions_table)
        
        # Панель массового удаления
        bulk_delete_layout = QHBoxLayout()
        
        # Кнопка удаления всех записей
        self.delete_all_button = QPushButton('⚠️ Удалить все записи')
        self.delete_all_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 10px 15px;
                font-size: 11px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:disabled {
                background-color: #6c757d;
                color: #adb5bd;
            }
        """)
        self.delete_all_button.setEnabled(False)
        bulk_delete_layout.addWidget(self.delete_all_button)
        
        bulk_delete_layout.addStretch()
        
        # Информация о количестве записей
        self.records_count_label = QLabel('Записей: 0')
        self.records_count_label.setFont(QFont('Arial', 10))
        self.records_count_label.setStyleSheet("color: #6c757d;")
        bulk_delete_layout.addWidget(self.records_count_label)
        
        layout.addLayout(bulk_delete_layout)
    
    def update_table(self, transactions):
        """Обновление таблицы транзакций"""
        self.transactions_table.setRowCount(len(transactions))
        
        for row, transaction in enumerate(transactions):
            # ID
            self.transactions_table.setItem(row, 0, QTableWidgetItem(str(transaction['id'])))
            # Дата (форматируем для отображения)
            display_date = self.format_date_for_display(transaction['date'])
            self.transactions_table.setItem(row, 1, QTableWidgetItem(display_date))
            # Время
            self.transactions_table.setItem(row, 2, QTableWidgetItem(transaction['time']))
            # Доходы
            income_item = QTableWidgetItem(f"{transaction['income']:.2f} руб.")
            self.transactions_table.setItem(row, 3, income_item)
            # Расходы
            expense_item = QTableWidgetItem(f"{transaction['expense']:.2f} руб.")
            self.transactions_table.setItem(row, 4, expense_item)
            
            # Подсветка строк в зависимости от типа операции
            if transaction['income'] > 0:
                income_item.setBackground(QColor(144, 238, 144))  # lightGreen
            if transaction['expense'] > 0:
                expense_item.setBackground(QColor(240, 128, 128))  # lightCoral
        
        # Обновляем счетчик записей
        self.records_count_label.setText(f'Записей: {len(transactions)}')
        self.delete_all_button.setEnabled(len(transactions) > 0)
    
    def format_date_for_display(self, db_date):
        """Форматирует дату из БД для отображения"""
        try:
            # Если дата в формате YYYY-MM-DD, преобразуем в DD.MM.YYYY
            if '-' in db_date:
                parts = db_date.split('-')
                if len(parts) == 3:
                    return f"{parts[2]}.{parts[1]}.{parts[0]}"
        except:
            pass
        return db_date
    
    def get_selected_date_time(self):
        """Возвращает выбранные дату и время в формате для БД"""
        date = self.date_input.date().toString("yyyy-MM-dd")
        time = self.time_input.time().toString("HH:mm:ss")
        return date, time
    
    def is_future_datetime(self):
        """Проверяет, является ли выбранные дата и время будущими"""
        selected_date = self.date_input.date()
        selected_time = self.time_input.time()
        current_datetime = QDateTime.currentDateTime()
        
        # Создаем QDateTime из выбранных даты и времени
        selected_datetime = QDateTime(selected_date, selected_time)
        
        # Сравниваем с текущим моментом
        return selected_datetime > current_datetime
    
    def show_context_menu(self, position):
        """Показывает контекстное меню для таблицы"""
        if not self.get_selected_transaction_id():
            return
            
        menu = QMenu()
        
        edit_action = QAction("✏️ Редактировать транзакцию", self)
        edit_action.triggered.connect(self.edit_selected_transaction)
        menu.addAction(edit_action)
        
        delete_action = QAction("🗑️ Удалить транзакцию", self)
        delete_action.triggered.connect(self.delete_selected_transaction)
        menu.addAction(delete_action)
        
        menu.addSeparator()
        
        # Добавляем информацию о выбранной записи
        transaction_id = self.get_selected_transaction_id()
        info_action = QAction(f"ID: {transaction_id}", self)
        info_action.setEnabled(False)
        menu.addAction(info_action)
        
        menu.exec(self.transactions_table.viewport().mapToGlobal(position))
    
    def on_selection_changed(self):
        """Обработчик изменения выбора в таблице"""
        has_selection = self.get_selected_transaction_id() is not None
        self.edit_selected_button.setEnabled(has_selection)
        self.delete_selected_button.setEnabled(has_selection)
    
    def on_double_click(self, index):
        """Обработчик двойного клика по таблице - открываем редактирование"""
        if index.isValid():
            self.edit_selected_transaction()
    
    def get_selected_transaction_id(self):
        """Возвращает ID выбранной транзакции"""
        current_row = self.transactions_table.currentRow()
        if current_row >= 0:
            item = self.transactions_table.item(current_row, 0)
            if item:
                return int(item.text())
        return None
    
    def get_selected_transaction_info(self):
        """Возвращает информацию о выбранной транзакции"""
        current_row = self.transactions_table.currentRow()
        if current_row >= 0:
            id_item = self.transactions_table.item(current_row, 0)
            date_item = self.transactions_table.item(current_row, 1)
            time_item = self.transactions_table.item(current_row, 2)
            income_item = self.transactions_table.item(current_row, 3)
            expense_item = self.transactions_table.item(current_row, 4)
            
            if all([id_item, date_item, time_item, income_item, expense_item]):
                return {
                    'id': id_item.text(),
                    'date': self.parse_display_date(date_item.text()),  # Конвертируем обратно в YYYY-MM-DD
                    'time': time_item.text(),
                    'income': float(income_item.text().replace(' руб.', '').strip()),
                    'expense': float(expense_item.text().replace(' руб.', '').strip())
                }
        return None
    
    def parse_display_date(self, display_date):
        """Парсит дату из формата отображения в формат БД"""
        try:
            # Если дата в формате DD.MM.YYYY, преобразуем в YYYY-MM-DD
            if '.' in display_date:
                parts = display_date.split('.')
                if len(parts) == 3:
                    return f"{parts[2]}-{parts[1]}-{parts[0]}"
        except:
            pass
        return display_date
    
    def confirm_delete_transaction(self, transaction_id):
        """Подтверждение удаления транзакции"""
        transaction_info = self.get_selected_transaction_info()
        if transaction_info:
            message = (f"Удалить транзакцию?\n\n"
                      f"ID: {transaction_info['id']}\n"
                      f"Дата: {transaction_info['date']}\n"
                      f"Время: {transaction_info['time']}\n"
                      f"Доход: {transaction_info['income']:.2f} руб.\n"
                      f"Расход: {transaction_info['expense']:.2f} руб.")
        else:
            message = f"Удалить транзакцию #{transaction_id}?"
        
        return QMessageBox.question(
            self, 
            'Подтверждение удаления', 
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
    
    def edit_selected_transaction(self):
        """Открывает диалог редактирования выбранной транзакции"""
        transaction_info = self.get_selected_transaction_info()
        if transaction_info:
            dialog = EditTransactionDialog(transaction_info, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                return dialog.get_updated_data()
        return None
    
    def delete_selected_transaction(self):
        """Удаляет выбранную транзакцию"""
        transaction_id = self.get_selected_transaction_id()
        if transaction_id:
            return transaction_id
        return None
    
    def confirm_delete_all_transactions(self):
        """Подтверждение удаления всех транзакций"""
        row_count = self.transactions_table.rowCount()
        if row_count == 0:
            return QMessageBox.StandardButton.No
            
        return QMessageBox.warning(
            self,
            'Удаление всех записей',
            f'Вы уверены, что хотите удалить ВСЕ записи ({row_count} шт.)?\n\nЭто действие нельзя отменить!',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )