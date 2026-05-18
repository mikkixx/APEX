from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QTextEdit, QMessageBox
)
from PyQt6.QtCore import Qt


class DiaryDetailWindow(QWidget):
    def __init__(self, entry, user_data, on_close=None):
        super().__init__()
        self.entry = entry
        self.user_data = user_data
        self.on_close = on_close
        self.setWindowTitle("Запись дневника")
        self.setMinimumSize(640, 550)
        self._build()

    def closeEvent(self, event):
        if self.on_close:
            self.on_close()
        super().closeEvent(event)

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
        layout.setSpacing(10)

        # Date title
        date_row = QHBoxLayout()
        date_row.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        d_lbl = QLabel("Дата:")
        d_lbl.setStyleSheet("font-size: 24px; font-weight: bold;")
        d_val = QLabel(str(self.entry.date))
        d_val.setStyleSheet("font-size: 24px; color: #888;")
        date_row.addWidget(d_lbl)
        date_row.addSpacing(6)
        date_row.addWidget(d_val)
        layout.addLayout(date_row)
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

        layout.addLayout(info_row("Тип занятия", self.entry.activity_type))
        layout.addLayout(info_row("Длительность", f"{self.entry.duration} мин"))
        layout.addLayout(info_row("Количество шагов", self.entry.steps))
        layout.addLayout(info_row("Качество сна", f"{self.entry.sleep_hours} ч"))
        layout.addLayout(info_row("Усталость", f"{self.entry.fatigue} / 10"))
        layout.addLayout(info_row("Настроение", f"{self.entry.mood} / 10"))
        layout.addLayout(info_row("Комментарий", self.entry.comment or "Комментарий отсутствует"))
        layout.addSpacing(16)

        # Athlete can edit/delete their own entries
        if self.user_data['role'] == 'спортсмен':
            btn_row = QHBoxLayout()
            edit_btn = QPushButton("Редактировать")
            edit_btn.clicked.connect(self._edit)
            del_btn = QPushButton("Удалить")
            del_btn.setStyleSheet("""
                QPushButton { background: #1a1a1a; color: white; border-radius: 20px; padding: 10px 24px; }
            """)
            del_btn.clicked.connect(self._delete)
            btn_row.addWidget(edit_btn)
            btn_row.addSpacing(10)
            btn_row.addWidget(del_btn)
            btn_row.addStretch()
            layout.addLayout(btn_row)
            layout.addSpacing(16)

        # Specialist recommendations
        from core.operations import get_recommendations_for_entry
        ok, msg, recs = get_recommendations_for_entry(self.entry.id)

        if ok and recs:
            for rec in recs:
                spec_title = QLabel(f"Рекомендации специалиста ({rec['author_fio']}, {rec['author_role']})")
                spec_title.setStyleSheet("font-size: 20px; font-weight: bold; margin-top: 10px;")
                spec_title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
                layout.addWidget(spec_title)

                rec_box = QTextEdit()
                rec_box.setPlainText(rec['text'])
                rec_box.setReadOnly(True)
                rec_box.setFixedHeight(80)
                rec_box.setStyleSheet("""
                    QTextEdit { border: 1px solid #e0e0e0; border-radius: 20px;
                        background: #f9f9f9; padding: 8px; font-size: 20px; color: #444; }
                """)
                layout.addWidget(rec_box)
        else:
            no_rec = QLabel("Рекомендации специалиста отсутствуют.")
            no_rec.setStyleSheet("color: #aaa; font-size: 20px;")
            no_rec.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            layout.addWidget(no_rec)

        layout.addStretch()

    def _edit(self):
        from ui.diary_add_window import DiaryAddWindow
        self.edit_win = DiaryAddWindow(
            self.user_data['id'],
            entry=self.entry,
            on_saved=lambda: (self.on_close and self.on_close(), self.close())
        )
        self.edit_win.show()

    def _delete(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("Подтверждение")
        msg.setText("Удалить эту запись?")
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        msg.setStyleSheet("font-family: 'Alegreya'; font-size: 20px;")
        
        msg.button(QMessageBox.StandardButton.Yes).setText("Да")
        msg.button(QMessageBox.StandardButton.No).setText("Нет")
        
        reply = msg.exec()
        
        if reply == QMessageBox.StandardButton.Yes:
            from core.operations import delete_diary_entry
            ok, msg_text, _ = delete_diary_entry(self.entry.id, self.user_data['id'])
            if ok:
                self.close()
            else:
                QMessageBox.warning(self, "Ошибка", msg_text)
