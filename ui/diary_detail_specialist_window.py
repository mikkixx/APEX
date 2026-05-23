from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QTextEdit, QMessageBox,
    QDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from core.operations import add_diary_recommendation, get_recommendations_for_entry


class DiaryDetailSpecialistWindow(QWidget):
    def __init__(self, entry, viewer_data, on_close=None):
        super().__init__()
        self.entry = entry
        self.viewer_data = viewer_data
        self.on_close = on_close
        self.setWindowTitle("Запись дневника")
        self.setMinimumSize(660, 550)

        self.btn_trainer = None
        self.btn_doctor = None
        
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

        date_row = QHBoxLayout()
        date_row.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        d_lbl = QLabel("Дата:")
        d_lbl.setStyleSheet("font-size: 28px; font-weight: bold; border: none;")
        d_val = QLabel(str(self.entry.date))
        d_val.setStyleSheet("font-size: 28px; color: #888; border: none;")
        date_row.addWidget(d_lbl)
        date_row.addSpacing(6)
        date_row.addWidget(d_val)
        layout.addLayout(date_row)
        layout.addSpacing(12)

        def info_row(label, value):
            row = QHBoxLayout()
            lbl = QLabel(f"{label}:")
            lbl.setStyleSheet("font-size: 20px; font-weight: bold; border: none; background: transparent;")
            val = QLabel(str(value))
            val.setStyleSheet("font-size: 20px; color: #777; border: none; background: transparent;")
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

        role = self.viewer_data.get('role', '')
        btn_wrap = QHBoxLayout()
        btn_wrap.addStretch()
        btn_wrap.setSpacing(10)

        if role == 'тренер':
            self.btn_trainer = QPushButton("Добавить рекомендацию тренера")
            self.btn_trainer.setFixedHeight(52)
            self.btn_trainer.setStyleSheet("""
                QPushButton { background: #1a1a1a; color: white; border-radius: 20px;
                    font-size: 20px; font-weight: bold; padding: 0px 20px; }
                QPushButton:hover { background: #333; }
            """)
            self.btn_trainer.clicked.connect(lambda: self._add_recommendation('тренер'))
            btn_wrap.addWidget(self.btn_trainer)
            btn_wrap.addStretch()
        
        elif role == 'врач':
            self.btn_doctor = QPushButton("Добавить рекомендацию врача")
            self.btn_doctor.setFixedHeight(52)
            self.btn_doctor.setStyleSheet("""
                QPushButton { background: #1a1a1a; color: white; border-radius: 20px;
                    font-size: 20px; font-weight: bold; padding: 0px 20px; }
                QPushButton:hover { background: #333; }
            """)
            self.btn_doctor.clicked.connect(lambda: self._add_recommendation('врач'))
            btn_wrap.addWidget(self.btn_doctor)
            btn_wrap.addStretch()
            
        layout.addLayout(btn_wrap)
        layout.addSpacing(12)

        self.recs_layout = QVBoxLayout()
        self.recs_layout.setSpacing(12)
        layout.addLayout(self.recs_layout)

        layout.addStretch()

        self._refresh_recommendations()

    def _refresh_recommendations(self):
        while self.recs_layout.count():
            item = self.recs_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        ok, msg, recs = get_recommendations_for_entry(self.entry.id)
        
        has_trainer_rec = False
        has_doctor_rec = False

        if ok and recs:
            for rec in recs:
                author_role = rec.get('author_role', '')
                if 'тренер' in author_role.lower():
                    has_trainer_rec = True
                elif 'врач' in author_role.lower():
                    has_doctor_rec = True

                rec_title = QLabel(f"Рекомендации от {rec['author_fio']} ({rec['author_role']})")
                rec_title.setStyleSheet("font-size: 20px; font-weight: bold; margin-top: 8px; border: none;")
                rec_title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
                self.recs_layout.addWidget(rec_title)

                rec_box = QTextEdit()
                rec_box.setPlainText(rec['text'])
                rec_box.setReadOnly(True)
                rec_box.setFixedHeight(90)
                rec_box.setStyleSheet("""
                    QTextEdit { border: 1px solid #e0e0e0; border-radius: 20px;
                        background: #f9f9f9; padding: 8px; font-size: 20px; color: #444; }
                """)
                self.recs_layout.addWidget(rec_box)

        if self.btn_trainer:
            self.btn_trainer.setVisible(not has_trainer_rec)
            
        if self.btn_doctor:
            self.btn_doctor.setVisible(not has_doctor_rec)

    def _add_recommendation(self, role_type):
        dlg = QDialog(self)
        dlg.setWindowTitle(f"Добавить рекомендацию ({role_type})")
        dlg.setMinimumWidth(500)
        dlg.setFont(QFont("Alegreya", 20))

        v = QVBoxLayout(dlg)
        v.setContentsMargins(24, 20, 24, 24)
        v.setSpacing(12)

        lbl = QLabel(f"Текст рекомендации ({role_type}):")
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
        cancel_btn.setFixedSize(130, 50)
        cancel_btn.setStyleSheet("""
            QPushButton { background: #1a1a1a; color: white;
                border-radius: 20px; font-size: 20px; font-weight: bold; }
            QPushButton:hover { background: #333; }
        """)

        save_btn = QPushButton("Сохранить")
        save_btn.setFixedSize(150, 50)
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
                ok, msg, _ = add_diary_recommendation(
                    self.viewer_data['id'],
                    self.entry.id,
                    text
                )
                if ok:
                    QMessageBox.information(self, "Успех", f"Рекомендация ({role_type}) успешно добавлена.")
                    self._refresh_recommendations()
                else:
                    QMessageBox.warning(self, "Ошибка", msg)