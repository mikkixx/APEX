from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QTextEdit, QMessageBox,
    QDialog, QDialogButtonBox
)
from PyQt6.QtCore import Qt


class DiaryDetailSpecialistWindow(QWidget):
    """Diary entry detail view for coach or doctor — read-only with add recommendation."""

    def __init__(self, entry, viewer_data, on_close=None):
        super().__init__()
        self.entry = entry
        self.viewer_data = viewer_data
        self.on_close = on_close
        self.setWindowTitle("Запись дневника")
        self.setMinimumSize(660, 600)
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

        # Title
        date_row = QHBoxLayout()
        date_row.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        d_lbl = QLabel("Дата:")
        d_lbl.setStyleSheet("font-size: 32px; font-weight: bold;")
        d_val = QLabel(str(self.entry.date))
        d_val.setStyleSheet("font-size: 32px; color: #888;")
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
        layout.addLayout(info_row("Комментарий", self.entry.comment or "—"))
        layout.addSpacing(16)

        # Add recommendation button
        add_rec_btn = QPushButton("Добавить рекомендацию")
        add_rec_btn.setFixedHeight(52)
        add_rec_btn.clicked.connect(self._add_recommendation)
        layout.addWidget(add_rec_btn)
        layout.addSpacing(12)

        # Existing recommendations
        from core.operations import get_recommendations_for_entry
        ok, msg, recs = get_recommendations_for_entry(self.entry.id)
        if ok and recs:
            for rec in recs:
                rec_title = QLabel(f"Рекомендации специалиста ({rec['author_fio']}, {rec['author_role']})")
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
        v = QVBoxLayout(dlg)
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
                    self.viewer_data['id'],
                    self.entry.athlete_id,
                    'training_diary',
                    self.entry.id,
                    text
                )
                if not ok:
                    QMessageBox.warning(self, "Ошибка", msg)
                else:
                    self.close()
