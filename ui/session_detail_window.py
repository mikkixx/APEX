from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QFrame, QTextEdit
)
from PyQt6.QtCore import Qt


class SessionDetailWindow(QWidget):
    def __init__(self, session, athlete_id):
        super().__init__()
        self.session = session
        self.athlete_id = athlete_id
        self.setWindowTitle("Подробнее о занятии")
        self.setMinimumSize(600, 500)
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
        layout.setContentsMargins(48, 36, 48, 36)
        layout.setSpacing(10)

        date_row = QHBoxLayout()
        date_lbl = QLabel("Дата:")
        date_lbl.setStyleSheet("font-size: 20px; font-weight: bold;")
        date_val = QLabel(str(self.session.date))
        date_val.setStyleSheet("font-size: 20px; color: #888;")
        date_row.addStretch()
        date_row.addWidget(date_lbl)
        date_row.addSpacing(6)
        date_row.addWidget(date_val)
        date_row.addStretch()
        layout.addLayout(date_row)
        layout.addSpacing(12)

        def info_row(label, value):
            row = QHBoxLayout()
            lbl = QLabel(f"{label}:")
            lbl.setStyleSheet("font-size: 15px; font-weight: bold;")
            val = QLabel(str(value))
            val.setStyleSheet("font-size: 15px; color: #777;")
            row.addWidget(lbl)
            row.addSpacing(6)
            row.addWidget(val)
            row.addStretch()
            return row

        layout.addLayout(info_row("Тип занятия", self.session.activity_type))
        layout.addLayout(info_row("Длительность", f"{self.session.duration} мин"))

        if self.session.time:
            layout.addLayout(info_row("Время", str(self.session.time)))

        layout.addLayout(info_row("Статус", self.session.status))
        layout.addSpacing(20)

        # Recommendations
        from core.operations import get_session_recommendations
        ok, msg, recs = get_session_recommendations(self.session.id)

        if ok and recs:
            for rec in recs:
                rec_title = QLabel(f"Рекомендации тренера ({rec['author_fio']})")
                rec_title.setStyleSheet("font-size: 15px; font-weight: bold; margin-top: 12px;")
                rec_title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
                layout.addWidget(rec_title)

                rec_box = QTextEdit()
                rec_box.setPlainText(rec['text'])
                rec_box.setReadOnly(True)
                rec_box.setFixedHeight(80)
                rec_box.setStyleSheet("""
                    QTextEdit { border: 1px solid #e0e0e0; border-radius: 10px;
                        background: #f9f9f9; padding: 8px; font-size: 14px; color: #444; }
                """)
                layout.addWidget(rec_box)
        else:
            no_rec = QLabel("Рекомендаций пока нет.")
            no_rec.setStyleSheet("color: #aaa; font-size: 14px;")
            no_rec.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            layout.addWidget(no_rec)

        layout.addStretch()
