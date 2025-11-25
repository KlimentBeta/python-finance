from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class RightPanel(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background-color: #e8f4fd;
                border: 2px solid #b8daff;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Заголовок панели баланса
        balance_label = QLabel('Финансовый баланс')
        balance_label.setFont(QFont('Arial', 13, QFont.Weight.Bold))
        balance_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(balance_label)
        
        layout.addSpacing(15)
        
        # Общий доход
        income_frame = QFrame()
        income_frame.setStyleSheet("""
            QFrame {
                background-color: #d4edda;
                border: 2px solid #c3e6cb;
                border-radius: 6px;
                padding: 10px;
            }
        """)
        income_layout = QVBoxLayout(income_frame)
        income_title = QLabel('Общие доходы:')
        income_title.setFont(QFont('Arial', 10))
        self.total_income_label = QLabel('0.00 руб.')
        self.total_income_label.setFont(QFont('Arial', 12, QFont.Weight.Bold))
        self.total_income_label.setStyleSheet("color: #155724;")
        income_layout.addWidget(income_title)
        income_layout.addWidget(self.total_income_label)
        layout.addWidget(income_frame)
        
        layout.addSpacing(8)
        
        # Общий расход
        expense_frame = QFrame()
        expense_frame.setStyleSheet("""
            QFrame {
                background-color: #f8d7da;
                border: 2px solid #f5c6cb;
                border-radius: 6px;
                padding: 10px;
            }
        """)
        expense_layout = QVBoxLayout(expense_frame)
        expense_title = QLabel('Общие расходы:')
        expense_title.setFont(QFont('Arial', 10))
        self.total_expense_label = QLabel('0.00 руб.')
        self.total_expense_label.setFont(QFont('Arial', 12, QFont.Weight.Bold))
        self.total_expense_label.setStyleSheet("color: #721c24;")
        expense_layout.addWidget(expense_title)
        expense_layout.addWidget(self.total_expense_label)
        layout.addWidget(expense_frame)
        
        layout.addSpacing(12)
        
        # Итоговый баланс
        balance_frame = QFrame()
        balance_frame.setStyleSheet("""
            QFrame {
                background-color: #d1ecf1;
                border: 2px solid #bee5eb;
                border-radius: 6px;
                padding: 9px;
            }
        """)
        balance_layout = QVBoxLayout(balance_frame)
        balance_title = QLabel('ИТОГОВЫЙ БАЛАНС:')
        balance_title.setFont(QFont('Arial', 10, QFont.Weight.Bold))
        self.final_balance_label = QLabel('0.00 руб.')
        self.final_balance_label.setFont(QFont('Arial', 12, QFont.Weight.Bold))
        balance_layout.addWidget(balance_title)
        balance_layout.addWidget(self.final_balance_label)
        layout.addWidget(balance_frame)
        
        layout.addSpacing(15)
        
        # Статистика
        stats_label = QLabel('Статистика:')
        stats_label.setFont(QFont('Arial', 11, QFont.Weight.Bold))
        layout.addWidget(stats_label)
        
        self.total_transactions_label = QLabel('Всего транзакций: 0')
        self.total_transactions_label.setFont(QFont('Arial', 9))
        layout.addWidget(self.total_transactions_label)
        
        self.avg_income_label = QLabel('Средний доход: 0.00 руб.')
        self.avg_income_label.setFont(QFont('Arial', 9))
        layout.addWidget(self.avg_income_label)
        
        self.avg_expense_label = QLabel('Средний расход: 0.00 руб.')
        self.avg_expense_label.setFont(QFont('Arial', 9))
        layout.addWidget(self.avg_expense_label)
        
        layout.addSpacing(20)
        
        # Кнопка экспорта
        self.export_button = QPushButton('📊 Экспорт в Excel')
        self.export_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 12px;
                font-size: 12px;
                font-weight: bold;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
        """)
        layout.addWidget(self.export_button)
        
        layout.addStretch()
    
    def update_balance(self, summary: dict):
        """Обновление панели баланса на основе сводки"""
        # Обновление labels
        self.total_income_label.setText(f"{summary['total_income']:.2f} руб.")
        self.total_expense_label.setText(f"{summary['total_expense']:.2f} руб.")
        self.final_balance_label.setText(f"{summary['balance']:.2f} руб.")
        
        # Цвет баланса в зависимости от значения
        if summary['balance'] > 0:
            self.final_balance_label.setStyleSheet("color: #155724;")
        elif summary['balance'] < 0:
            self.final_balance_label.setStyleSheet("color: #721c24;")
        else:
            self.final_balance_label.setStyleSheet("color: #856404;")
        
        # Статистика
        self.total_transactions_label.setText(f"Всего транзакций: {summary['total_transactions']}")
        self.avg_income_label.setText(f"Средний доход: {summary['avg_income']:.2f} руб.")
        self.avg_expense_label.setText(f"Средний расход: {summary['avg_expense']:.2f} руб.")