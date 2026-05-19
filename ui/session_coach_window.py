from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QTextEdit, QMessageBox,
    QDialog, QVBoxLayout as DVL, QDialogButtonBox
)
from PyQt6.QtCore import Qt


class SessionCoachWindow(QWidget):
    def __init__(self, session, athlete_data, viewer_data):
        super().__init__()
        self.session = session
        self.athlete_data = athlete_data
        self.viewer_data = viewer_data
        self.setWindowTitle("Занятие")
        self.setMinimumSize(680, 560)
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
        layout = QVBoxLayout(container)
        layout.setContentsMargins(52, 36, 52, 36)
        layout.setSpacing(12)

        # Title
        date_str = str(self.session.date)
        time_str = str(self.session.time) if self.session.time else ""
        title_str = f"Занятие: {date_str}" + (f", {time_str}" if time_str else "")
        title = QLabel(title_str)
        title.setStyleSheet("font-size: 36px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(title)
        layout.addSpacing(12)

        def info_row(label, value):
            row = QHBoxLayout()
            lbl = QLabel(f"{label}:")
            lbl.setStyleSheet("font-size: 20px; font-weight: bold;")
            val = QLabel(str(value))
            val.setStyleSheet("font-size: 20px; color: #777;")
            row.addWidget(lbl)
            row.addSpacing(6)
            row.addWidget(val)
            row.addStretch()
            return row

        layout.addLayout(info_row("Тип занятия", self.session.activity_type))
        layout.addLayout(info_row("Длительность", f"{self.session.duration} мин"))

        # Status badge
        status_lbl = QLabel(self.session.status)
        status_lbl.setStyleSheet("""
            QLabel { border: 1.5px solid #1a1a1a; border-radius: 16px;
                padding: 6px 18px; font-size: 20px; color: #1a1a1a; }
        """)
        layout.addWidget(status_lbl)
        layout.addSpacing(16)

        # Buttons for coach
        role = self.viewer_data.get('role', '')
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        if role == 'тренер':
            edit_btn = QPushButton("Редактировать")
            edit_btn.setFixedHeight(52)
            edit_btn.clicked.connect(self._edit_session)
            btn_row.addWidget(edit_btn)

            del_btn = QPushButton("Удалить")
            del_btn.setFixedHeight(52)
            del_btn.clicked.connect(self._delete_session)
            btn_row.addWidget(del_btn)

        add_rec_btn = QPushButton("Добавить рекомендацию")
        add_rec_btn.setFixedHeight(52)
        add_rec_btn.clicked.connect(self._add_recommendation)
        btn_row.addWidget(add_rec_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)
        layout.addSpacing(16)

        # Existing recommendations
        from core.operations import get_session_recommendations
        ok, msg, recs = get_session_recommendations(self.session.id)
        if ok and recs:
            for rec in recs:
                rec_title = QLabel(f"Рекомендации тренера ({rec['author_fio']})")
                rec_title.setStyleSheet("font-size: 20px; font-weight: bold; margin-top: 8px;")
                rec_title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
                layout.addWidget(rec_title)

                rec_box = QTextEdit()
                rec_box.setPlainText(rec['text'])
                rec_box.setReadOnly(True)
                rec_box.setFixedHeight(90)
                rec_box.setStyleSheet("""
                    QTextEdit { border: 1px solid #e0e0e0; border-radius: 10px;
                        background: #f9f9f9; padding: 8px; font-size: 20px; color: #444; }
                """)
                layout.addWidget(rec_box)

        layout.addStretch()

    def _add_recommendation(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Добавить рекомендацию")
        dlg.setFixedSize(500, 280)
        v = DVL(dlg)
        lbl = QLabel("Рекомендация:")
        lbl.setStyleSheet("font-size: 20px;")
        v.addWidget(lbl)
        te = QTextEdit()
        te.setFixedHeight(120)
        v.addWidget(te)
        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(dlg.accept)
        btns.rejected.connect(dlg.reject)
        v.addWidget(btns)
        if dlg.exec():
            text = te.toPlainText().strip()
            if text:
                from core.operations import add_recommendation
                ok, msg, _ = add_recommendation(
                    self.viewer_data['id'], self.athlete_data['id'],
                    'session', self.session.id, text
                )
                if not ok:
                    QMessageBox.warning(self, "Ошибка", msg)
                else:
                    self.close()
                    self.__init__(self.session, self.athlete_data, self.viewer_data)
                    self.show()

    def _edit_session(self):
        from ui.session_add_window import SessionAddWindow
        plan_mock = type('Plan', (), {'id': self.session.plan_id})()
        self.edit_win = SessionAddWindow(plan_mock, session=self.session,
                                          on_saved=lambda: (self.close(),))
        self.edit_win.show()

    def _delete_session(self):
        reply = QMessageBox.question(self, "Удалить занятие", "Удалить это занятие?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            from core.operations import delete_session
            ok, msg, _ = delete_session(self.session.id, self.viewer_data['id'])
            if ok:
                self.close()
            else:
                QMessageBox.warning(self, "Ошибка", msg)
