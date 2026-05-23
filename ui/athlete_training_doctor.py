from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QWidget, QFrame, QDateEdit, QDialog, QDialogButtonBox
)
from PyQt6.QtCore import Qt, QDate
from core.operations import get_training_plan
from PyQt6.QtGui import QFont

class AthleteTrainingDoctor:
    def __init__(self, specialist_data, athlete_data, layout, parent_widget=None):
        self.specialist_data = specialist_data
        self.athlete_data = athlete_data
        self.layout = layout
        self.parent = parent_widget
        self._start_date = None
        self._end_date = None

    def build(self):
        layout = self.layout

        header_row = QHBoxLayout()
        header_row.addStretch()
        title = QLabel("ТРЕНИРОВОЧНЫЙ ПЛАН")
        title.setStyleSheet("font-size: 48px; font-weight: bold; letter-spacing: 1px; border: none; background: transparent;")
        header_row.addWidget(title)
        header_row.addStretch()

        range_btn = QPushButton("Выбрать диапазон  ∨")
        range_btn.setFixedWidth(292)
        range_btn.setFixedHeight(50)
        range_btn.setStyleSheet("""
            QPushButton { background: #1a1a1a; color: white; border-radius: 20px;
                font-size: 20px; font-weight: bold; }
            QPushButton:hover { background: #333; }
        """)
        range_btn.clicked.connect(self._show_range_picker)
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
        athlete_id = self.athlete_data.get('id')
        if not athlete_id:
            return
            
        ok, msg, plans = get_training_plan(athlete_id, self._start_date, self._end_date)

        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not ok or not plans:
            empty = QLabel("Тренировочных планов не найдено.")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setStyleSheet("color: #888; font-size: 20px; margin-top: 40px; background: transparent; border: none;")
            self.scroll_layout.addWidget(empty)
            return

        for plan_info in plans:
            plan = plan_info['plan']
            outer = QFrame()
            outer.setStyleSheet("QFrame { border: 1px solid #e0e0e0; border-radius: 20px; background: #fafafa; }")
            outer_layout = QVBoxLayout(outer)
            outer_layout.setContentsMargins(24, 20, 24, 20)
            outer_layout.setSpacing(12)

            plan_title = QLabel(f"{plan.title} ({plan.start_date} — {plan.end_date})")
            plan_title.setStyleSheet("font-size: 28px; font-weight: bold; border: none; background: transparent;")
            plan_title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            outer_layout.addWidget(plan_title)

            for session in plan_info['sessions']:
                outer_layout.addWidget(self._session_card(session))

            self.scroll_layout.addWidget(outer)
        self.scroll_layout.addStretch()

    def _session_card(self, session):
        card = QFrame()
        card.setStyleSheet("QFrame { background: white; border: 1px solid #e0e0e0; border-radius: 20px; }")
        cl = QVBoxLayout(card)
        cl.setContentsMargins(20, 14, 20, 14)
        cl.setSpacing(6)

        def row(lbl, val):
            r = QHBoxLayout()
            l = QLabel(f"{lbl}:")
            l.setStyleSheet("font-weight: bold; font-size: 20px; background: transparent; border: none;")
            v = QLabel(str(val))
            v.setStyleSheet("font-size: 20px; color: #777; background: transparent; border: none;")
            r.addWidget(l); r.addSpacing(4); r.addWidget(v); r.addStretch()
            return r

        cl.addLayout(row("Тип занятия", session.activity_type))
        cl.addLayout(row("Длительность", f"{session.duration} мин"))

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        status_badge = QPushButton(session.status.capitalize())
        status_badge.setEnabled(False)
        status_badge.setFixedHeight(46)
        status_badge.setStyleSheet("""
            QPushButton { background: transparent; color: #1a1a1a; border: 1.5px solid #1a1a1a;
                border-radius: 20px; padding: 8px 24px; font-size: 20px; }
        """)
        btn_row.addWidget(status_badge)

        detail_btn = QPushButton("Подробнее")
        detail_btn.setFixedHeight(46)
        detail_btn.setStyleSheet("""
            QPushButton { background: #1a1a1a; color: white; border-radius: 20px;
                padding: 8px 24px; font-size: 20px; }
            QPushButton:hover { background: #333; }
        """)
        detail_btn.clicked.connect(lambda: self._open_detail(session))
        btn_row.addWidget(detail_btn)
        btn_row.addStretch()
        cl.addLayout(btn_row)
        return card

    def _open_detail(self, session):
        from ui.session_detail_window import SessionDetailWindow
        self.detail_win = SessionDetailWindow(session, self.athlete_data['id'])
        self.detail_win.show()

    def _show_range_picker(self):
        dlg = QDialog(self.parent)
        dlg.setWindowTitle("Выбрать диапазон")
        dlg.setFixedSize(400, 180)
        dlg.setFont(QFont("Alegreya", 20))
        v = QVBoxLayout(dlg)
        row = QHBoxLayout()

        start = QDateEdit(calendarPopup=True)
        start.setFixedSize(160, 60)
        start.setDate(QDate.currentDate().addDays(-7))
        end = QDateEdit(calendarPopup=True)
        end.setFixedSize(160, 60)
        end.setDate(QDate.currentDate())

        lbl_from = QLabel("С:")
        lbl_from.setStyleSheet("font-size: 20px; background: transparent; border: none;")
        row.addWidget(lbl_from)
        row.addWidget(start)
        row.addSpacing(8)

        lbl_to = QLabel("По:")
        lbl_to.setStyleSheet("font-size: 20px; background: transparent; border: none;")
        row.addWidget(lbl_to)
        row.addWidget(end)
        v.addLayout(row)

        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btns.button(QDialogButtonBox.StandardButton.Ok).setText("Применить")
        btns.button(QDialogButtonBox.StandardButton.Cancel).setText("Отмена")
        btns.accepted.connect(dlg.accept)
        btns.rejected.connect(dlg.reject)
        v.addWidget(btns)

        if dlg.exec():
            self._start_date = start.date().toPyDate()
            self._end_date = end.date().toPyDate()
            self._refresh()