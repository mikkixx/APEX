from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtCore import Qt, pyqtSignal

class NavBar(QWidget):
    nav_training = pyqtSignal()
    nav_diary = pyqtSignal()
    nav_medical = pyqtSignal()
    nav_profile = pyqtSignal()
    nav_chats = pyqtSignal()
    nav_logout = pyqtSignal()

    def __init__(self, active_tab=""):
        super().__init__()
        self.active_tab = active_tab
        self._build()

    def _build(self):
        self.setFixedHeight(64)
        self.setStyleSheet("""
            NavBar {
                background: #ffffff;
                border-bottom: 1px solid #e0e0e0;
            }
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 0, 24, 0)
        layout.setSpacing(0)

        # Logo
        logo_label = QLabel()
        logo_pix = QPixmap("img/logo.png")
        if not logo_pix.isNull():
            logo_label.setPixmap(logo_pix.scaledToHeight(44, Qt.TransformationMode.SmoothTransformation))
        else:
            logo_label.setText("APEX")
            logo_label.setStyleSheet("font-size: 22px; font-weight: bold;")
        logo_label.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(logo_label)
        layout.addSpacing(32)

        tabs = [
            ("Тренировочный план", "training", self.nav_training),
            ("Дневник нагрузок",    "diary",    self.nav_diary),
            ("Медкарта",            "medical",  self.nav_medical),
            ("Профиль",             "profile",  self.nav_profile),
            ("Чаты",                "chats",    self.nav_chats),
        ]

        for label, key, signal in tabs:
            btn = QPushButton(label)
            btn.setFlat(True)
            is_active = (key == self.active_tab)
            
            # 🔹 ИСПРАВЛЕНИЕ: убрано подчеркивание, неактивные ссылки стали светлее (#888888)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    color: {'#1a1a1a' if is_active else '#888888'};
                    font-size: 20px;
                    font-weight: {'bold' if is_active else 'normal'};
                    border: none;
                    border-radius: 0px;
                    padding: 4px 16px;
                }}
                QPushButton:hover {{
                    color: #1a1a1a;
                }}
            """)
            btn.clicked.connect(signal.emit)
            layout.addWidget(btn)

        layout.addStretch()

        logout_btn = QPushButton("Выйти")
        logout_btn.setFixedWidth(110)
        logout_btn.clicked.connect(self.nav_logout.emit)
        layout.addWidget(logout_btn)