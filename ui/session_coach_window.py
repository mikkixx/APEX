from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSpinBox, QDateEdit, QTimeEdit, QLineEdit, QMessageBox, QScrollArea, QTextEdit, QDialog
)
from PyQt6.QtCore import Qt 
from PyQt6.QtGui import QFont
from core.operations import edit_session, delete_session, add_recommendation_to_session, get_session_recommendations

class SessionCoachWindow(QWidget):
    def __init__(self, specialist_data, athlete_data, session, on_close=None):
        super().__init__()
        self.specialist_data = specialist_data
        self.athlete_data = athlete_data
        self.session = session
        self.on_close = on_close
        self.is_editing = False
        self.setWindowTitle("Занятие")
        self.setMinimumSize(520, 550)
        self._build()

    def _get(self, key, default=None):
        if isinstance(self.session, dict):
            return self.session.get(key, default)
        return getattr(self.session, key, default)

    def _build(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        main_layout.addWidget(scroll)

        self.container = QWidget()
        scroll.setWidget(self.container)
        self.container.setStyleSheet("""
            QLabel, QLineEdit, QDateEdit, QTimeEdit, QSpinBox, QPushButton, QTextEdit {
                font-size: 20px;
            }
        """)

        self.stack_layout = QVBoxLayout(self.container)
        self.stack_layout.setContentsMargins(48, 32, 48, 32)
        self.stack_layout.setSpacing(14)

        self.view_widget = QWidget()
        self._build_view()
        self.stack_layout.addWidget(self.view_widget)

        self.edit_widget = QWidget()
        self._build_edit()
        self.edit_widget.hide()
        self.stack_layout.addWidget(self.edit_widget)

        self.stack_layout.addStretch()

    def _build_view(self):
        layout = QVBoxLayout(self.view_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        title = QLabel("Детали занятия")
        title.setStyleSheet("font-size: 28px; font-weight: bold; border: none; background: transparent;")
        layout.addWidget(title)
        layout.addSpacing(8)

        def info_row(label, value):
            row = QHBoxLayout()
            lbl = QLabel(f"{label}:")
            lbl.setStyleSheet("font-weight: bold; font-size: 20px; border: none; background: transparent;")
            val = QLabel(str(value) if value else "—")
            val.setStyleSheet("font-size: 20px; color: #777; border: none; background: transparent;")
            row.addWidget(lbl); row.addSpacing(6); row.addWidget(val); row.addStretch()
            return row

        layout.addLayout(info_row("Дата", self._get('date', '—')))
        layout.addLayout(info_row("Время", self._get('time', '—')))
        layout.addLayout(info_row("Тип занятия", self._get('activity_type', '—')))
        layout.addLayout(info_row("Длительность", f"{self._get('duration', 0)} мин"))

        status_val = self._get('status', 'запланировано')
        layout.addLayout(info_row("Статус", status_val.capitalize()))
        layout.addSpacing(16)

        rec_title = QLabel("Рекомендации:")
        rec_title.setStyleSheet("font-size: 22px; font-weight: bold; border: none; background: transparent;")
        layout.addWidget(rec_title)

        self.recs_layout = QVBoxLayout()
        self.recs_layout.setSpacing(10)
        self._load_recommendations()
        layout.addLayout(self.recs_layout)

        self.add_rec_btn = QPushButton("Добавить рекомендацию")
        self.add_rec_btn.setFixedHeight(52)
        self.add_rec_btn.setStyleSheet("""
            QPushButton { background: #1a1a1a; color: white; border-radius: 20px; font-weight: bold; }
            QPushButton:hover { background: #333; }
        """)
        self.add_rec_btn.clicked.connect(self._add_recommendation)
        layout.addWidget(self.add_rec_btn)

        if status_val != 'выполнено':
            self.add_rec_btn.hide()

        layout.addSpacing(16)

        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(12)

        self.edit_toggle_btn = QPushButton("Редактировать")
        self.edit_toggle_btn.setFixedHeight(52)
        self.edit_toggle_btn.setStyleSheet("""
            QPushButton { background: #1a1a1a; color: white; border-radius: 20px; font-weight: bold; }
            QPushButton:hover { background: #333; }
        """)
        self.edit_toggle_btn.clicked.connect(self._toggle_edit)
        btn_layout.addWidget(self.edit_toggle_btn)

        self.del_btn = QPushButton("Удалить занятие")
        self.del_btn.setFixedHeight(52)
        self.del_btn.setStyleSheet("""
            QPushButton { background: #1a1a1a; color: white; border-radius: 20px; font-weight: bold; }
            QPushButton:hover { background: #333; }
        """)
        self.del_btn.clicked.connect(self._delete_session)
        btn_layout.addWidget(self.del_btn)

        layout.addLayout(btn_layout)

    def _build_edit(self):
        layout = QVBoxLayout(self.edit_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        title = QLabel("Редактирование")
        title.setStyleSheet("font-size: 28px; font-weight: bold;")
        layout.addWidget(title)
        layout.addSpacing(8)

        layout.addWidget(QLabel("Тип занятия:"))
        self.edit_activity = QLineEdit()
        self.edit_activity.setPlaceholderText("Например: Бег, Силовая")
        self.edit_activity.setFixedHeight(52)
        self.edit_activity.setText(str(self._get('activity_type', '')))
        layout.addWidget(self.edit_activity)

        layout.addWidget(QLabel("Дата:"))
        self.edit_date = QDateEdit(calendarPopup=True)
        self.edit_date.setFixedHeight(52)
        d = self._get('date')
        if d: self.edit_date.setDate(d if hasattr(d, 'toPyDate') else d)
        layout.addWidget(self.edit_date)

        layout.addWidget(QLabel("Время (необязательно):"))
        self.edit_time = QTimeEdit()
        self.edit_time.setFixedHeight(52)
        t = self._get('time')
        if t: self.edit_time.setTime(t if hasattr(t, 'toPyTime') else t)
        layout.addWidget(self.edit_time)

        layout.addWidget(QLabel("Длительность (мин):"))
        self.edit_duration = QSpinBox()
        self.edit_duration.setRange(1, 300)
        self.edit_duration.setFixedHeight(52)
        self.edit_duration.setValue(int(self._get('duration', 0)))
        layout.addWidget(self.edit_duration)

        layout.addSpacing(20)

        save_btn = QPushButton("Сохранить")
        save_btn.setFixedHeight(56)
        save_btn.setStyleSheet("""
            QPushButton { background: #1a1a1a; color: white; border-radius: 20px; font-weight: bold; }
            QPushButton:hover { background: #333; }
        """)
        save_btn.clicked.connect(self._save_edits)
        layout.addWidget(save_btn)

        cancel_btn = QPushButton("Отмена")
        cancel_btn.setFixedHeight(52)
        cancel_btn.setStyleSheet("""
            QPushButton { background: #1a1a1a; color: white; border-radius: 20px; font-weight: bold; }
            QPushButton:hover { background: #333; }
        """)
        cancel_btn.clicked.connect(self._cancel_edit)
        layout.addWidget(cancel_btn)

    def _toggle_edit(self):
        self.is_editing = not self.is_editing
        if self.is_editing:
            self.view_widget.hide()
            self.edit_widget.show()
            self.setWindowTitle("Редактирование")
        else:
            self.edit_widget.hide()
            self.view_widget.show()
            self.setWindowTitle("Занятие")
            self.edit_activity.setText(str(self._get('activity_type', '')))
            d = self._get('date')
            if d: self.edit_date.setDate(d if hasattr(d, 'toPyDate') else d)
            t = self._get('time')
            if t: self.edit_time.setTime(t if hasattr(t, 'toPyTime') else t)
            self.edit_duration.setValue(int(self._get('duration', 0)))

    def _cancel_edit(self):
        self._toggle_edit()

    def _save_edits(self):
        ok, msg, _ = edit_session(
            self.specialist_data['id'],
            self._get('id'),
            self.edit_date.date().toPyDate(),
            self.edit_time.time().toPyTime(),
            self.edit_activity.text().strip(),
            self.edit_duration.value()
        )
        if ok:
            QMessageBox.information(self, "Успех", "Занятие обновлено.")
            if self.on_close: self.on_close()
            self.close()
        else:
            QMessageBox.warning(self, "Ошибка", msg)

    def _add_recommendation(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Добавить рекомендацию")
        dlg.setMinimumWidth(500)
        dlg.setFont(QFont("Alegreya", 20))

        v = QVBoxLayout(dlg)
        v.setContentsMargins(24, 20, 24, 24)
        v.setSpacing(12)

        lbl = QLabel("Текст рекомендации:")
        lbl.setStyleSheet("font-size: 20px; font-weight: bold;")
        v.addWidget(lbl)

        te = QTextEdit()
        te.setFixedHeight(120)
        te.setStyleSheet("""
            QTextEdit { border: 1.5px solid #cccccc; border-radius: 20px;
                padding: 8px 16px; font-size: 20px; background: #ffffff; }
        """)
        v.addWidget(te)

        btn_row = QHBoxLayout()
        btn_row.addStretch()

        cancel_btn = QPushButton("Отмена")
        cancel_btn.setFixedSize(140, 50)
        cancel_btn.setStyleSheet("""
            QPushButton { background: #1a1a1a; color: white;
                border-radius: 20px; font-size: 20px; font-weight: bold; }
            QPushButton:hover { background: #333; }
        """)

        save_btn = QPushButton("Сохранить")
        save_btn.setFixedSize(160, 50)
        save_btn.setStyleSheet("""
            QPushButton { background: #1a1a1a; color: white;
                border-radius: 20px; font-size: 20px; font-weight: bold; }
            QPushButton:hover { background: #333; }
        """)

        cancel_btn.clicked.connect(dlg.reject)
        save_btn.clicked.connect(dlg.accept)
        btn_row.addWidget(cancel_btn)
        btn_row.addSpacing(10)
        btn_row.addWidget(save_btn)
        v.addLayout(btn_row)

        if dlg.exec() == QDialog.DialogCode.Accepted:
            text = te.toPlainText().strip()
            if text:
                ok, msg, _ = add_recommendation_to_session(
                    self.specialist_data['id'],
                    self._get('id'),
                    text
                )
                if ok:
                    self._load_recommendations()  
                else:
                    QMessageBox.warning(self, "Ошибка", msg)

    def _load_recommendations(self):
        while self.recs_layout.count():
            item = self.recs_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
            
        ok, msg, recs = get_session_recommendations(self._get('id'))
        has_recs = bool(recs)

        if hasattr(self, 'add_rec_btn'):
            self.add_rec_btn.setVisible(not has_recs and self._get('status') == 'выполнено')

        if has_recs:
            for r in recs:
                box = QLabel(f"<b>{r['author_fio']} ({r['author_role']}):</b><br>{r['text']}")
                box.setStyleSheet("border: 1px solid #e0e0e0; border-radius: 20px; padding: 8px; background: #fafafa; font-size: 20px;")
                box.setWordWrap(True)
                self.recs_layout.addWidget(box)
        else:
            no_rec = QLabel("Рекомендаций нет.")
            no_rec.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_rec.setStyleSheet("border: 1px solid #e0e0e0; border-radius: 12px; padding: 8px; background: #fafafa; font-size: 20px; color: #888;")
            self.recs_layout.addWidget(no_rec)

    def _delete_session(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("Удалить занятие")
        msg.setText("Вы уверены?")
        msg.setFont(QFont("Alegreya", 20))
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.button(QMessageBox.StandardButton.Yes).setText("Удалить")
        msg.button(QMessageBox.StandardButton.No).setText("Отмена")
        if msg.exec() == QMessageBox.StandardButton.Yes:
            ok, err_msg, _ = delete_session(self.specialist_data['id'], self._get('id'))
            if ok:
                if self.on_close: self.on_close()
                self.close()
            else:
                QMessageBox.warning(self, "Ошибка", err_msg)