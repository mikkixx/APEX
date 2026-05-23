from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QScrollArea, QDateEdit, QDoubleSpinBox, QMessageBox
)
from PyQt6.QtCore import QDate
from core.operations import create_medical_exam

class ExamAddWindow(QWidget):
    def __init__(self, athlete_id, doctor_id, on_saved=None):
        super().__init__()
        self.athlete_id = athlete_id
        self.doctor_id = doctor_id
        self.on_saved = on_saved
        self.metric_rows = []
        self.setWindowTitle("Новый медицинский осмотр")
        self.setMinimumSize(950, 700)
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
        container.setStyleSheet("""
            QLabel, QLineEdit, QDateEdit, QSpinBox, QDoubleSpinBox, QPushButton {
                font-size: 20px;
            }
            QDateEdit, QLineEdit { padding: 0 10px; }
        """)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(48, 32, 48, 32)
        layout.setSpacing(14)

        title = QLabel("Новый осмотр")
        title.setStyleSheet("font-size: 32px; font-weight: bold;")
        layout.addWidget(title)
        layout.addSpacing(8)

        layout.addWidget(QLabel("Дата осмотра:"))
        self.date_edit = QDateEdit(calendarPopup=True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setFixedHeight(52)
        layout.addWidget(self.date_edit)

        layout.addWidget(QLabel("Тип осмотра:"))
        self.exam_type = QLineEdit()
        self.exam_type.setPlaceholderText("Например: общий, кардиологический")
        self.exam_type.setFixedHeight(52)
        layout.addWidget(self.exam_type)

        metrics_lbl = QLabel("Показатели")
        metrics_lbl.setStyleSheet("font-size: 24px; font-weight: bold; margin-top: 8px;")
        layout.addWidget(metrics_lbl)
        layout.addSpacing(4)

        info_lbl = QLabel("💡 Норма вводится через дефис (например: 4.0-4.6). Значения вне диапазона подсветятся красным автоматически.")
        info_lbl.setStyleSheet("font-size: 18px; color: #666; background: transparent; border: none;")
        info_lbl.setWordWrap(True)
        layout.addWidget(info_lbl)
        layout.addSpacing(8)

        self.metrics_container = QWidget()
        self.metrics_layout = QVBoxLayout(self.metrics_container)
        self.metrics_layout.setContentsMargins(0, 0, 0, 0)
        self.metrics_layout.setSpacing(10)
        layout.addWidget(self.metrics_container)

        add_metric_btn = QPushButton("Добавить показатель")
        add_metric_btn.setFixedHeight(52)
        add_metric_btn.setStyleSheet("""
            QPushButton { background: #1a1a1a; color: white; border-radius: 20px; font-weight: bold; }
            QPushButton:hover { background: #333; }
        """)
        add_metric_btn.clicked.connect(self._add_metric_row)
        layout.addWidget(add_metric_btn)

        self._add_metric_row()

        save_btn = QPushButton("Сохранить осмотр")
        save_btn.setFixedHeight(56)
        save_btn.setStyleSheet("""
            QPushButton { background: #1a1a1a; color: white; border-radius: 20px; font-weight: bold; }
            QPushButton:hover { background: #333; }
        """)
        save_btn.clicked.connect(self._save)
        layout.addWidget(save_btn)
        layout.addStretch()

    def _add_metric_row(self):
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(8)

        name_inp = QLineEdit()
        name_inp.setPlaceholderText("Тип показателя")
        name_inp.setFixedHeight(48)

        val_inp = QDoubleSpinBox()
        val_inp.setRange(-9999, 9999)
        val_inp.setDecimals(2)
        val_inp.setFixedHeight(48)
        val_inp.setFixedWidth(180)

        unit_inp = QLineEdit()
        unit_inp.setPlaceholderText("Ед.измерения")
        unit_inp.setFixedHeight(48)
        unit_inp.setFixedWidth(160)

        ref_inp = QLineEdit()
        ref_inp.setPlaceholderText("Норма (4.0-4.6)")
        ref_inp.setFixedHeight(48)
        ref_inp.setFixedWidth(200)

        del_btn = QPushButton("Удалить")
        del_btn.setFixedHeight(48)
        del_btn.setStyleSheet("""
            QPushButton { background: #1a1a1a; color: white; border-radius: 20px; font-weight: bold; }
            QPushButton:hover { background: transparent; border: 1px solid #1a1a1a; color: #1a1a1a;}
        """)
        del_btn.clicked.connect(lambda: self._remove_metric_row(row_widget))

        # ✅ Автоподсветка критичных значений
        val_inp.valueChanged.connect(lambda: self._check_critical(val_inp, ref_inp, name_inp))
        ref_inp.textChanged.connect(lambda: self._check_critical(val_inp, ref_inp, name_inp))

        row_layout.addWidget(name_inp, 2)
        row_layout.addWidget(val_inp)
        row_layout.addWidget(unit_inp)
        row_layout.addWidget(ref_inp)
        row_layout.addWidget(del_btn)

        self.metrics_layout.addWidget(row_widget)
        self.metric_rows.append((row_widget, name_inp, val_inp, unit_inp, ref_inp))

    def _remove_metric_row(self, row_widget):
        if len(self.metric_rows) <= 1:
            QMessageBox.warning(self, "Внимание", "Должен остаться хотя бы один показатель.")
            return
        row_widget.deleteLater()
        self.metric_rows = [r for r in self.metric_rows if r[0] != row_widget]

    def _check_critical(self, val_inp, ref_inp, name_inp):
        ref_text = ref_inp.text().strip().replace(',', '.')
        val = val_inp.value()
        
        # ✅ Стиль применяется к ВСЕМУ виджету (включая стрелочки), как просили
        if '-' in ref_text:
            try:
                low_str, high_str = ref_text.split('-')
                low, high = float(low_str), float(high_str)
                if val < low or val > high:
                    name_inp.setStyleSheet("QLineEdit { color: #cc0000; font-weight: bold; }")
                    # ✅ Красит всё поле целиком (текст + стрелки)
                    val_inp.setStyleSheet("color: #cc0000; font-weight: bold;") 
                else:
                    name_inp.setStyleSheet("")
                    val_inp.setStyleSheet("") # ✅ Сброс
            except ValueError:
                name_inp.setStyleSheet("")
                val_inp.setStyleSheet("")
        else:
            name_inp.setStyleSheet("")
            val_inp.setStyleSheet("")

    def _save(self):
        date = self.date_edit.date().toPyDate()
        exam_type = self.exam_type.text().strip()
        if not exam_type:
            QMessageBox.warning(self, "Ошибка", "Укажите тип осмотра")
            return

        metrics = []
        for _, name_inp, val_inp, unit_inp, ref_inp in self.metric_rows:
            name = name_inp.text().strip()
            if not name: continue
                
            ref_text = ref_inp.text().strip()
            metrics.append({
                'metric_type': name,
                'value': val_inp.value(),
                'unit': unit_inp.text().strip() or '—',
                'ref_range': ref_text if ref_text else '—',
                'is_critical': False
            })

        if not metrics:
            QMessageBox.warning(self, "Ошибка", "Добавьте хотя бы один показатель")
            return

        ok, msg, _ = create_medical_exam(self.athlete_id, self.doctor_id, date, exam_type, metrics)
        if ok:
            QMessageBox.information(self, "Успех", "Осмотр успешно сохранён.")
            if self.on_saved:
                self.on_saved()
            self.close()
        else:
            QMessageBox.warning(self, "Ошибка", msg)