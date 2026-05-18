from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QWidget, QComboBox, QFrame,
    QMessageBox, QDateEdit, QDialog, QDialogButtonBox,
    QSpinBox, QDoubleSpinBox, QTextEdit, QLineEdit
)
from PyQt6.QtCore import Qt, QDate
from ui.base_window import BaseWindow

PER_PAGE = 3

class DiaryEntryCard(QFrame):
    def __init__(self, entry, on_detail):
        super().__init__()
        self.entry = entry
        # ✅ Задаём имя объекта для точного применения стилей
        self.setObjectName("DiaryEntryCard")
        self._build(on_detail)

    def _build(self, on_detail):
        self.setStyleSheet("""
            QFrame#DiaryEntryCard { 
                background: #fff; 
                border: 1px solid #e0e0e0; 
                border-radius: 20px; 
            }
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 14, 20, 14)
        layout.setSpacing(4)

        def row(lbl, val, gray=True):
            r = QHBoxLayout()
            l = QLabel(f"{lbl}: ")
            l.setStyleSheet("font-weight: bold; font-size: 20px; background: transparent;")
            v = QLabel(str(val))
            v.setStyleSheet(f"font-size: 20px; color: {'#777' if gray else '#1a1a1a'}; background: transparent;")
            r.addWidget(l)
            r.addSpacing(4)
            r.addWidget(v)
            r.addStretch()
            return r

        layout.addLayout(row("Тип занятия", self.entry.activity_type))
        layout.addLayout(row("Длительность", f"{self.entry.duration} мин"))
        layout.addLayout(row("Количество шагов", self.entry.steps))
        layout.addLayout(row("Качество сна", f"{self.entry.sleep_hours} ч"))

        btn_row = QHBoxLayout()
        detail_btn = QPushButton("Подробнее")
        detail_btn.setStyleSheet("""
            QPushButton { 
                background: #1a1a1a; 
                color: white; 
                border-radius: 20px;
                padding: 7px 18px; 
                font-size: 20px; 
            }
        """)
        detail_btn.clicked.connect(lambda: on_detail(self.entry))
        btn_row.addWidget(detail_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)


class DiaryWindow(BaseWindow):
    active_tab = "diary"
    def __init__(self, user_data):
        super().__init__(user_data)
        self.page = 1
        self.start_date = None
        self.end_date = None
        self.activity_filter = None
        self._load()

    def _load(self):
        layout = self._content_layout

        # Header
        header_row = QHBoxLayout()
        add_btn = QPushButton("Добавить запись")
        add_btn.setFixedWidth(228)
        add_btn.clicked.connect(self._add_entry)
        header_row.addWidget(add_btn)
        header_row.addStretch()
        title = QLabel("ДНЕВНИК НАГРУЗОК")
        title.setStyleSheet("font-size: 48px; font-weight: bold; letter-spacing: 1px; ")
        header_row.addWidget(title)
        header_row.addStretch()
        layout.addLayout(header_row)
        layout.addSpacing(12)

        # Filter panel
        filter_card = QFrame()
        filter_card.setStyleSheet("""
            QFrame { border: none; border-radius: 18px; background: #fafafa; }
            QLabel, QDateEdit, QComboBox, QPushButton { font-size: 20px; }
        """)
        filter_layout_outer = QVBoxLayout(filter_card)
        filter_layout_outer.setContentsMargins(20, 14, 20, 14)

        filter_row = QHBoxLayout()
        filter_lbl = QLabel("Фильтрация")
        filter_lbl.setStyleSheet("font-size: 20px; font-weight: bold; ")
        filter_row.addWidget(filter_lbl)
        filter_row.addStretch()

        filter_row.addWidget(QLabel("С:"))
        self.range_start = QDateEdit(calendarPopup=True)
        self.range_start.setFixedSize(160, 50)
        self.range_start.setDate(QDate.currentDate().addDays(-7))
        filter_row.addWidget(self.range_start)

        filter_row.addSpacing(10)

        filter_row.addWidget(QLabel("По:"))
        self.range_end = QDateEdit(calendarPopup=True)
        self.range_end.setFixedSize(160, 50)
        self.range_end.setDate(QDate.currentDate())
        filter_row.addWidget(self.range_end)

        filter_row.addSpacing(10)

        self.activity_combo = QComboBox()
        self.activity_combo.setFixedWidth(240)
        self.activity_combo.addItem("Загрузка...")
        self.activity_combo.setEnabled(False)

        apply_btn = QPushButton("Применить")
        apply_btn.setFixedWidth(150)
        apply_btn.clicked.connect(self._apply_filter)

        filter_row.addWidget(self.activity_combo)
        filter_row.addWidget(apply_btn)
        filter_layout_outer.addLayout(filter_row)

        # Entries scroll
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)

        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_layout.setSpacing(10)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_area.setWidget(self.scroll_widget)

        filter_layout_outer.addWidget(self.scroll_area)

        # Pagination
        page_row = QHBoxLayout()
        page_row.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.prev_btn = QPushButton("←")
        self.prev_btn.setFixedWidth(24)
        self.prev_btn.setStyleSheet("QPushButton { background: none; color: black; border: none; font-size: 20px; } ")
        self.prev_btn.clicked.connect(self._prev_page)
        self.page_label = QLabel("1 страница из 1")
        self.page_label.setStyleSheet("font-size: 20px; ")
        self.next_btn = QPushButton("→")
        self.next_btn.setFixedWidth(24)
        self.next_btn.setStyleSheet("QPushButton { background: none; color: black; border: none; font-size: 20px; } ")
        self.next_btn.clicked.connect(self._next_page)
        page_row.addWidget(self.prev_btn)
        page_row.addWidget(self.page_label)
        page_row.addWidget(self.next_btn)
        filter_layout_outer.addLayout(page_row)

        layout.addWidget(filter_card)

        self._load_activity_types()
        self._refresh()

    def _load_activity_types(self):
        """Загружает уникальные типы занятий пользователя через get_diary_entries"""
        from core.operations import get_diary_entries
        
        ok, msg, data = get_diary_entries(self.user_data['id'], page=1, per_page=500)
        
        self.activity_combo.clear()
        self.activity_combo.addItem("Все типы")
        
        if ok and data.get('entries'):
            unique_types = list(set(
                entry.activity_type for entry in data['entries'] 
                if entry.activity_type and entry.activity_type.strip()
            ))
            if unique_types:
                for t in sorted(unique_types):
                    self.activity_combo.addItem(t)
                self.activity_combo.setEnabled(True)
            else:
                self.activity_combo.addItem("У вас отсутствуют типы занятий")
                self.activity_combo.setEnabled(False)
        else:
            self.activity_combo.addItem("У вас отсутствуют типы занятий")
            self.activity_combo.setEnabled(False)

    def _apply_filter(self):
        self.page = 1
        self.start_date = self.range_start.date().toPyDate()
        self.end_date = self.range_end.date().toPyDate()
        act = self.activity_combo.currentText()
        if act in ("Все типы", "У вас отсутствуют типы занятий", "Загрузка..."):
            self.activity_filter = None
        else:
            self.activity_filter = act
        self._refresh()

    def _add_entry(self):
        from ui.diary_add_window import DiaryAddWindow
        self.add_win = DiaryAddWindow(self.user_data['id'], on_saved=self._force_refresh)
        self.add_win.show()

    def _force_refresh(self):
        self.start_date = None
        self.end_date = None
        self.activity_filter = None
        self.page = 1
        
        self._load_activity_types()
        self._refresh()

    def _refresh(self):
        from core.operations import get_diary_entries
        ok, msg, data = get_diary_entries(
            self.user_data['id'],
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

        if not ok:
            QMessageBox.warning(self, "Ошибка", msg)
            print(msg)  
            return

        entries = data.get('entries', [])
        total = data.get('total', 0)
        total_pages = max(1, (total + PER_PAGE - 1) // PER_PAGE)

        if not entries:
            empty = QLabel("Записей не найдено.")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setStyleSheet("color: #888; font-size: 20px; margin: 20px; ")
            self.scroll_layout.addWidget(empty)
        else:
            for entry in entries:
                date_lbl = QLabel(f"Дата: <span style='color:#888'>{entry.date}</span>")
                date_lbl.setStyleSheet("font-size: 20px; font-weight: bold; margin-top: 6px; background: transparent;")
                self.scroll_layout.addWidget(date_lbl)
                card = DiaryEntryCard(entry, self._open_detail)
                self.scroll_layout.addWidget(card)

        self.page_label.setText(f"{self.page} страница из {total_pages}")
        self.prev_btn.setEnabled(self.page > 1)
        self.next_btn.setEnabled(self.page < total_pages)

    def _prev_page(self):
        if self.page > 1:
            self.page -= 1
            self._refresh()

    def _next_page(self):
        self.page += 1
        self._refresh()

    def _open_detail(self, entry):
        from ui.diary_detail_window import DiaryDetailWindow
        self.detail = DiaryDetailWindow(entry, self.user_data, on_close=self._refresh)
        self.detail.show()
