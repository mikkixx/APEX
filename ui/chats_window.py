from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QWidget, QFrame, QTextEdit,
    QLineEdit, QMessageBox, QListWidget, QListWidgetItem,
    QInputDialog, QSizePolicy, QDateEdit
)
from PyQt6.QtCore import Qt, QDate, QTimer
from PyQt6.QtGui import QPixmap, QFont
from ui.base_window import BaseWindow


class ChatsWindow(BaseWindow):
    active_tab = "chats"

    def __init__(self, user_data):
        super().__init__(user_data)
        self.current_partner = None
        self._load()

    def _load(self):
        layout = self._content_layout

        title = QLabel("ЧАТЫ")
        title.setStyleSheet("font-size: 26px; font-weight: bold; letter-spacing: 1px;")
        title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(title)
        layout.addSpacing(12)

        main_card = QFrame()
        main_card.setStyleSheet("QFrame { border: 1px solid #e0e0e0; border-radius: 20px; background: #fafafa; }")
        main_row = QHBoxLayout(main_card)
        main_row.setContentsMargins(0, 0, 0, 0)
        main_row.setSpacing(0)

        # Left panel - partner list
        left_panel = QFrame()
        left_panel.setFixedWidth(220)
        left_panel.setStyleSheet("""
            QFrame { border: none; border-right: 1px solid #e0e0e0;
                border-radius: 0px; background: #f5f5f5;
                border-top-left-radius: 20px; border-bottom-left-radius: 20px; }
        """)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)

        self.partner_list = QListWidget()
        self.partner_list.setStyleSheet("""
            QListWidget { border: none; background: transparent; font-size: 14px; }
            QListWidget::item { padding: 12px 16px; border-bottom: 1px solid #e8e8e8; }
            QListWidget::item:selected { background: #e0e0e0; }
            QListWidget::item:hover { background: #eaeaea; }
        """)
        self.partner_list.currentRowChanged.connect(self._on_partner_selected)
        left_layout.addWidget(self.partner_list)

        add_partner_btn = QPushButton("Добавить собеседника")
        add_partner_btn.setStyleSheet("""
            QPushButton { background: #1a1a1a; color: white; border-radius: 0px;
                border-bottom-left-radius: 20px; padding: 14px;
                font-size: 13px; border: none; }
            QPushButton:hover { background: #333; }
        """)
        add_partner_btn.clicked.connect(self._add_partner)
        left_layout.addWidget(add_partner_btn)

        main_row.addWidget(left_panel)

        # Right panel - chat area
        self.right_panel = QFrame()
        self.right_panel.setStyleSheet("QFrame { border: none; background: transparent; }")
        right_layout = QVBoxLayout(self.right_panel)
        right_layout.setContentsMargins(20, 16, 20, 16)
        right_layout.setSpacing(10)

        # Partner info header
        partner_info_row = QHBoxLayout()
        self.partner_avatar = QLabel()
        self.partner_avatar.setFixedSize(44, 44)
        self.partner_avatar.setStyleSheet("border-radius: 22px; background: #ccc;")
        self.partner_avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.partner_name_lbl = QLabel("Выберите собеседника")
        self.partner_name_lbl.setStyleSheet("font-size: 16px; font-weight: bold;")
        partner_info_row.addWidget(self.partner_avatar)
        partner_info_row.addSpacing(8)
        partner_info_row.addWidget(self.partner_name_lbl)
        partner_info_row.addStretch()
        right_layout.addLayout(partner_info_row)

        # Search & filter
        search_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск")
        self.search_input.setFixedHeight(40)
        self.date_filter = QDateEdit(calendarPopup=True)
        self.date_filter.setDate(QDate.currentDate().addDays(-30))
        self.date_filter.setPrefix("С: ")
        self.date_filter.setFixedHeight(40)
        self.date_end = QDateEdit(calendarPopup=True)
        self.date_end.setDate(QDate.currentDate())
        self.date_end.setPrefix("По: ")
        self.date_end.setFixedHeight(40)
        apply_search_btn = QPushButton("Применить")
        apply_search_btn.setFixedWidth(110)
        apply_search_btn.setFixedHeight(40)
        apply_search_btn.clicked.connect(self._reload_messages)
        search_row.addWidget(self.search_input)
        search_row.addWidget(self.date_filter)
        search_row.addWidget(self.date_end)
        search_row.addWidget(apply_search_btn)
        right_layout.addLayout(search_row)

        # Messages scroll
        self.msg_scroll = QScrollArea()
        self.msg_scroll.setWidgetResizable(True)
        self.msg_scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self.msg_widget = QWidget()
        self.msg_layout = QVBoxLayout(self.msg_widget)
        self.msg_layout.setSpacing(8)
        self.msg_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.msg_scroll.setWidget(self.msg_widget)
        right_layout.addWidget(self.msg_scroll)

        # Send message
        send_row = QHBoxLayout()
        self.msg_input = QTextEdit()
        self.msg_input.setPlaceholderText("Новое сообщение")
        self.msg_input.setFixedHeight(64)
        send_btn = QPushButton("Отправить")
        send_btn.setFixedWidth(120)
        send_btn.setFixedHeight(64)
        send_btn.clicked.connect(self._send_message)
        send_row.addWidget(self.msg_input)
        send_row.addWidget(send_btn)
        right_layout.addLayout(send_row)

        main_row.addWidget(self.right_panel)
        layout.addWidget(main_card)

        self._load_partners()

    def _load_partners(self):
        from core.operations import get_chat_partners
        ok, msg, partners = get_chat_partners(self.user_data['id'])
        self.partners = partners or []
        self.partner_list.clear()
        for p in self.partners:
            item = QListWidgetItem(f"  {p['full_name']}")
            item.setData(Qt.ItemDataRole.UserRole, p)
            self.partner_list.addItem(item)

    def _on_partner_selected(self, row):
        if row < 0 or row >= len(self.partners):
            return
        self.current_partner = self.partners[row]
        self.partner_name_lbl.setText(self.current_partner['full_name'])
        self._reload_messages()

    def _reload_messages(self):
        if not self.current_partner:
            return
        from core.operations import get_chat_messages
        search = self.search_input.text().strip() or None
        start = self.date_filter.date().toPyDate()
        end = self.date_end.date().toPyDate()

        ok, msg, messages = get_chat_messages(
            self.user_data['id'], self.current_partner['id'],
            search_query=search, start_date=start, end_date=end
        )

        while self.msg_layout.count():
            item = self.msg_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not ok:
            return

        for message in (messages or []):
            self._add_message_bubble(message)

        # Scroll to bottom
        QTimer.singleShot(50, lambda: self.msg_scroll.verticalScrollBar().setValue(
            self.msg_scroll.verticalScrollBar().maximum()
        ))

    def _add_message_bubble(self, message):
        is_mine = message['is_mine']
        row = QHBoxLayout()

        bubble = QFrame()
        bubble.setStyleSheet(f"""
            QFrame {{
                background: {'#1a1a1a' if is_mine else '#f0f0f0'};
                border-radius: 12px;
                padding: 4px;
            }}
        """)
        bubble_layout = QVBoxLayout(bubble)
        bubble_layout.setContentsMargins(12, 8, 12, 8)
        bubble_layout.setSpacing(2)

        if not is_mine:
            sender_lbl = QLabel(message.get('sender_name', ''))
            sender_lbl.setStyleSheet("font-size: 11px; font-weight: bold; color: #555;")
            bubble_layout.addWidget(sender_lbl)

        text_lbl = QLabel(message['text'])
        text_lbl.setWordWrap(True)
        text_lbl.setStyleSheet(f"color: {'white' if is_mine else '#1a1a1a'}; font-size: 14px;")
        text_lbl.setMaximumWidth(500)
        bubble_layout.addWidget(text_lbl)

        time_lbl = QLabel(str(message['sent_at'])[:16])
        time_lbl.setStyleSheet(f"font-size: 10px; color: {'#aaa' if is_mine else '#888'};")
        bubble_layout.addWidget(time_lbl)

        if is_mine:
            row.addStretch()
            row.addWidget(bubble)
        else:
            row.addWidget(bubble)
            row.addStretch()

        container = QWidget()
        container.setLayout(row)
        self.msg_layout.addWidget(container)

    def _send_message(self):
        if not self.current_partner:
            QMessageBox.warning(self, "Ошибка", "Выберите собеседника")
            return
        text = self.msg_input.toPlainText().strip()
        if not text:
            return
        from core.operations import send_message
        ok, msg, _ = send_message(self.user_data['id'], self.current_partner['id'], text)
        if ok:
            self.msg_input.clear()
            self._reload_messages()
        else:
            QMessageBox.warning(self, "Ошибка", msg)

    def _add_partner(self):
        email, ok = QInputDialog.getText(self, "Добавить собеседника", "Введите email пользователя:")
        if not ok or not email.strip():
            return
        from core.operations import add_chat_partner
        success, msg, partner_data = add_chat_partner(self.user_data['id'], email.strip())
        if success:
            # Check if already in list
            for p in self.partners:
                if p['id'] == partner_data['id']:
                    QMessageBox.information(self, "Инфо", "Собеседник уже добавлен.")
                    return
            self.partners.append(partner_data)
            item = QListWidgetItem(f"  {partner_data['full_name']}")
            item.setData(Qt.ItemDataRole.UserRole, partner_data)
            self.partner_list.addItem(item)
            self.partner_list.setCurrentRow(len(self.partners) - 1)
        else:
            QMessageBox.warning(self, "Ошибка", msg)
