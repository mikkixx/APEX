from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QDateEdit, QMessageBox
)
from PyQt6.QtCore import QDate
from core.operations import create_training_plan

class PlanAddWindow(QWidget):
    # ✅ 1. ВАЖНО: должно быть __init__ (два подчеркивания)
    def __init__(self, athlete_id, coach_id, on_saved=None):
        super().__init__()
        self.athlete_id = athlete_id
        self.coach_id = coach_id
        self.on_saved = on_saved
        self.setWindowTitle("Новый тренировочный план")
        self.setMinimumSize(480, 380)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(48, 32, 48, 32)
        layout.setSpacing(12)

        title = QLabel("Новый план")
        title.setStyleSheet("font-size: 32px; font-weight: bold;")
        layout.addWidget(title)
        layout.addSpacing(8)

        layout.addWidget(QLabel("Название:"))
        self.title_input = QLineEdit()
        self.title_input.setFixedHeight(52)
        layout.addWidget(self.title_input)

        layout.addWidget(QLabel("Дата начала:"))
        self.start_date = QDateEdit(calendarPopup=True)
        self.start_date.setDate(QDate.currentDate())
        self.start_date.setFixedHeight(52)
        layout.addWidget(self.start_date)

        layout.addWidget(QLabel("Дата окончания:"))
        self.end_date = QDateEdit(calendarPopup=True)
        self.end_date.setDate(QDate.currentDate().addDays(30))
        self.end_date.setFixedHeight(52)
        layout.addWidget(self.end_date)

        save_btn = QPushButton("Создать план")
        save_btn.setFixedHeight(52)
        save_btn.clicked.connect(self._save)
        layout.addWidget(save_btn)
        layout.addStretch()

    def _save(self):
        title = self.title_input.text().strip()
        if not title:
            QMessageBox.warning(self, "Ошибка", "Введите название плана")
            return
            
        start = self.start_date.date().toPyDate()
        end = self.end_date.date().toPyDate()
        
        if end < start:
            QMessageBox.warning(self, "Ошибка", "Дата окончания раньше начала")
            return

        # ✅ 2. ВАЖНО: Порядок аргументов строго как в operations.py
        # (specialist_id, athlete_id, start_date, end_date, title)
        ok, msg, _ = create_training_plan(
            specialist_id=self.coach_id,
            athlete_id=self.athlete_id,
            start_date=start,
            end_date=end,
            title=title
        )
        if ok:
            if self.on_saved:
                self.on_saved()
            self.close()
        else:
            QMessageBox.warning(self, "Ошибка", msg)