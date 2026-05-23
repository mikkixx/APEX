from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QWidget, QFrame, QComboBox,
    QTextEdit, QMessageBox, QDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from core.operations import get_athlete_medical_records, get_medical_filter_options

class AthleteMedicalDoctor:
    def __init__(self, specialist_data, athlete_data, layout):
        self.specialist_data = specialist_data
        self.athlete_data = athlete_data
        self.layout = layout
        self.page = 1
        self.exam_type_filter = None
        self._all_exams = []

    def build(self):
        layout = self.layout

        header_row = QHBoxLayout()
        new_exam_btn = QPushButton("Новый осмотр")
        new_exam_btn.setFixedHeight(50)
        new_exam_btn.setFixedWidth(180)
        new_exam_btn.setStyleSheet("""
            QPushButton { background: #1a1a1a; color: white; border-radius: 20px;
                font-size: 20px; font-weight: bold; padding: 0px; }
            QPushButton:hover { background: #333; }
        """)
        new_exam_btn.clicked.connect(self._new_exam)
        header_row.addWidget(new_exam_btn)
        header_row.addStretch()

        title = QLabel("МЕДИЦИНСКИЕ ПОКАЗАТЕЛИ")
        title.setStyleSheet("font-size: 48px; font-weight: bold; letter-spacing: 1px; border: none; background: transparent;")
        header_row.addWidget(title)
        header_row.addStretch()
        layout.addLayout(header_row)
        layout.addSpacing(16)

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

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_layout.setSpacing(12)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_area.setWidget(self.scroll_widget)
        oc.addWidget(self.scroll_area)

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
        
        self._load_exam_types()
        self._refresh()

    def _load_exam_types(self):
        current_selection = self.type_combo.currentText()

        ok, msg, types = get_medical_filter_options(self.athlete_data['id'])
        
        self.type_combo.clear()
        self.type_combo.addItem("Все типы")
        if ok and types:
            for t in types:
                self.type_combo.addItem(t)
            self.type_combo.setEnabled(True)
        else:
            self.type_combo.addItem("Типы не найдены")
            self.type_combo.setEnabled(False)

        idx = self.type_combo.findText(current_selection)
        self.type_combo.setCurrentIndex(idx if idx >= 0 else 0)

    def _apply(self):
        t = self.type_combo.currentText()
        self.exam_type_filter = t if t not in ("Все типы", "Типы не найдены") else None
        self.page = 1
        self._refresh()

    def _refresh(self):
        # Загружаем ВСЕ осмотры с бэкенда
        ok, msg, exams = get_athlete_medical_records(
            self.specialist_data['id'],
            self.athlete_data['id']
        )

        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not ok:
            empty = QLabel(f"Ошибка загрузки: {msg}")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setStyleSheet("color: #cc0000; font-size: 20px; margin: 20px; border: none; background: transparent;")
            self.scroll_layout.addWidget(empty)
            return

        self._all_exams = exams or []

        if self.exam_type_filter:
            self._exams = [e for e in self._all_exams if e.get('exam_type') == self.exam_type_filter]
        else:
            self._exams = self._all_exams

        total = len(self._exams)

        if not self._exams:
            empty = QLabel("Медосмотров не найдено.")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setStyleSheet("color: #888; font-size: 20px; margin: 20px; border: none; background: transparent;")
            self.scroll_layout.addWidget(empty)
        else:
            if self.page > total:
                self.page = total
            elif self.page < 1:
                self.page = 1
                
            idx = self.page - 1
            self._render(self._exams[idx])

        self._load_exam_types()

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
        title_lbl.setStyleSheet("font-size: 24px; font-weight: bold; border: none; background: transparent;")
        cl.addWidget(title_lbl)

        def row(label, value, critical=False):
            r = QHBoxLayout()
            lbl_color = "#cc0000" if critical else "#1a1a1a"
            val_color = "#cc0000" if critical else "#777"
            lbl = QLabel(f"{label}:")
            lbl.setStyleSheet(f"font-weight: bold; font-size: 20px; color: {lbl_color}; border: none; background: transparent;")
            val = QLabel(str(value))
            val.setStyleSheet(f"font-size: 20px; color: {val_color}; border: none; background: transparent;")
            r.addWidget(lbl); r.addSpacing(4); r.addWidget(val); r.addStretch()
            return r

        cl.addLayout(row("Тип осмотра", exam['exam_type']))
        cl.addLayout(row("Врач", f"{exam['doctor_fio']}, {exam['doctor_email']}"))

        mt = QLabel("Показатели")
        mt.setStyleSheet("font-size: 24px; font-weight: bold; margin-top: 8px; border: none; background: transparent;")
        mt.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        cl.addWidget(mt)

        for m in exam.get('metrics', []):
            ref = m.get('ref_range', '')
            display = f"{m['value']} {m['unit']}"
            if ref and ref != '—':
                display += f"  |  норма: {ref}"
            is_crit = bool(m.get('is_critical', False))
            if is_crit:
                display += "  ⚠ критично"
            cl.addLayout(row(m['type'], display, critical=is_crit))

        rec_title = QLabel("Рекомендации врача")
        rec_title.setStyleSheet("font-size: 24px; font-weight: bold; margin-top: 10px; border: none; background: transparent;")
        rec_title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        cl.addWidget(rec_title)

        recs = exam.get('recommendations', [])
        if recs:
            rec = recs[0]
            r_text = rec['text'] if isinstance(rec, dict) else rec.text
            rec_box = QTextEdit()
            rec_box.setPlainText(r_text)
            rec_box.setReadOnly(True)
            rec_box.setFixedHeight(80)
            rec_box.setStyleSheet("""
                QTextEdit {
                    border: 1px solid #e0e0e0;
                    border-radius: 20px;
                    background: #ffffff;
                    padding: 8px;
                    font-size: 20px;
                    color: #333;
                }
            """)
            cl.addWidget(rec_box)
        else:
            no_rec_box = QLabel("Рекомендаций нет.")
            no_rec_box.setAlignment(Qt.AlignmentFlag.AlignLeft)
            no_rec_box.setStyleSheet("""
                QLabel {
                    background: #ffffff;
                    border: 1px solid #e0e0e0;
                    border-radius: 20px;
                    padding: 8px;
                    font-size: 20px;
                    color: #888;
                }
            """)
            no_rec_box.setFixedHeight(80)
            cl.addWidget(no_rec_box)

        if not recs:
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
        from ui.exam_add_window import ExamAddWindow
        def on_exam_saved():
            self.page = 1
            self._refresh()

        self.new_exam_win = ExamAddWindow(
            self.athlete_data['id'],
            self.specialist_data['id'],
            on_saved=on_exam_saved
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
            QPushButton { background: #1a1a1a; color: white;
                border-radius: 20px; font-size: 20px; font-weight: bold; }
            QPushButton:hover { background: #333; }
        """)
        ok_btn = QPushButton("Сохранить")
        ok_btn.setFixedSize(160, 50)
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

        if dlg.exec() == QDialog.DialogCode.Accepted:
            text = te.toPlainText().strip()
            if text:
                from core.operations import add_medical_recommendation
                ok, msg, _ = add_medical_recommendation(
                    self.specialist_data['id'], 
                    exam['exam_id'], 
                    text
                )
                if ok:
                    QMessageBox.information(None, "Успех", "Рекомендация добавлена.")
                    self._refresh()
                else:
                    QMessageBox.warning(None, "Ошибка", msg)

    def _prev(self):
        if self.page > 1:
            self.page -= 1
            self._refresh()

    def _next(self):
        self.page += 1
        self._refresh()