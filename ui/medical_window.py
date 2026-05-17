from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QWidget, QComboBox, QFrame,
    QMessageBox, QDateEdit, QTextEdit
)
from PyQt6.QtCore import Qt, QDate
from ui.base_window import BaseWindow

PER_PAGE = 1  # one exam per page to match wireframe


class MedicalWindow(BaseWindow):
    active_tab = "medical"

    def __init__(self, user_data):
        super().__init__(user_data)
        self.page = 1
        self.exam_date_filter = None
        self.exam_type_filter = None
        self._all_exams = []
        self._load()

    def _load(self):
        layout = self._content_layout

        title = QLabel("МЕДКАРТА")
        title.setStyleSheet("font-size: 26px; font-weight: bold; letter-spacing: 1px;")
        title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(title)
        layout.addSpacing(12)

        # Main card
        outer = QFrame()
        outer.setStyleSheet("QFrame { border: 1px solid #e0e0e0; border-radius: 18px; background: #fafafa; }")
        outer_layout = QVBoxLayout(outer)
        outer_layout.setContentsMargins(24, 20, 24, 20)
        outer_layout.setSpacing(12)

        # Filter row
        filter_row = QHBoxLayout()
        filter_lbl = QLabel("Фильтрация")
        filter_lbl.setStyleSheet("font-weight: bold; font-size: 14px;")
        filter_row.addWidget(filter_lbl)
        filter_row.addStretch()

        self.date_filter = QDateEdit(calendarPopup=True)
        self.date_filter.setDate(QDate.currentDate())
        self.date_filter.setPrefix("Дата: ")
        self.date_filter.setSpecialValueText("Любая дата")

        self.type_combo = QComboBox()
        self.type_combo.setFixedWidth(180)
        self.type_combo.addItems(["Тип осмотра", "общий", "кардиологический", "неврологический", "ортопедический"])

        apply_btn = QPushButton("Применить")
        apply_btn.setFixedWidth(120)
        apply_btn.clicked.connect(self._apply_filter)

        filter_row.addWidget(self.date_filter)
        filter_row.addWidget(self.type_combo)
        filter_row.addWidget(apply_btn)
        outer_layout.addLayout(filter_row)

        # Scroll area for exam
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_layout.setSpacing(12)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_area.setWidget(self.scroll_widget)
        outer_layout.addWidget(self.scroll_area)

        # Pagination
        page_row = QHBoxLayout()
        page_row.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.prev_btn = QPushButton("←")
        self.prev_btn.setFixedWidth(36)
        self.prev_btn.setStyleSheet("QPushButton { background: transparent; color: #1a1a1a; border: none; font-size: 18px; }")
        self.prev_btn.clicked.connect(self._prev)
        self.page_label = QLabel("1 страница из 1")
        self.page_label.setStyleSheet("font-size: 14px;")
        self.next_btn = QPushButton("→")
        self.next_btn.setFixedWidth(36)
        self.next_btn.setStyleSheet("QPushButton { background: transparent; color: #1a1a1a; border: none; font-size: 18px; }")
        self.next_btn.clicked.connect(self._next)
        page_row.addWidget(self.prev_btn)
        page_row.addWidget(self.page_label)
        page_row.addWidget(self.next_btn)
        outer_layout.addLayout(page_row)

        layout.addWidget(outer)
        self._refresh()

    def _apply_filter(self):
        self.page = 1
        t = self.type_combo.currentText()
        self.exam_type_filter = t if t != "Тип осмотра" else None
        # Date filter - you can add more logic if needed
        self._refresh()

    def _refresh(self):
        from core.operations import get_medical_data
        ok, msg, exams = get_medical_data(
            self.user_data['id'],
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
        total_pages = max(1, total)  # one per page

        if not self._all_exams:
            empty = QLabel("Медицинских осмотров не найдено.")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setStyleSheet("color: #888; font-size: 14px; margin: 20px;")
            self.scroll_layout.addWidget(empty)
        else:
            idx = self.page - 1
            if idx >= len(self._all_exams):
                idx = len(self._all_exams) - 1
                self.page = idx + 1
            exam = self._all_exams[idx]
            self._render_exam(exam)

        self.page_label.setText(f"{self.page} страница из {total_pages}")
        self.prev_btn.setEnabled(self.page > 1)
        self.next_btn.setEnabled(self.page < total_pages)

    def _render_exam(self, exam):
        exam_card = QFrame()
        exam_card.setStyleSheet("QFrame { background: white; border: 1px solid #e0e0e0; border-radius: 14px; }")
        card_layout = QVBoxLayout(exam_card)
        card_layout.setContentsMargins(20, 16, 20, 16)
        card_layout.setSpacing(6)

        title_lbl = QLabel(f"Медицинский осмотр ({exam['exam_date']})")
        title_lbl.setStyleSheet("font-size: 15px; font-weight: bold; margin-bottom: 4px;")
        card_layout.addWidget(title_lbl)

        def row(label, value, critical=False):
            r = QHBoxLayout()
            lbl_color = "#cc0000" if critical else "#1a1a1a"
            val_color = "#cc0000" if critical else "#777"
            lbl = QLabel(f"{label}:")
            lbl.setStyleSheet(f"font-weight: bold; font-size: 14px; color: {lbl_color};")
            val = QLabel(str(value))
            val.setStyleSheet(f"font-size: 14px; color: {val_color};")
            r.addWidget(lbl)
            r.addSpacing(4)
            r.addWidget(val)
            r.addStretch()
            return r

        card_layout.addLayout(row("Тип осмотра", exam['exam_type']))
        card_layout.addLayout(row("Врач", f"{exam['doctor_fio']}, {exam['doctor_email']}"))

        metrics_title = QLabel("Показатели")
        metrics_title.setStyleSheet("font-size: 14px; font-weight: bold; margin-top: 8px;")
        metrics_title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        card_layout.addWidget(metrics_title)

        for metric in exam.get('metrics', []):
            display = f"{metric['value']} {metric['unit']}"
            if metric.get('is_critical'):
                display += " (критично)"
            card_layout.addLayout(row(metric['type'], display, critical=metric.get('is_critical', False)))

        # Doctor recommendations
        recs = exam.get('recommendations', [])
        if recs:
            rec_title = QLabel("Рекомендации врача")
            rec_title.setStyleSheet("font-size: 14px; font-weight: bold; margin-top: 10px;")
            rec_title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            card_layout.addWidget(rec_title)

            for rec in recs:
                rec_box = QTextEdit()
                rec_box.setPlainText(rec.text if hasattr(rec, 'text') else str(rec))
                rec_box.setReadOnly(True)
                rec_box.setFixedHeight(72)
                rec_box.setStyleSheet("""
                    QTextEdit { border: 1px solid #e0e0e0; border-radius: 10px;
                        background: #f9f9f9; padding: 8px; font-size: 14px; color: #444; }
                """)
                card_layout.addWidget(rec_box)

        self.scroll_layout.addWidget(exam_card)

    def _prev(self):
        if self.page > 1:
            self.page -= 1
            self._refresh()

    def _next(self):
        self.page += 1
        self._refresh()
