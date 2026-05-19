from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QWidget, QFrame, QDateEdit, QDialog, QDialogButtonBox
)
from PyQt6.QtCore import Qt, QDate


class AthleteTrainingDoctor:
    """Doctor view: read-only training plan."""
    def __init__(self, specialist_data, athlete_data, layout):
        self.specialist_data = specialist_data
        self.athlete_data = athlete_data
        self.layout = layout
        self._start_date = None
        self._end_date = None

    def build(self):
        layout = self.layout

        header_row = QHBoxLayout()
        header_row.addStretch()
        title = QLabel("ТРЕНИРОВОЧНЫЙ ПЛАН")
        title.setStyleSheet("font-size: 48px; font-weight: bold;")
        header_row.addWidget(title)
        header_row.addStretch()
        range_btn = QPushButton("Выбрать диапазон  ∨")
        range_btn.setFixedWidth(280)
        range_btn.setFixedHeight(48)
        range_btn.clicked.connect(self._show_range)
        header_row.addWidget(range_btn)
        layout.addLayout(header_row)
        layout.addSpacing(16)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_layout.setSpacing(16)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_area.setWidget(self.scroll_widget)
        layout.addWidget(self.scroll_area)
        self._refresh()

    def _refresh(self):
        from core.operations import get_training_plan
        ok, msg, plans = get_training_plan(self.athlete_data['id'], self._start_date, self._end_date)

        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not ok or not plans:
            empty = QLabel("Тренировочных планов не найдено.")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setStyleSheet("color: #888; font-size: 20px; margin-top: 40px;")
            self.scroll_layout.addWidget(empty)
            return

        for plan_info in plans:
            plan = plan_info['plan']
            outer = QFrame()
            outer.setStyleSheet("QFrame { border: 1px solid #e0e0e0; border-radius: 20px; background: #fafafa; }")
            ol = QVBoxLayout(outer)
            ol.setContentsMargins(24, 20, 24, 20)
            ol.setSpacing(12)

            plan_title = QLabel(f"{plan.title} ({plan.start_date} — {plan.end_date})")
            plan_title.setStyleSheet("font-size: 20px; font-weight: bold;")
            plan_title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            ol.addWidget(plan_title)

            for session in plan_info['sessions']:
                card = QFrame()
                card.setStyleSheet("QFrame { background: white; border: 1px solid #e0e0e0; border-radius: 16px; }")
                cl = QVBoxLayout(card)
                cl.setContentsMargins(20, 14, 20, 14)
                cl.setSpacing(6)

                def row(lbl, val):
                    r = QHBoxLayout()
                    l = QLabel(f"{lbl}:")
                    l.setStyleSheet("font-weight: bold; font-size: 20px;")
                    v = QLabel(str(val))
                    v.setStyleSheet("font-size: 20px; color: #777;")
                    r.addWidget(l); r.addSpacing(4); r.addWidget(v); r.addStretch()
                    return r

                cl.addLayout(row("Тип занятия", session.activity_type))
                cl.addLayout(row("Длительность", f"{session.duration} мин"))

                status_btn = QPushButton(session.status.capitalize())
                status_btn.setEnabled(False)
                status_btn.setStyleSheet("""
                    QPushButton { background: white; color: #1a1a1a; border: 1.5px solid #1a1a1a;
                        border-radius: 16px; padding: 6px 18px; font-size: 20px; }
                """)
                cl.addWidget(status_btn)

                detail_btn = QPushButton("Подробнее")
                detail_btn.setStyleSheet("QPushButton { background: #1a1a1a; color: white; border-radius: 16px; padding: 8px 24px; font-size: 20px; }")
                br = QHBoxLayout()
                br.addWidget(detail_btn); br.addStretch()
                cl.addLayout(br)
                ol.addWidget(card)

            self.scroll_layout.addWidget(outer)
        self.scroll_layout.addStretch()

    def _show_range(self):
        dlg = QDialog()
        dlg.setWindowTitle("Выбрать диапазон")
        dlg.setFixedSize(400, 160)
        v = QVBoxLayout(dlg)
        row = QHBoxLayout()
        start = QDateEdit(calendarPopup=True)
        start.setDate(QDate.currentDate().addDays(-7))
        start.setFixedHeight(48)
        end = QDateEdit(calendarPopup=True)
        end.setDate(QDate.currentDate())
        end.setFixedHeight(48)
        row.addWidget(QLabel("С:")); row.addWidget(start)
        row.addSpacing(8); row.addWidget(QLabel("По:")); row.addWidget(end)
        v.addLayout(row)
        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(dlg.accept); btns.rejected.connect(dlg.reject)
        v.addWidget(btns)
        if dlg.exec():
            self._start_date = start.date().toPyDate()
            self._end_date = end.date().toPyDate()
            self._refresh()
