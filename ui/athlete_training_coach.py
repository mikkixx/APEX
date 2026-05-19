from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QWidget, QFrame, QMessageBox,
    QDateEdit, QDialog, QDialogButtonBox, QLineEdit, QSpinBox, QComboBox, QTimeEdit
)
from PyQt6.QtCore import Qt, QDate, QTime

ACTIVITY_TYPES = ["бег", "велосипед", "плавание", "силовая", "растяжка", "другое"]


class AthleteTrainingCoach:
    """Training plan view/edit for coach."""
    def __init__(self, specialist_data, athlete_data, layout):
        self.specialist_data = specialist_data
        self.athlete_data = athlete_data
        self.layout = layout
        self.page = 1

    def build(self):
        layout = self.layout

        header_row = QHBoxLayout()
        new_plan_btn = QPushButton("Новый план")
        new_plan_btn.setFixedHeight(48)
        new_plan_btn.setFixedWidth(160)
        new_plan_btn.clicked.connect(self._new_plan)
        header_row.addWidget(new_plan_btn)
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

        self._start_date = None
        self._end_date = None
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
            outer_layout = QVBoxLayout(outer)
            outer_layout.setContentsMargins(24, 20, 24, 20)
            outer_layout.setSpacing(12)

            plan_title = QLabel(f"{plan.title} ({plan.start_date} — {plan.end_date})")
            plan_title.setStyleSheet("font-size: 20px; font-weight: bold;")
            plan_title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            outer_layout.addWidget(plan_title)

            for session in plan_info['sessions']:
                card = self._session_card(session, plan.id)
                outer_layout.addWidget(card)

            # Bottom buttons
            bottom_row = QHBoxLayout()
            add_session_btn = QPushButton("Добавить занятие")
            add_session_btn.setFixedHeight(48)
            add_session_btn.clicked.connect(lambda _, pid=plan.id: self._add_session(pid))
            del_plan_btn = QPushButton("Удалить план")
            del_plan_btn.setFixedHeight(48)
            del_plan_btn.setStyleSheet("QPushButton { background: #1a1a1a; color: white; border-radius: 18px; padding: 10px 24px; font-size: 20px; }")
            del_plan_btn.clicked.connect(lambda _, pid=plan.id: self._delete_plan(pid))
            bottom_row.addWidget(add_session_btn)
            bottom_row.addSpacing(10)
            bottom_row.addWidget(del_plan_btn)
            bottom_row.addStretch()
            outer_layout.addLayout(bottom_row)

            self.scroll_layout.addWidget(outer)
        self.scroll_layout.addStretch()

    def _session_card(self, session, plan_id):
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

        # Status badge
        status_btn = QPushButton(session.status.capitalize())
        status_btn.setEnabled(False)
        status_btn.setStyleSheet("""
            QPushButton { background: white; color: #1a1a1a; border: 1.5px solid #1a1a1a;
                border-radius: 16px; padding: 6px 18px; font-size: 20px; }
        """)
        cl.addWidget(status_btn)

        btn_row = QHBoxLayout()
        detail_btn = QPushButton("Подробнее")
        detail_btn.setStyleSheet("QPushButton { background: #1a1a1a; color: white; border-radius: 16px; padding: 8px 24px; font-size: 20px; }")
        detail_btn.clicked.connect(lambda: self._open_session(session))
        btn_row.addWidget(detail_btn)
        btn_row.addStretch()
        cl.addLayout(btn_row)
        return card

    def _open_session(self, session):
        from ui.session_coach_window import SessionCoachWindow
        self.session_win = SessionCoachWindow(self.specialist_data, self.athlete_data, session, on_close=self._refresh)
        self.session_win.show()

    def _new_plan(self):
        from ui.new_plan_window import NewPlanWindow
        self.new_plan_win = NewPlanWindow(self.specialist_data['id'], self.athlete_data['id'], on_saved=self._refresh)
        self.new_plan_win.show()

    def _add_session(self, plan_id):
        from ui.add_session_window import AddSessionWindow
        self.add_sess = AddSessionWindow(plan_id, self.specialist_data['id'], on_saved=self._refresh)
        self.add_sess.show()

    def _delete_plan(self, plan_id):
        reply = QMessageBox.question(None, "Удалить план", "Удалить этот тренировочный план?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            from core.operations import delete_training_plan
            ok, msg, _ = delete_training_plan(plan_id, self.specialist_data['id'])
            if ok:
                self._refresh()
            else:
                QMessageBox.warning(None, "Ошибка", msg)

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
        row.addSpacing(8)
        row.addWidget(QLabel("По:")); row.addWidget(end)
        v.addLayout(row)
        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(dlg.accept); btns.rejected.connect(dlg.reject)
        v.addWidget(btns)
        if dlg.exec():
            self._start_date = start.date().toPyDate()
            self._end_date = end.date().toPyDate()
            self._refresh()
