from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QSpinBox, QDateEdit, QTimeEdit,
    QMessageBox, QScrollArea, QComboBox
)
from PyQt6.QtCore import QDate, QTime


class SessionAddWindow(QWidget):
    def __init__(self, plan, session=None, on_saved=None):
        super().__init__()
        self.plan = plan
        self.session = session
        self.on_saved = on_saved
        self.setWindowTitle("Редактировать занятие" if session else "Добавить занятие")
        self.setMinimumSize(480, 500)
        self._build()

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        from PyQt6.QtWidgets import QScrollArea
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        outer.addWidget(scroll)

        container = QWidget()
        scroll.setWidget(container)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(48, 32, 48, 32)
        layout.setSpacing(12)

        title_lbl = QLabel("Редактировать занятие" if self.session else "Добавить занятие")
        title_lbl.setStyleSheet("font-size: 32px; font-weight: bold;")
        layout.addWidget(title_lbl)
        layout.addSpacing(8)

        layout.addWidget(QLabel("Тип занятия:"))
        self.activity_input = QLineEdit()
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

        save_btn = QPushButton("Сохранить")
        save_btn.setFixedHeight(52)
        save_btn.clicked.connect(self._save)
        layout.addWidget(save_btn)
        layout.addStretch()

    def _save(self):
        from core.operations import add_session, edit_session
        activity = self.activity_input.text().strip()
        date = self.date_edit.date().toPyDate()
        time = self.time_edit.time().toPyTime()
        duration = self.duration_spin.value()

        if not activity:
            QMessageBox.warning(self, "Ошибка", "Введите тип занятия")
            return

        if self.session:
            ok, msg, _ = edit_session(self.session.id, activity, date, time, duration)
        else:
            ok, msg, _ = add_session(self.plan.id, activity, date, time, duration)

        if ok:
            if self.on_saved:
                self.on_saved()
            self.close()
        else:
            QMessageBox.warning(self, "Ошибка", msg)
