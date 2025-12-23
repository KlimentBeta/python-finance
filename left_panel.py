from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QComboBox, QDateEdit, QPushButton, QHBoxLayout 
from PyQt6.QtCore import QDate, Qt
from PyQt6.QtGui import QFont

class LeftPanel(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                padding: 12px;
            }
        """)
        
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout(self)
        
        # Заголовок панели фильтров
        filter_label = QLabel('Фильтры по дате')
        filter_label.setFont(QFont('Arial', 12, QFont.Weight.Bold))
        filter_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(filter_label)
        
        layout.addSpacing(15)
        
        # Период фильтрации
        period_label = QLabel('Период:')
        period_label.setFont(QFont('Arial', 10))
        layout.addWidget(period_label)
        
        self.period_combo = QComboBox()
        self.period_combo.addItems(['За все время', 'Сегодня', 'Последние 7 дней', 
                                   'Текущий месяц', 'Произвольный период'])
        self.period_combo.setStyleSheet("""
            QComboBox {
                padding: 6px;
                font-size: 11px;
                border: 1px solid #ced4da;
                border-radius: 4px;
                background-color: white;
            }
        """)
        layout.addWidget(self.period_combo)
        
        layout.addSpacing(12)
        
        # Начальная дата
        start_date_label = QLabel('С:')
        start_date_label.setFont(QFont('Arial', 10))
        layout.addWidget(start_date_label)
        
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addDays(-30))
        self.start_date.setCalendarPopup(True)
        self.start_date.setStyleSheet("""
            QDateEdit {
                padding: 6px;
                font-size: 11px;
                border: 1px solid #ced4da;
                border-radius: 4px;
                background-color: white;
            }
        """)
        layout.addWidget(self.start_date)
        
        layout.addSpacing(8)
        
        # Конечная дата
        end_date_label = QLabel('По:')
        end_date_label.setFont(QFont('Arial', 10))
        layout.addWidget(end_date_label)
        
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        self.end_date.setStyleSheet("""
            QDateEdit {
                padding: 6px;
                font-size: 11px;
                border: 1px solid #ced4da;
                border-radius: 4px;
                background-color: white;
            }
        """)
        layout.addWidget(self.end_date)
        
        layout.addSpacing(15)

        # --- Фильтр по категории ---
        category_filter_layout = QHBoxLayout()

        category_label = QLabel("Категория:")
        category_label.setFont(QFont('Arial', 10, QFont.Weight.Bold))
        category_filter_layout.addWidget(category_label)

        self.category_filter_combo = QComboBox()  # ← СОЗДАЁМ АТРИБУТ
        self.category_filter_combo.addItem("Все")
        self.category_filter_combo.addItem("Продукты")
        self.category_filter_combo.addItem("Транспорт")
        self.category_filter_combo.addItem("Зарплата")
        self.category_filter_combo.addItem("Развлечения")
        self.category_filter_combo.setEditable(True)  # можно вводить своё
        category_filter_layout.addWidget(self.category_filter_combo)

        layout.addLayout(category_filter_layout)
        
        # Кнопка применения фильтра
        self.apply_filter_btn = QPushButton('Применить фильтр')
        self.apply_filter_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 10px;
                font-size: 11px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        layout.addWidget(self.apply_filter_btn)
        
        # Кнопка сброса фильтра
        self.reset_filter_btn = QPushButton('Сбросить фильтр')
        self.reset_filter_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 10px;
                font-size: 11px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        layout.addWidget(self.reset_filter_btn)
        
        layout.addStretch()

        
    
    def reset_filters(self):
        """Сброс фильтров к значениям по умолчанию"""
        self.period_combo.setCurrentIndex(0)
        self.start_date.setDate(QDate.currentDate().addDays(-30))
        self.end_date.setDate(QDate.currentDate())
    
    def get_filter_params(self):
        """Возвращает параметры фильтра"""
        period_index = self.period_combo.currentIndex()
        start_date = self.start_date.date().toString("yyyy-MM-dd")
        end_date = self.end_date.date().toString("yyyy-MM-dd")
        
        # Преобразуем индекс в тип фильтра
        filter_types = ['all', 'today', 'week', 'month', 'custom']
        filter_type = filter_types[period_index]
        
        return filter_type, start_date, end_date
    

    def get_selected_category(self) -> str | None:
        text = self.category_filter_combo.currentText()
        return None if text == "Все" else text
    
    def update_category_filter_options(self, categories: list[str]):
        self.category_filter_combo.clear()
        self.category_filter_combo.addItem("Все")
        for cat in sorted(set(c for c in categories if c)):
            self.category_filter_combo.addItem(cat)