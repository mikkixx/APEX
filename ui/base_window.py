from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QMessageBox
from PyQt6.QtCore import Qt

SPECIALIST_ROLES = ('тренер', 'врач', 'coach', 'doctor')

def _is_specialist(user_data):
    return str(user_data.get('role', '')).lower() in SPECIALIST_ROLES


class BaseWindow(QMainWindow):
    active_tab = ""

    # Вкладки спортсмена
    ATHLETE_TABS = [
        ("Тренировочный план", "training"),
        ("Дневник нагрузок",   "diary"),
        ("Медкарта",           "medical"),
        ("Профиль",            "profile"),
        ("Чаты",               "chats"),
    ]

    # Вкладки специалиста (тренер / врач)
    SPECIALIST_TABS = [
        ("Мои спортсмены", "athletes"),
        ("Отчеты",         "reports"),
        ("Профиль",        "profile"),
        ("Чаты",           "chats"),
    ]

    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        # Выбираем набор вкладок по роли
        self.NAV_TABS = self.SPECIALIST_TABS if _is_specialist(user_data) else self.ATHLETE_TABS
        self.setMinimumSize(1200, 750)
        self.setWindowTitle("APEX")

        central = QWidget()
        self.setCentralWidget(central)
        self._main_layout = QVBoxLayout(central)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(0)

        self._build_navbar()

        self.content = QWidget()
        self._content_layout = QVBoxLayout(self.content)
        self._content_layout.setContentsMargins(40, 32, 40, 32)
        self._main_layout.addWidget(self.content)

    def _build_navbar(self):
        from ui.navbar import NavBar
        self.navbar = NavBar(tabs=self.NAV_TABS, active_tab=self.active_tab)
        self.navbar.nav_requested.connect(self._navigate)
        self.navbar.nav_logout.connect(self._logout)
        self._main_layout.addWidget(self.navbar)

    def _navigate(self, tab):
        if tab == self.active_tab:
            return
        try:
            w = None

            # ── Вкладки спортсмена ────────────────────────────────────
            if tab == "training":
                from ui.training_plan_window import TrainingPlanWindow
                w = TrainingPlanWindow(self.user_data)
            elif tab == "diary":
                from ui.diary_window import DiaryWindow
                w = DiaryWindow(self.user_data)
            elif tab == "medical":
                from ui.medical_window import MedicalWindow
                w = MedicalWindow(self.user_data)

            # ── Вкладки специалиста ───────────────────────────────────
            elif tab == "athletes":
                from ui.my_athletes_window import MyAthletesWindow
                w = MyAthletesWindow(self.user_data)
            elif tab == "reports":
                from ui.reports_window import ReportsWindow
                w = ReportsWindow(self.user_data)

            # ── Общие вкладки ─────────────────────────────────────────
            elif tab == "profile":
                from ui.profile_window import ProfileWindow
                w = ProfileWindow(self.user_data)
            elif tab == "chats":
                from ui.chats_window import ChatsWindow
                w = ChatsWindow(self.user_data)

            if w is None:
                return

            # Сначала показываем новое — потом закрываем текущее,
            # чтобы Qt не видел момента «0 открытых окон».
            self._next_window = w
            w.show()
            self.close()

        except Exception as e:
            import traceback, sys
            print(f"\n🔴 ОШИБКА при открытии вкладки '{tab}':")
            traceback.print_exc()
            sys.stderr.flush()
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть окно:\n{e}")

    def _logout(self):
        from ui.login_window import LoginWindow
        self._login = LoginWindow()
        self._login.show()
        self.close()


# Оставляем для обратной совместимости — теперь просто алиас
class SpecialistBaseWindow(BaseWindow):
    pass
