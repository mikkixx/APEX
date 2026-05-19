from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QWidget, QComboBox, QFrame,
    QMessageBox, QDateEdit, QTextEdit
)
from PyQt6.QtCore import Qt, QDate
from ui.base_window import BaseWindow

PER_PAGE = 1

class MedicalWindow(BaseWindow):
    active_tab = "medical"

    def __init__(self, user_data):
        super().__init__(user_data)
        self.page = 1
        self.exam_type_filter = None
        self.exam_date = None
        self._load()

    def _load(self):
        layout = self._content_layout

        title = QLabel("МЕДКАРТА")
        title.setStyleSheet("font-size: 48px; font-weight: bold; letter-spacing: 1px;")
        title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(title)
        layout.addSpacing(12)

        # === FILTER PANEL ===
        filter_card = QFrame()
        filter_card.setStyleSheet("""
            QFrame { border: none; border-radius: 18px; background: #fafafa; }
            QLabel, QDateEdit, QComboBox, QPushButton { font-size: 20px; }
        """)
        filter_layout_outer = QVBoxLayout(filter_card)
        filter_layout_outer.setContentsMargins(20, 14, 20, 14)

        filter_row = QHBoxLayout()
        filter_lbl = QLabel("Фильтрация")
        filter_lbl.setStyleSheet("font-size: 20px; font-weight: bold;")
        filter_row.addWidget(filter_lbl)
        filter_row.addStretch()

        filter_row.addWidget(QLabel("Дата:"))
        self.date_filter = QDateEdit(calendarPopup=True)
        self.date_filter.setFixedSize(160, 50)
        self.date_filter.setDate(QDate.currentDate())
        self.exam_date = QDate.currentDate().toPyDate()
        filter_row.addWidget(self.date_filter)
        filter_row.addSpacing(10)

        # Combo Box for Exam Types
        self.type_combo = QComboBox()
        self.type_combo.setFixedWidth(240)
        self.type_combo.addItem("Все типы")
        self.type_combo.setEnabled(False)

        apply_btn = QPushButton("Применить")
        apply_btn.setFixedWidth(150)
        apply_btn.clicked.connect(self._apply_filter)

        filter_row.addWidget(self.type_combo)
        filter_row.addWidget(apply_btn)
        filter_layout_outer.addLayout(filter_row)

        # Scroll Area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_layout.setSpacing(12)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_area.setWidget(self.scroll_widget)
        filter_layout_outer.addWidget(self.scroll_area)

        # Pagination
        page_row = QHBoxLayout()
        page_row.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.prev_btn = QPushButton("←")
        self.prev_btn.setFixedWidth(24)
        self.prev_btn.setStyleSheet("QPushButton { background: transparent; color: #1a1a1a; border: none; font-size: 18px; } ")
        self.prev_btn.clicked.connect(self._prev_page)
        self.page_label = QLabel("1 страница из 1")
        self.page_label.setStyleSheet("font-size: 20px; ")
        self.next_btn = QPushButton("→")
        self.next_btn.setFixedWidth(24)
        self.next_btn.setStyleSheet("QPushButton { background: transparent; color: #1a1a1a; border: none; font-size: 18px; } ")
        self.next_btn.clicked.connect(self._next_page)
        page_row.addWidget(self.prev_btn)
        page_row.addWidget(self.page_label)
        page_row.addWidget(self.next_btn)
        filter_layout_outer.addLayout(page_row)

        layout.addWidget(filter_card)

        # ✅ Сначала грузим данные, потом заполняем фильтры
        self._refresh()

    def _load_exam_types_from_exams(self, exams):
        """Заполняет комбобокс типами осмотров из уже загруженных данных"""
        self.type_combo.clear()
        self.type_combo.addItem("Все типы")
        
        if exams:
            unique_types = sorted(set(
                e.get('exam_type', '').strip() for e in exams 
                if e.get('exam_type') and e['exam_type'].strip()
            ))
            for t in unique_types:
                self.type_combo.addItem(t)
            self.type_combo.setEnabled(True)
        else:
            self.type_combo.addItem("Типы не найдены")
            self.type_combo.setEnabled(False)

    def _apply_filter(self):
        self.page = 1
        self.exam_date = self.date_filter.date().toPyDate()
        
        t = self.type_combo.currentText()
        self.exam_type_filter = t if t not in ("Все типы", "Типы не найдены", "Загрузка...", "Ошибка загрузки") else None
        self._refresh()

    def _refresh(self):
        from core.operations import get_medical_data
        
        ok, msg, exams = get_medical_data(
            self.user_data['id'], 
            exam_date=self.exam_date,
            exam_type=self.exam_type_filter
        )

        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not ok:
            QMessageBox.warning(self, "Ошибка", msg)
            return

        self._all_exams = exams or []
        total = len(self._all_exams)

        if total == 0:
            empty = QLabel("Медицинских осмотров не найдено.")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setStyleSheet("color: #888; font-size: 20px; margin: 20px;")
            self.scroll_layout.addWidget(empty)
            self.page_label.setText("0 страниц")
            # ✅ Очищаем фильтры если нет данных
            self.type_combo.clear()
            self.type_combo.addItem("Все типы")
            return

        # ✅ Заполняем фильтры из реальных данных (без отдельного запроса)
        self._load_exam_types_from_exams(self._all_exams)

        idx = min(self.page - 1, total - 1)
        exam = self._all_exams[idx]
        self._render_exam(exam)

        self.page_label.setText(f"{self.page} страница из {total}")
        self.prev_btn.setEnabled(self.page > 1)
        self.next_btn.setEnabled(self.page < total)

    def _render_exam(self, exam):
        exam_card = QFrame()
        exam_card.setStyleSheet("QFrame { background: white; border: 1px solid #e0e0e0; border-radius: 16px; }")
        cl = QVBoxLayout(exam_card)
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

        metrics_title = QLabel("Показатели")
        metrics_title.setStyleSheet("font-size: 20px; font-weight: bold; margin-top: 8px;")
        metrics_title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        cl.addWidget(metrics_title)

        for m in exam.get('metrics', []):
            display = f"{m['value']} {m['unit']}"
            if m.get('is_critical'):
                display += " (критично)"
            cl.addLayout(row(m['type'], display, critical=m.get('is_critical', False)))

        recs = exam.get('recommendations', [])
        if recs:
            rec_title = QLabel("Рекомендации врача")
            rec_title.setStyleSheet("font-size: 20px; font-weight: bold; margin-top: 10px;")
            rec_title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            cl.addWidget(rec_title)
            for rec in recs:
                rec_box = QTextEdit()
                rec_box.setPlainText(rec.text if hasattr(rec, 'text') else str(rec))
                rec_box.setReadOnly(True)
                rec_box.setFixedHeight(80)
                rec_box.setStyleSheet("""
                    QTextEdit { border: 1px solid #e0e0e0; border-radius: 10px;
                        background: #f9f9f9; padding: 8px; font-size: 20px; color: #444; }
                """)
                cl.addWidget(rec_box)

        self.scroll_layout.addWidget(exam_card)

    def _prev_page(self):
        if self.page > 1:
            self.page -= 1
            self._refresh()

    def _next_page(self):
        self.page += 1
        self._refresh()