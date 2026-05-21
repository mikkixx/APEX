from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QScrollArea, QDateEdit, QMessageBox, QWidget
)
from PyQt6.QtCore import QDate
from core.operations import create_training_plan

class PlanAddWindow(QDialog):
    def __init__(self, athlete_id, coach_id, on_saved=None, parent=None):
        super().__init__(parent)
        self.athlete_id = athlete_id
        self.coach_id = coach_id
        self.on_saved = on_saved
        self.setWindowTitle("Новый тренировочный план")
        self.setMinimumSize(480, 530)
        self.setModal(True)
        self._build()

    def _build(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        main_layout.addWidget(scroll)

        container = QWidget()
        scroll.setWidget(container)

        container.setStyleSheet("""
            QLabel, QLineEdit, QDateEdit, QPushButton {
                font-size: 20px;
            }
            QDateEdit {
                padding: 0 10px;
                background: white;
            }
        """)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(48, 32, 48, 32)
        layout.setSpacing(12)

        title = QLabel("Новый план")
        title.setStyleSheet("font-size: 32px; font-weight: bold;")
        layout.addWidget(title)
        layout.addSpacing(8)

        layout.addWidget(QLabel("Название:"))
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Например: Базовая подготовка")
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

        layout.addSpacing(16)

        save_btn = QPushButton("Создать план")
        save_btn.setFixedHeight(56)
        save_btn.setStyleSheet("""
            QPushButton {
                background: #1a1a1a; 
                color: white; 
                border-radius: 20px; 
                font-weight: bold;
            }
            QPushButton:hover { background: #333; }
        """)
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
            QMessageBox.warning(self, "Ошибка", "Дата окончания должна быть позже даты начала")
            return

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
            self.accept()
        else:
            QMessageBox.warning(self, "Ошибка", msg)