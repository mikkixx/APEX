from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QWidget, QFrame, QComboBox, QTextEdit, QMessageBox
)
from PyQt6.QtCore import Qt

PER_PAGE = 1


class AthleteMedicalCoach:
    """Coach view: read-only medical card for athlete."""
    def __init__(self, specialist_data, athlete_data, layout):
        self.specialist_data = specialist_data
        self.athlete_data = athlete_data
        self.layout = layout
        self.page = 1
        self.exam_type_filter = None

    def build(self):
        layout = self.layout

        title = QLabel("МЕДИЦИНСКИЕ ПОКАЗАТЕЛИ")
        title.setStyleSheet("font-size: 48px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(title)
        layout.addSpacing(12)

        outer = QFrame()
        outer.setStyleSheet("QFrame { border: 1px solid #e0e0e0; border-radius: 20px; background: #fafafa; }")
        oc = QVBoxLayout(outer)
        oc.setContentsMargins(24, 20, 24, 20)
        oc.setSpacing(12)

        filter_row = QHBoxLayout()
        flbl = QLabel("Фильтрация  ⛉")
        flbl.setStyleSheet("font-size: 20px; font-weight: bold;")
        filter_row.addWidget(flbl)
        filter_row.addStretch()

        lbl_d = QLabel("Дата ∨")
        lbl_d.setStyleSheet("font-size: 20px;")
        filter_row.addWidget(lbl_d)
        filter_row.addSpacing(8)

        self.type_combo = QComboBox()
        self.type_combo.setFixedHeight(48)
        self.type_combo.addItems(["Тип осмотра", "общий", "кардиологический", "неврологический", "ортопедический"])
        filter_row.addWidget(self.type_combo)

        apply_btn = QPushButton("Применить")
        apply_btn.setFixedHeight(48)
        apply_btn.setFixedWidth(160)
        apply_btn.clicked.connect(self._apply)
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
        self.prev_btn.setFixedWidth(40)
        self.prev_btn.setStyleSheet("QPushButton { background: transparent; color: #1a1a1a; border: none; font-size: 22px; }")
        self.prev_btn.clicked.connect(self._prev)
        self.page_label = QLabel("1 страница из 1")
        self.page_label.setStyleSheet("font-size: 20px;")
        self.next_btn = QPushButton("→")
        self.next_btn.setFixedWidth(40)
        self.next_btn.setStyleSheet("QPushButton { background: transparent; color: #1a1a1a; border: none; font-size: 22px; }")
        self.next_btn.clicked.connect(self._next)
        page_row.addWidget(self.prev_btn)
        page_row.addWidget(self.page_label)
        page_row.addWidget(self.next_btn)
        oc.addLayout(page_row)
        layout.addWidget(outer)
        self._refresh()

    def _apply(self):
        t = self.type_combo.currentText()
        self.exam_type_filter = t if t != "Тип осмотра" else None
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
        total_pages = max(1, total)

        if not self._exams:
            empty = QLabel("Медосмотров не найдено.")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setStyleSheet("color: #888; font-size: 20px;")
            self.scroll_layout.addWidget(empty)
        else:
            idx = min(self.page - 1, len(self._exams) - 1)
            self._render(self._exams[idx], read_only=True)

        self.page_label.setText(f"{self.page} страница из {total_pages}")
        self.prev_btn.setEnabled(self.page > 1)
        self.next_btn.setEnabled(self.page < total_pages)

    def _render(self, exam, read_only=True):
        card = QFrame()
        card.setStyleSheet("QFrame { background: white; border: 1px solid #e0e0e0; border-radius: 16px; }")
        cl = QVBoxLayout(card)
        cl.setContentsMargins(20, 16, 20, 16)
        cl.setSpacing(8)

        title_lbl = QLabel(f"Медицинский осмотр ({exam['exam_date']})")
        title_lbl.setStyleSheet("font-size: 20px; font-weight: bold;")
        cl.addWidget(title_lbl)

        def row(label, value, critical=False):
            r = QHBoxLayout()
            c = "#cc0000" if critical else "#1a1a1a"
            vc = "#cc0000" if critical else "#777"
            lbl = QLabel(f"{label}:")
            lbl.setStyleSheet(f"font-weight: bold; font-size: 20px; color: {c};")
            val = QLabel(str(value))
            val.setStyleSheet(f"font-size: 20px; color: {vc};")
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

        self.scroll_layout.addWidget(card)

    def _prev(self):
        if self.page > 1:
            self.page -= 1
            self._refresh()

    def _next(self):
        self.page += 1
        self._refresh()
