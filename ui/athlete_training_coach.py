from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QWidget, QFrame, QMessageBox,
    QDateEdit, QDialog, QDialogButtonBox
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
from core.operations import get_training_plan, delete_training_plan

class AthleteTrainingCoach:
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
        new_plan_btn = QPushButton("Новый план")
        new_plan_btn.setFixedHeight(50)
        new_plan_btn.setFixedWidth(180)
        new_plan_btn.setStyleSheet("""
            QPushButton { background: #1a1a1a; color: white; border-radius: 20px;
                font-size: 20px; font-weight: bold; padding: 0px; }
            QPushButton:hover { background: #333; }
        """)
        new_plan_btn.clicked.connect(self._new_plan)
        header_row.addWidget(new_plan_btn)
        header_row.addStretch()

        title = QLabel("ТРЕНИРОВОЧНЫЙ ПЛАН")
        title.setStyleSheet("font-size: 48px; font-weight: bold; letter-spacing: 1px; border: none; background: transparent;")
        header_row.addWidget(title)
        header_row.addStretch()

        range_btn = QPushButton("Выбрать диапазон  ∨")
        range_btn.setFixedWidth(292)
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
                outer_layout.addWidget(self._session_card(session, plan.id))

            bottom_row = QHBoxLayout()
            add_session_btn = QPushButton("Добавить занятие")
            add_session_btn.setFixedHeight(50)
            add_session_btn.setStyleSheet("""
                QPushButton { background: #1a1a1a; color: white; border-radius: 20px;
                    font-size: 20px; font-weight: bold; padding: 0px 20px; }
                QPushButton:hover { background: #333; }
            """)
            add_session_btn.clicked.connect(lambda _, pid=plan.id: self._add_session(pid))

            del_plan_btn = QPushButton("Удалить план")
            del_plan_btn.setFixedHeight(50)
            del_plan_btn.setStyleSheet("""
                QPushButton { background: #1a1a1a; color: white; border-radius: 20px;
                    font-size: 20px; font-weight: bold; padding: 0px 20px; }
                QPushButton:hover { background: #333; }
            """)
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
        
        status_badge = QPushButton(session.status.capitalize())
        status_badge.setEnabled(False)
        status_badge.setStyleSheet("""
            QPushButton { background: white; color: #1a1a1a; border: 1.5px solid #1a1a1a;
                border-radius: 20px; padding: 8px 24px; font-size: 20px; }
        """)
        btn_row.addWidget(status_badge)
        
        btn_row.addSpacing(10)

        detail_btn = QPushButton("Подробнее")
        detail_btn.setStyleSheet("""
            QPushButton { background: #1a1a1a; color: white; border-radius: 20px;
                padding: 8px 24px; font-size: 20px; }
            QPushButton:hover { background: #333; }
        """)
        detail_btn.clicked.connect(lambda: self._open_session(session))
        btn_row.addWidget(detail_btn)
        btn_row.addStretch()
        cl.addLayout(btn_row)
        return card

    def _open_session(self, session):
        from ui.session_coach_window import SessionCoachWindow
        self.session_win = SessionCoachWindow(
            self.specialist_data, self.athlete_data, session
        )
        self.session_win.show()

    def _new_plan(self):
        from ui.plan_add_window import PlanAddWindow
        self.new_plan_win = PlanAddWindow(
            athlete_id=self.athlete_data['id'],
            coach_id=self.specialist_data['id'],
            on_saved=self._refresh,
            parent=self.parent
        )
        self.new_plan_win.show()

    def _add_session(self, plan_id):
        from ui.session_add_window import SessionAddWindow
        self.add_sess = SessionAddWindow(plan_id, self.specialist_data['id'], on_saved=self._refresh)
        self.add_sess.show()

    def _delete_plan(self, plan_id):
        confirm_msg = QMessageBox(self.parent)
        confirm_msg.setWindowTitle("Подтверждение удаления")
        confirm_msg.setText("Вы уверены, что хотите удалить этот тренировочный план?\nЭто действие нельзя отменить.")
        confirm_msg.setIcon(QMessageBox.Icon.Question)
        confirm_msg.setFont(QFont("Alegreya", 20))
        confirm_msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        confirm_msg.button(QMessageBox.StandardButton.Yes).setText("Удалить")
        confirm_msg.button(QMessageBox.StandardButton.No).setText("Отмена")

        if confirm_msg.exec() == QMessageBox.StandardButton.Yes:
            ok, msg_text, _ = delete_training_plan(self.specialist_data['id'], plan_id)

            result_msg = QMessageBox(self.parent)
            result_msg.setFont(QFont("Alegreya", 20))
            result_msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            result_msg.button(QMessageBox.StandardButton.Ok).setText("Хорошо")

            if ok:
                result_msg.setWindowTitle("Успех")
                result_msg.setText("Тренировочный план успешно удалён.")
                result_msg.setIcon(QMessageBox.Icon.Information)
                self._refresh()
            else:
                result_msg.setWindowTitle("Ошибка")
                result_msg.setText(msg_text)
                result_msg.setIcon(QMessageBox.Icon.Warning)

            result_msg.exec()

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