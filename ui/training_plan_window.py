from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QWidget, QComboBox, QFrame, QMessageBox, QDateEdit
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
from ui.base_window import BaseWindow


class SessionCard(QFrame):
    def __init__(self, session, athlete_id, parent_window):
        super().__init__()
        self.session = session
        self.athlete_id = athlete_id
        self.parent_window = parent_window
        self._build()

    def _build(self):
        self.setStyleSheet("""
            QFrame {
                background: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 20px;
            }
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(6)

        type_row = QHBoxLayout()
        type_lbl = QLabel("Тип занятия:")
        type_lbl.setStyleSheet("font-weight: bold;")
        type_val = QLabel(self.session.activity_type)
        type_val.setStyleSheet("color: #777;")
        type_row.addWidget(type_lbl)
        type_row.addSpacing(4)
        type_row.addWidget(type_val)
        type_row.addStretch()
        layout.addLayout(type_row)

        dur_row = QHBoxLayout()
        dur_lbl = QLabel("Длительность:")
        dur_lbl.setStyleSheet("font-weight: bold;")
        dur_val = QLabel(f"{self.session.duration} мин")
        dur_val.setStyleSheet("color: #777;")
        dur_row.addWidget(dur_lbl)
        dur_row.addSpacing(4)
        dur_row.addWidget(dur_val)
        dur_row.addStretch()
        layout.addLayout(dur_row)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        if self.session.status == 'выполнено':
            done_btn = QPushButton("Выполнено")
            done_btn.setEnabled(False)
            done_btn.setStyleSheet("""
                QPushButton { background: #1a1a1a; color: white;
                    border-radius: 20px; padding: 8px 18px; font-size: 13px; }
            """)
            btn_row.addWidget(done_btn)
        else:
            status_combo = QComboBox()
            status_combo.addItems(["Выберите статус", "выполнено", "пропущено"])
            status_combo.setCurrentText(self.session.status if self.session.status != 'запланировано' else "Выберите статус")
            status_combo.setStyleSheet("""
                QComboBox { background: #1a1a1a; color: white; border-radius: 16px;
                    padding: 8px 18px; font-size: 20px; border: none; }
                QComboBox::drop-down { border: none; }
                QComboBox QAbstractItemView { background: white; color: black; }
            """)
            status_combo.currentTextChanged.connect(lambda v: self._update_status(v))
            btn_row.addWidget(status_combo)

        detail_btn = QPushButton("Подробнее")
        detail_btn.setStyleSheet("""
            QPushButton { background: #1a1a1a; color: white;
                border-radius: 20px; padding: 8px 18px; font-size: 20px; }
        """)
        detail_btn.clicked.connect(self._open_detail)
        btn_row.addWidget(detail_btn)
        btn_row.addStretch()

        layout.addLayout(btn_row)

    def _update_status(self, status):
        if status == "Выберите статус":
            return
        from core.operations import update_session_status
        ok, msg, _ = update_session_status(self.session.id, self.athlete_id, status)
        if not ok:
            QMessageBox.warning(self, "Ошибка", msg)

    def _open_detail(self):
        from ui.session_detail_window import SessionDetailWindow
        self.detail = SessionDetailWindow(self.session, self.athlete_id)
        self.detail.show()


class TrainingPlanWindow(BaseWindow):
    active_tab = "training"

    def __init__(self, user_data):
        super().__init__(user_data)
        self._load()

    def _load(self):
        layout = self._content_layout

        # Header row
        header_row = QHBoxLayout()
        title = QLabel("ТРЕНИРОВОЧНЫЙ ПЛАН")
        title.setStyleSheet("font-size: 48px; font-weight: bold; letter-spacing: 1px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_row.addStretch()
        header_row.addWidget(title)
        header_row.addStretch()

        range_btn = QPushButton("Выбрать диапазон  ∨")
        range_btn.setFixedWidth(292)
        range_btn.clicked.connect(self._show_range_picker)
        header_row.addWidget(range_btn)
        layout.addLayout(header_row)
        layout.addSpacing(16)

        # Scroll area for plan cards
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        layout.addWidget(self.scroll_area)

        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_layout.setSpacing(16)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_area.setWidget(self.scroll_widget)

        self._refresh_plans()

    def _refresh_plans(self, start_date=None, end_date=None):
        from core.operations import get_training_plan, sync_overdue_sessions
        athlete_id = self.user_data['id']
        sync_overdue_sessions(athlete_id)
        ok, msg, plans = get_training_plan(athlete_id, start_date, end_date)

        # Clear
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not ok or not plans:
            empty = QLabel("Тренировочный план не найден.")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setStyleSheet("color: #888; font-size: 20px; margin-top: 40px;")
            self.scroll_layout.addWidget(empty)
            return

        outer = QFrame()
        outer.setStyleSheet("QFrame { border: 1px solid #e0e0e0; border-radius: 20px; background: #fafafa; }")
        outer_layout = QVBoxLayout(outer)
        outer_layout.setContentsMargins(24, 20, 24, 20)
        outer_layout.setSpacing(12)

        for plan_info in plans:
            plan = plan_info['plan']
            plan_title = QLabel(f"{plan.title} ({plan.start_date} — {plan.end_date})")
            plan_title.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 4px;")
            plan_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            outer_layout.addWidget(plan_title)

            sessions = plan_info['sessions']
            if not sessions:
                no_s = QLabel("Занятий в плане не найдено.")
                no_s.setStyleSheet("color: #888;")
                outer_layout.addWidget(no_s)
            for session in sessions:
                card = SessionCard(session, athlete_id, self)
                outer_layout.addWidget(card)

        self.scroll_layout.addWidget(outer)
        self.scroll_layout.addStretch()

    def _show_range_picker(self):
        from PyQt6.QtWidgets import QDialog, QDialogButtonBox
        dlg = QDialog(self)
        dlg.setWindowTitle("Выбрать диапазон")
        dlg.setFixedSize(400, 180)
        dlg.setFont(QFont("Alegreya", 18))
        v = QVBoxLayout(dlg)
        row = QHBoxLayout()

        start = QDateEdit(calendarPopup=True)
        start.setFixedSize(160, 60)
        start.setDate(QDate.currentDate().addDays(-7))
        end = QDateEdit(calendarPopup=True)
        end.setFixedSize(160, 60)
        end.setDate(QDate.currentDate())

        lbl_from = QLabel("С:")
        lbl_from.setStyleSheet("font-size: 18px;")
        row.addWidget(lbl_from)
        row.addWidget(start)
        row.addSpacing(8)

        lbl_to = QLabel("По:")
        lbl_to.setStyleSheet("font-size: 18px;")
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
            from datetime import date
            s = start.date().toPyDate()
            e = end.date().toPyDate()
            self._refresh_plans(s, e)
