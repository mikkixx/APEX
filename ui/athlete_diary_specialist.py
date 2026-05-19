from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QWidget, QFrame, QComboBox,
    QDateEdit, QMessageBox, QTextEdit, QDialog,
    QDialogButtonBox
)
from PyQt6.QtCore import Qt, QDate

PER_PAGE = 3


class AthleteDiarySpecialist:
    """Diary view for coach or doctor inside athlete profile."""
    def __init__(self, specialist_data, athlete_data, layout):
        self.specialist_data = specialist_data
        self.athlete_data = athlete_data
        self.layout = layout
        self.page = 1
        self.start_date = None
        self.end_date = None
        self.activity_filter = None

    def build(self):
        layout = self.layout

        title = QLabel("ДНЕВНИК НАГРУЗОК")
        title.setStyleSheet("font-size: 48px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(title)
        layout.addSpacing(12)

        filter_card = QFrame()
        filter_card.setStyleSheet("QFrame { border: 1px solid #e0e0e0; border-radius: 20px; background: #fafafa; }")
        fc = QVBoxLayout(filter_card)
        fc.setContentsMargins(24, 16, 24, 16)
        fc.setSpacing(12)

        filter_row = QHBoxLayout()
        flbl = QLabel("Фильтрация  ⛉")
        flbl.setStyleSheet("font-size: 20px; font-weight: bold;")
        filter_row.addWidget(flbl)
        filter_row.addStretch()

        filter_row.addWidget(QLabel("С:"))
        self.date_start = QDateEdit(calendarPopup=True)
        self.date_start.setFixedHeight(48)
        self.date_start.setDate(QDate.currentDate().addDays(-7))
        filter_row.addWidget(self.date_start)
        filter_row.addSpacing(8)
        filter_row.addWidget(QLabel("По:"))
        self.date_end = QDateEdit(calendarPopup=True)
        self.date_end.setFixedHeight(48)
        self.date_end.setDate(QDate.currentDate())
        filter_row.addWidget(self.date_end)
        filter_row.addSpacing(8)

        self.act_combo = QComboBox()
        self.act_combo.setFixedHeight(48)
        self.act_combo.addItems(["Тип занятия", "бег", "велосипед", "плавание", "силовая", "растяжка", "другое"])
        filter_row.addWidget(self.act_combo)

        apply_btn = QPushButton("Применить")
        apply_btn.setFixedHeight(48)
        apply_btn.setFixedWidth(160)
        apply_btn.clicked.connect(self._apply)
        filter_row.addWidget(apply_btn)
        fc.addLayout(filter_row)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_layout.setSpacing(10)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_area.setWidget(self.scroll_widget)
        fc.addWidget(self.scroll_area)

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
        fc.addLayout(page_row)

        layout.addWidget(filter_card)
        self._refresh()

    def _apply(self):
        self.page = 1
        self.start_date = self.date_start.date().toPyDate()
        self.end_date = self.date_end.date().toPyDate()
        a = self.act_combo.currentText()
        self.activity_filter = a if a != "Тип занятия" else None
        self._refresh()

    def _refresh(self):
        from core.operations import get_diary_entries
        ok, msg, data = get_diary_entries(
            self.athlete_data['id'],
            start_date=self.start_date,
            end_date=self.end_date,
            page=self.page,
            per_page=PER_PAGE,
            activity_type=self.activity_filter
        )

        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        entries = data.get('entries', []) if ok else []
        total = data.get('total', 0) if ok else 0
        total_pages = max(1, (total + PER_PAGE - 1) // PER_PAGE)

        if not entries:
            empty = QLabel("Записей не найдено.")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setStyleSheet("color: #888; font-size: 20px;")
            self.scroll_layout.addWidget(empty)
        else:
            for entry in entries:
                date_lbl = QLabel(f"Дата: <span style='color:#888'>{entry.date}</span>")
                date_lbl.setStyleSheet("font-size: 20px; font-weight: bold;")
                self.scroll_layout.addWidget(date_lbl)
                card = self._entry_card(entry)
                self.scroll_layout.addWidget(card)

        self.page_label.setText(f"{self.page} страница из {total_pages}")
        self.prev_btn.setEnabled(self.page > 1)
        self.next_btn.setEnabled(self.page < total_pages)

    def _entry_card(self, entry):
        card = QFrame()
        card.setStyleSheet("QFrame { background: white; border: 1px solid #e0e0e0; border-radius: 16px; }")
        cl = QVBoxLayout(card)
        cl.setContentsMargins(20, 14, 20, 14)
        cl.setSpacing(4)

        def row(lbl, val):
            r = QHBoxLayout()
            l = QLabel(f"{lbl}:")
            l.setStyleSheet("font-weight: bold; font-size: 20px;")
            v = QLabel(str(val))
            v.setStyleSheet("font-size: 20px; color: #777;")
            r.addWidget(l); r.addSpacing(4); r.addWidget(v); r.addStretch()
            return r

        cl.addLayout(row("Тип занятия", entry.activity_type))
        cl.addLayout(row("Длительность", f"{entry.duration} мин"))
        cl.addLayout(row("Количество шагов", entry.steps))
        cl.addLayout(row("Качество сна", f"{entry.sleep_hours} ч"))

        detail_btn = QPushButton("Подробнее")
        detail_btn.setStyleSheet("QPushButton { background: #1a1a1a; color: white; border-radius: 16px; padding: 8px 24px; font-size: 20px; }")
        detail_btn.clicked.connect(lambda: self._open_detail(entry))
        br = QHBoxLayout()
        br.addWidget(detail_btn)
        br.addStretch()
        cl.addLayout(br)
        return card

    def _open_detail(self, entry):
        from ui.diary_detail_specialist_window import DiaryDetailSpecialistWindow
        self.detail_win = DiaryDetailSpecialistWindow(self.specialist_data, self.athlete_data, entry, on_close=self._refresh)
        self.detail_win.show()

    def _prev(self):
        if self.page > 1:
            self.page -= 1
            self._refresh()

    def _next(self):
        self.page += 1
        self._refresh()
