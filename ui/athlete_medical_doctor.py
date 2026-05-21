from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QWidget, QFrame, QComboBox,
    QTextEdit, QMessageBox, QDialog, QDialogButtonBox,
    QLineEdit, QDoubleSpinBox, QDateEdit, QCheckBox
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont

PER_PAGE = 1


class AthleteMedicalDoctor:
    """Doctor view: medical card with full edit + add exam + add recommendation."""
    def __init__(self, specialist_data, athlete_data, layout):
        self.specialist_data = specialist_data
        self.athlete_data = athlete_data
        self.layout = layout
        self.page = 1
        self.exam_type_filter = None

    def build(self):
        layout = self.layout

        title = QLabel("МЕДИЦИНСКИЕ ПОКАЗАТЕЛИ")
        title.setStyleSheet("font-size: 48px; font-weight: bold; letter-spacing: 1px;")
        title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(title)
        layout.addSpacing(12)

        # Filter panel — эталонный стиль из medical_window
        filter_card = QFrame()
        filter_card.setStyleSheet("""
            QFrame { border: none; border-radius: 18px; background: #fafafa; }
            QLabel, QDateEdit, QComboBox, QPushButton { font-size: 20px; }
        """)
        oc = QVBoxLayout(filter_card)
        oc.setContentsMargins(20, 14, 20, 14)
        oc.setSpacing(8)

        filter_row = QHBoxLayout()
        filter_row.setSpacing(10)
        filter_lbl = QLabel("Фильтрация")
        filter_lbl.setStyleSheet("font-size: 20px; font-weight: bold;")
        filter_row.addWidget(filter_lbl)
        filter_row.addStretch()

        self.type_combo = QComboBox()
        self.type_combo.setFixedWidth(240)
        self.type_combo.addItem("Все типы")
        self.type_combo.setEnabled(False)

        apply_btn = QPushButton("Применить")
        apply_btn.setFixedWidth(150)
        apply_btn.clicked.connect(self._apply)
        filter_row.addWidget(self.type_combo)
        filter_row.addSpacing(10)
        filter_row.addWidget(apply_btn)
        oc.addLayout(filter_row)

        # Кнопка нового осмотра
        new_exam_btn = QPushButton("Новый осмотр")
        new_exam_btn.setFixedHeight(48)
        new_exam_btn.setFixedWidth(200)
        new_exam_btn.setStyleSheet("""
            QPushButton { background: #1a1a1a; color: white; border-radius: 20px;
                font-size: 20px; font-weight: bold; padding: 0px; }
            QPushButton:hover { background: #333; }
        """)
        new_exam_btn.clicked.connect(self._new_exam)
        oc.addWidget(new_exam_btn)

        # Scroll
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_layout.setSpacing(12)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_area.setWidget(self.scroll_widget)
        oc.addWidget(self.scroll_area)

        # Pagination
        page_row = QHBoxLayout()
        page_row.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.prev_btn = QPushButton("←")
        self.prev_btn.setFixedSize(44, 44)
        self.prev_btn.setStyleSheet("QPushButton { background: transparent; color: #1a1a1a; border: none; font-size: 24px; padding: 0px; } QPushButton:hover { color: #555; }")
        self.prev_btn.clicked.connect(self._prev)
        self.page_label = QLabel("1 страница из 1")
        self.page_label.setStyleSheet("font-size: 20px;")
        self.next_btn = QPushButton("→")
        self.next_btn.setFixedSize(44, 44)
        self.next_btn.setStyleSheet("QPushButton { background: transparent; color: #1a1a1a; border: none; font-size: 24px; padding: 0px; } QPushButton:hover { color: #555; }")
        self.next_btn.clicked.connect(self._next)
        page_row.addWidget(self.prev_btn)
        page_row.addWidget(self.page_label)
        page_row.addWidget(self.next_btn)
        oc.addLayout(page_row)

        layout.addWidget(filter_card)
        self._refresh()

    def _load_exam_types(self, exams):
        self.type_combo.clear()
        self.type_combo.addItem("Все типы")
        if exams:
            unique = sorted(set(
                e.get('exam_type', '').strip() for e in exams
                if e.get('exam_type') and e['exam_type'].strip()
            ))
            for t in unique:
                self.type_combo.addItem(t)
            self.type_combo.setEnabled(True)
        else:
            self.type_combo.addItem("Типы не найдены")
            self.type_combo.setEnabled(False)

    def _apply(self):
        t = self.type_combo.currentText()
        self.exam_type_filter = t if t not in ("Все типы", "Типы не найдены") else None
        self.page = 1
        self._refresh()

    def _refresh(self):
        from core.operations import get_medical_data
        ok, msg, exams = get_medical_data(self.athlete_data['id'], exam_type=self.exam_type_filter)

        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self._exams = exams or []
        total = len(self._exams)

        if not self._exams:
            empty = QLabel("Медосмотров не найдено.")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setStyleSheet("color: #888; font-size: 20px; margin: 20px;")
            self.scroll_layout.addWidget(empty)
            self.type_combo.clear()
            self.type_combo.addItem("Все типы")
        else:
            self._load_exam_types(self._exams)
            idx = min(self.page - 1, total - 1)
            self._render(self._exams[idx])

        self.page_label.setText(f"{self.page} страница из {max(1, total)}")
        self.prev_btn.setEnabled(self.page > 1)
        self.next_btn.setEnabled(self.page < total)

    def _render(self, exam):
        card = QFrame()
        card.setStyleSheet("QFrame { background: white; border: 1px solid #e0e0e0; border-radius: 20px; }")
        cl = QVBoxLayout(card)
        cl.setContentsMargins(20, 16, 20, 16)
        cl.setSpacing(6)

        title_lbl = QLabel(f"Медицинский осмотр ({exam['exam_date']})")
        title_lbl.setStyleSheet("font-size: 22px; font-weight: bold; margin-bottom: 4px;")
        cl.addWidget(title_lbl)

        def row(label, value, critical=False):
            r = QHBoxLayout()
            lbl_color = "#cc0000" if critical else "#1a1a1a"
            val_color = "#cc0000" if critical else "#777"
            lbl = QLabel(f"{label}:")
            lbl.setStyleSheet(f"font-weight: bold; font-size: 20px; color: {lbl_color};")
            val = QLabel(str(value))
            val.setStyleSheet(f"font-size: 20px; color: {val_color};")
            r.addWidget(lbl); r.addSpacing(4); r.addWidget(val); r.addStretch()
            return r

        cl.addLayout(row("Тип осмотра", exam['exam_type']))
        cl.addLayout(row("Врач", f"{exam['doctor_fio']}, {exam['doctor_email']}"))

        mt = QLabel("Показатели")
        mt.setStyleSheet("font-size: 20px; font-weight: bold; margin-top: 8px;")
        mt.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        cl.addWidget(mt)

        for m in exam.get('metrics', []):
            display = f"{m['value']} {m['unit']}"
            if m.get('is_critical'):
                display += " (критично)"
            cl.addLayout(row(m['type'], display, critical=m.get('is_critical', False)))

        add_rec_btn = QPushButton("Добавить рекомендацию")
        add_rec_btn.setFixedHeight(48)
        add_rec_btn.setFixedWidth(300)
        add_rec_btn.setStyleSheet("""
            QPushButton { background: #1a1a1a; color: white; border-radius: 20px;
                font-size: 20px; font-weight: bold; padding: 0px; }
            QPushButton:hover { background: #333; }
        """)
        add_rec_btn.clicked.connect(lambda: self._add_rec(exam))
        cl.addWidget(add_rec_btn)
        self.scroll_layout.addWidget(card)

    def _new_exam(self):
        from ui.new_exam_window import NewExamWindow
        self.new_exam_win = NewExamWindow(
            self.specialist_data['id'], self.athlete_data['id'], on_saved=self._refresh
        )
        self.new_exam_win.show()

    def _add_rec(self, exam):
        dlg = QDialog()
        dlg.setWindowTitle("Добавить рекомендацию")
        dlg.setMinimumWidth(520)
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
            QPushButton { background: transparent; color: #1a1a1a;
                border: 1.5px solid #1a1a1a; border-radius: 20px; font-size: 20px; }
            QPushButton:hover { background: #f0f0f0; }
        """)
        ok_btn = QPushButton("Сохранить")
        ok_btn.setFixedSize(140, 50)
        ok_btn.setStyleSheet("""
            QPushButton { background: #1a1a1a; color: white;
                border-radius: 20px; font-size: 20px; font-weight: bold; }
            QPushButton:hover { background: #333; }
        """)
        cancel_btn.clicked.connect(dlg.reject)
        ok_btn.clicked.connect(dlg.accept)
        btn_row.addWidget(cancel_btn)
        btn_row.addSpacing(10)
        btn_row.addWidget(ok_btn)
        v.addLayout(btn_row)

        if dlg.exec():
            text = te.toPlainText().strip()
            if text:
                from core.operations import add_recommendation
                ok, msg, _ = add_recommendation(
                    self.specialist_data['id'], self.athlete_data['id'],
                    'exam', exam['exam_id'], text
                )
                if ok:
                    self._show_popup("Успех", "Рекомендация добавлена.")
                    self._refresh()
                else:
                    self._show_popup("Ошибка", msg, error=True)

    def _show_popup(self, title, text, error=False):
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setIcon(QMessageBox.Icon.Critical if error else QMessageBox.Icon.Information)
        msg.setFont(QFont("Alegreya", 20))
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.button(QMessageBox.StandardButton.Ok).setText("Хорошо")
        msg.exec()

    def _prev(self):
        if self.page > 1:
            self.page -= 1
            self._refresh()

    def _next(self):
        self.page += 1
        self._refresh()
