from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QScrollArea, QDateEdit, QComboBox, QSpinBox,
    QDoubleSpinBox, QHBoxLayout, QMessageBox, QCheckBox
)
from PyQt6.QtCore import QDate


class ExamAddWindow(QWidget):
    def __init__(self, athlete_id, doctor_id, on_saved=None):
        super().__init__()
        self.athlete_id = athlete_id
        self.doctor_id = doctor_id
        self.on_saved = on_saved
        self.metric_rows = []
        self.setWindowTitle("Новый медицинский осмотр")
        self.setMinimumSize(560, 700)
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
        layout = QVBoxLayout(container)
        layout.setContentsMargins(48, 32, 48, 32)
        layout.setSpacing(12)

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
        self.exam_type = QComboBox()
        self.exam_type.setFixedHeight(52)
        self.exam_type.addItems(["общий", "кардиологический", "неврологический", "ортопедический"])
        layout.addWidget(self.exam_type)

        metrics_lbl = QLabel("Показатели")
        metrics_lbl.setStyleSheet("font-size: 22px; font-weight: bold; margin-top: 8px;")
        layout.addWidget(metrics_lbl)

        self.metrics_container = QWidget()
        self.metrics_layout = QVBoxLayout(self.metrics_container)
        self.metrics_layout.setContentsMargins(0, 0, 0, 0)
        self.metrics_layout.setSpacing(8)
        layout.addWidget(self.metrics_container)

        add_metric_btn = QPushButton("+ Добавить показатель")
        add_metric_btn.setFixedHeight(48)
        add_metric_btn.setStyleSheet("""
            QPushButton { background: transparent; color: #1a1a1a;
                border: 1.5px solid #1a1a1a; border-radius: 18px; font-size: 20px; }
            QPushButton:hover { background: #f0f0f0; }
        """)
        add_metric_btn.clicked.connect(self._add_metric_row)
        layout.addWidget(add_metric_btn)

        self._add_metric_row()  # Start with one row

        save_btn = QPushButton("Сохранить осмотр")
        save_btn.setFixedHeight(52)
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
        val_inp.setFixedWidth(100)

        unit_inp = QLineEdit()
        unit_inp.setPlaceholderText("Ед.")
        unit_inp.setFixedHeight(48)
        unit_inp.setFixedWidth(70)

        ref_inp = QLineEdit()
        ref_inp.setPlaceholderText("Норма")
        ref_inp.setFixedHeight(48)
        ref_inp.setFixedWidth(100)

        crit_cb = QCheckBox("Критично")
        crit_cb.setStyleSheet("font-size: 20px;")

        row_layout.addWidget(name_inp, 2)
        row_layout.addWidget(val_inp)
        row_layout.addWidget(unit_inp)
        row_layout.addWidget(ref_inp)
        row_layout.addWidget(crit_cb)

        self.metrics_layout.addWidget(row_widget)
        self.metric_rows.append((name_inp, val_inp, unit_inp, ref_inp, crit_cb))

    def _save(self):
        from core.operations import create_medical_exam
        date = self.date_edit.date().toPyDate()
        exam_type = self.exam_type.currentText()

        metrics = []
        for name_inp, val_inp, unit_inp, ref_inp, crit_cb in self.metric_rows:
            name = name_inp.text().strip()
            if not name:
                continue
            metrics.append({
                'metric_type': name,
                'value': val_inp.value(),
                'unit': unit_inp.text().strip() or '—',
                'ref_range': ref_inp.text().strip() or '—',
                'is_critical': crit_cb.isChecked()
            })

        if not metrics:
            QMessageBox.warning(self, "Ошибка", "Добавьте хотя бы один показатель")
            return

        ok, msg, _ = create_medical_exam(
            self.athlete_id, self.doctor_id, date, exam_type, metrics
        )
        if ok:
            if self.on_saved:
                self.on_saved()
            self.close()
        else:
            QMessageBox.warning(self, "Ошибка", msg)
