from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QSpinBox, QDateEdit, QTimeEdit,
    QMessageBox, QScrollArea
)
from PyQt6.QtCore import QDate, QTime
from core.operations import add_session, edit_session

class SessionAddWindow(QWidget):
    def __init__(self, plan_id, specialist_id, session=None, on_saved=None):
        super().__init__()
        self.plan_id = plan_id
        self.specialist_id = specialist_id
        self.session = session
        self.on_saved = on_saved
        self.setWindowTitle("Редактировать занятие" if session else "Добавить занятие")
        self.setMinimumSize(520, 500)
        self._build()

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        outer.addWidget(scroll)

        container = QWidget()
        scroll.setWidget(container)

        container.setStyleSheet("""
            QLabel, QLineEdit, QDateEdit, QTimeEdit, QSpinBox, QPushButton {
                font-size: 20px;
            }
        """)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(48, 32, 48, 32)
        layout.setSpacing(12)

        title_lbl = QLabel("Редактировать занятие" if self.session else "Добавить занятие")
        title_lbl.setStyleSheet("font-size: 28px; font-weight: bold;")
        layout.addWidget(title_lbl)
        layout.addSpacing(8)

        layout.addWidget(QLabel("Тип занятия:"))
        self.activity_input = QLineEdit()
        self.activity_input.setPlaceholderText("Например: Бег, Силовая")
        self.activity_input.setFixedHeight(52)
        if self.session:
            self.activity_input.setText(self.session.activity_type)
        layout.addWidget(self.activity_input)

        layout.addWidget(QLabel("Дата:"))
        self.date_edit = QDateEdit(calendarPopup=True)
        self.date_edit.setFixedHeight(52)
        if self.session:
            d = self.session.date
            self.date_edit.setDate(QDate(d.year, d.month, d.day))
        else:
            self.date_edit.setDate(QDate.currentDate())
        layout.addWidget(self.date_edit)

        layout.addWidget(QLabel("Время (необязательно):"))
        self.time_edit = QTimeEdit()
        self.time_edit.setFixedHeight(52)
        if self.session and self.session.time:
            t = self.session.time
            self.time_edit.setTime(QTime(t.hour, t.minute))
        layout.addWidget(self.time_edit)

        layout.addWidget(QLabel("Длительность (мин):"))
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(1, 300)
        self.duration_spin.setFixedHeight(52)
        if self.session:
            self.duration_spin.setValue(self.session.duration)
        layout.addWidget(self.duration_spin)

        layout.addSpacing(20)

        save_btn = QPushButton("Сохранить")
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
        activity = self.activity_input.text().strip()
        date = self.date_edit.date().toPyDate()
        time = self.time_edit.time().toPyTime()
        duration = self.duration_spin.value()

        if not activity:
            QMessageBox.warning(self, "Ошибка", "Введите тип занятия")
            return

        if self.session:
            ok, msg, _ = edit_session(
                self.specialist_id, 
                self.session.id, 
                date, time, activity, duration
            )
        else:
            ok, msg, _ = add_session(
                self.specialist_id, 
                self.plan_id,  
                date, time, activity, duration
            )

        if ok:
            if self.on_saved:
                self.on_saved()
            self.close()
        else:
            QMessageBox.warning(self, "Ошибка", msg)