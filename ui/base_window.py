from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout
from ui.navbar import NavBar


class BaseWindow(QMainWindow):
    """Base class for all authenticated screens. Subclasses set self.active_tab."""
    active_tab = ""

    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.setMinimumSize(1100, 700)
        self.setWindowTitle("APEX")

        central = QWidget()
        self.setCentralWidget(central)
        self._main_layout = QVBoxLayout(central)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(0)

        self.navbar = NavBar(active_tab=self.active_tab)
        self.navbar.nav_training.connect(lambda: self._navigate("training"))
        self.navbar.nav_diary.connect(lambda: self._navigate("diary"))
        self.navbar.nav_medical.connect(lambda: self._navigate("medical"))
        self.navbar.nav_profile.connect(lambda: self._navigate("profile"))
        self.navbar.nav_chats.connect(lambda: self._navigate("chats"))
        self.navbar.nav_logout.connect(self._logout)
        self._main_layout.addWidget(self.navbar)

        self.content = QWidget()
        self._content_layout = QVBoxLayout(self.content)
        self._content_layout.setContentsMargins(40, 32, 40, 32)
        self._main_layout.addWidget(self.content)

    def _navigate(self, tab):
        if tab == self.active_tab:
            return
        if tab == "training":
            from ui.training_plan_window import TrainingPlanWindow
            w = TrainingPlanWindow(self.user_data)
        elif tab == "diary":
            from ui.diary_window import DiaryWindow
            w = DiaryWindow(self.user_data)
        elif tab == "medical":
            from ui.medical_window import MedicalWindow
            w = MedicalWindow(self.user_data)
        elif tab == "profile":
            from ui.profile_window import ProfileWindow
            w = ProfileWindow(self.user_data)
        elif tab == "chats":
            from ui.chats_window import ChatsWindow
            w = ChatsWindow(self.user_data)
        else:
            return
        w.show()
        self.close()

    def _logout(self):
        from core.operations import logout
        logout()
        from ui.login_window import LoginWindow
        self._login = LoginWindow()
        self._login.show()
        self.close()
