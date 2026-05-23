from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QWidget, QFrame, QComboBox, QTextEdit
)
from PyQt6.QtCore import Qt
from core.operations import get_medical_data, get_medical_filter_options

class AthleteMedicalCoach:
    """Coach view: read-only medical card for athlete."""
    def __init__(self, specialist_data, athlete_data, layout, parent_widget=None):
        self.specialist_data = specialist_data
        self.athlete_data = athlete_data
        self.layout = layout
        self.parent = parent_widget
        self.page = 1
        self.exam_type_filter = None

    def build(self):
        layout = self.layout

        title = QLabel("МЕДИЦИНСКИЕ ПОКАЗАТЕЛИ")
        title.setStyleSheet("font-size: 48px; font-weight: bold; letter-spacing: 1px; border: none; background: transparent;")
        title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(title)
        layout.addSpacing(12)

        filter_card = QFrame()
        filter_card.setStyleSheet("""
            QFrame { border: none; border-radius: 18px; background: #fafafa; }
            QLabel, QDateEdit, QComboBox, QPushButton { font-size: 20px; }
        """)
        oc = QVBoxLayout(filter_card)
        oc.setContentsMargins(20, 14, 20, 14)
        oc.setSpacing(0)

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
        ok, msg, types = get_medical_filter_options(self.athlete_data['id'])
        if ok and types:
            self.type_combo.clear()
            self.type_combo.addItem("Все типы")
            for t in types:
                self.type_combo.addItem(t)
            self.type_combo.setEnabled(True)

    def _apply(self):
        t = self.type_combo.currentText()
        self.exam_type_filter = t if t != "Все типы" else None
        self.page = 1
        self._refresh()

    def _refresh(self):
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
            empty.setStyleSheet("color: #888; font-size: 20px; margin: 20px; border: none; background: transparent;")
            self.scroll_layout.addWidget(empty)
            self.page_label.setText("0 страниц")
        else:
            idx = min(self.page - 1, total - 1)
            self._render(self._exams[idx])
            self.page_label.setText(f"{self.page} страница из {total}")
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
            is_crit = bool(critical)
            lbl_color = "#cc0000" if is_crit else "#1a1a1a"
            val_color = "#cc0000" if is_crit else "#777"
            
            lbl = QLabel(f"{label}:")
            lbl.setStyleSheet(f"QLabel {{ font-weight: bold; font-size: 20px; color: {lbl_color}; border: none; background: transparent; }}")
            
            val = QLabel(str(value))
            val.setStyleSheet(f"QLabel {{ font-size: 20px; color: {val_color}; border: none; background: transparent; }}")
            
            r.addWidget(lbl); r.addSpacing(4); r.addWidget(val); r.addStretch()
            return r

        cl.addLayout(row("Тип осмотра", exam['exam_type']))
        cl.addLayout(row("Врач", f"{exam['doctor_fio']}, {exam['doctor_email']}"))

        mt = QLabel("Показатели")
        mt.setStyleSheet("font-size: 24px; font-weight: bold; margin-top: 8px; border: none; background: transparent;")
        mt.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        cl.addWidget(mt)

        for m in exam.get('metrics', []):
            display = f"{m['value']} {m['unit']}"
            is_crit = bool(m.get('is_critical', False))
            if is_crit:
                display += " (критично)"
            cl.addLayout(row(m['type'], display, critical=is_crit))

        # ✅ ЗАГОЛОВОК РЕКОМЕНДАЦИЙ (Всегда виден, 24px)
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
            # ✅ Та же рамка, белый фон, скругление 20px, текст слева
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

        self.scroll_layout.addWidget(card)


    def _prev(self):
        if self.page > 1:
            self.page -= 1
            self._refresh()

    def _next(self):
        self.page += 1
        self._refresh()