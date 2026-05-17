from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QScrollArea, QSpinBox,
    QDoubleSpinBox, QTextEdit, QDateEdit, QMessageBox
)
from PyQt6.QtCore import QDate

class DiaryAddWindow(QWidget):
    def __init__(self, athlete_id, entry=None, on_saved=None):
        super().__init__()
        self.athlete_id = athlete_id
        self.entry = entry
        self.on_saved = on_saved
        self.setWindowTitle("Редактировать запись" if entry else "Добавить запись")
        self.setMinimumSize(520, 720)  # Чуть больше высоты для шрифта 20px
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

        # ✅ Глобальный стиль: шрифт 20px везде + уменьшенные кнопки +/-
        container.setStyleSheet("""
            QLabel, QLineEdit, QDateEdit, QSpinBox, QDoubleSpinBox, QTextEdit, QPushButton {
                font-size: 20px;
            }
        """)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(48, 32, 48, 32)
        layout.setSpacing(12)

        title = QLabel("Редактировать запись" if self.entry else "Добавить запись")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)
        layout.addSpacing(8)

        # Date
        layout.addWidget(QLabel("Дата:"))
        self.date_edit = QDateEdit(calendarPopup=True)
        self.date_edit.setFixedHeight(48)
        if self.entry:
            d = self.entry.date
            self.date_edit.setDate(QDate(d.year, d.month, d.day))
        else:
            self.date_edit.setDate(QDate.currentDate())
        layout.addWidget(self.date_edit)

        # ✅ Activity type: заменено на текстовое поле
        layout.addWidget(QLabel("Тип занятия:"))
        self.activity_input = QLineEdit()
        self.activity_input.setPlaceholderText("Введите тип занятия")
        self.activity_input.setFixedHeight(48)
        if self.entry:
            self.activity_input.setText(self.entry.activity_type)
        layout.addWidget(self.activity_input)

        # Duration
        layout.addWidget(QLabel("Длительность (мин):"))
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(1, 300)
        self.duration_spin.setFixedHeight(48)
        if self.entry:
            self.duration_spin.setValue(self.entry.duration)
        layout.addWidget(self.duration_spin)

        # Steps
        layout.addWidget(QLabel("Количество шагов:"))
        self.steps_spin = QSpinBox()
        self.steps_spin.setRange(0, 100000)
        self.steps_spin.setFixedHeight(48)
        if self.entry:
            self.steps_spin.setValue(self.entry.steps)
        layout.addWidget(self.steps_spin)

        # Sleep
        layout.addWidget(QLabel("Количество часов сна:"))
        self.sleep_spin = QDoubleSpinBox()
        self.sleep_spin.setRange(0, 24)
        self.sleep_spin.setSingleStep(0.5)
        self.sleep_spin.setFixedHeight(48)
        if self.entry:
            self.sleep_spin.setValue(self.entry.sleep_hours)
        layout.addWidget(self.sleep_spin)

        # Fatigue
        layout.addWidget(QLabel("Усталость (1–10):"))
        self.fatigue_spin = QSpinBox()
        self.fatigue_spin.setRange(1, 10)
        self.fatigue_spin.setFixedHeight(48)
        if self.entry:
            self.fatigue_spin.setValue(self.entry.fatigue)
        layout.addWidget(self.fatigue_spin)

        # Mood
        layout.addWidget(QLabel("Настроение (1–10):"))
        self.mood_spin = QSpinBox()
        self.mood_spin.setRange(1, 10)
        self.mood_spin.setFixedHeight(48)
        if self.entry:
            self.mood_spin.setValue(self.entry.mood)
        layout.addWidget(self.mood_spin)

        # Comment
        layout.addWidget(QLabel("Комментарий (необязательно):"))
        self.comment_edit = QTextEdit()
        self.comment_edit.setFixedHeight(110)
        if self.entry and self.entry.comment:
            self.comment_edit.setPlainText(self.entry.comment)
        layout.addWidget(self.comment_edit)

        layout.addSpacing(8)

        save_btn = QPushButton("Сохранить")
        save_btn.setFixedHeight(52)
        save_btn.clicked.connect(self._save)
        layout.addWidget(save_btn)
        layout.addStretch()

    def _save(self):
        from core.operations import add_diary_entry, edit_diary_entry
        d = self.date_edit.date().toPyDate()
        activity = self.activity_input.text().strip()  # ✅ Берём текст из поля
        duration = self.duration_spin.value()
        steps = self.steps_spin.value()
        sleep = self.sleep_spin.value()
        fatigue = self.fatigue_spin.value()
        mood = self.mood_spin.value()
        comment = self.comment_edit.toPlainText().strip() or None

        if self.entry:
            ok, msg, _ = edit_diary_entry(
                self.entry.id, self.athlete_id, d, activity,
                duration, steps, sleep, fatigue, mood, comment
            )
        else:
            ok, msg, _ = add_diary_entry(
                self.athlete_id, d, activity, duration, steps, sleep, fatigue, mood, comment
            )

        if ok:
            if self.on_saved:
                self.on_saved()
            self.close()
        else:
            QMessageBox.warning(self, "Ошибка", msg)
