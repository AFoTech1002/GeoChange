"""GeoChange v2 — Desktop GPS Location Spoofer for Android Emulator."""

import sys
import os
import webbrowser

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt

from app.styles import STYLESHEET
from app.config import STORE_URL


class SubscriptionExpiredDialog(QDialog):
    """Shown when trial/subscription has expired."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("GeoChange — Subscription Required")
        self.setFixedSize(400, 260)
        self.setObjectName("authWindow")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 32, 36, 32)
        layout.setSpacing(16)

        title = QLabel("Subscription Expired")
        title.setObjectName("authLogo")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        msg = QLabel(
            "Your trial or subscription has expired.\n"
            "Purchase a plan to continue using GeoChange."
        )
        msg.setAlignment(Qt.AlignCenter)
        msg.setWordWrap(True)
        msg.setStyleSheet("color: #8899aa; font-size: 13px;")
        layout.addWidget(msg)

        layout.addSpacing(8)

        buy_btn = QPushButton("Buy Subscription")
        buy_btn.setObjectName("teleportButton")
        buy_btn.setMinimumHeight(44)
        buy_btn.setCursor(Qt.PointingHandCursor)
        buy_btn.clicked.connect(lambda: webbrowser.open(STORE_URL))
        layout.addWidget(buy_btn)

        close_btn = QPushButton("Close")
        close_btn.setObjectName("secondaryButton")
        close_btn.setMinimumHeight(36)
        close_btn.clicked.connect(self.reject)
        layout.addWidget(close_btn)


def main():
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("GeoChange")
    app.setStyleSheet(STYLESHEET)

    from app.widgets.auth_window import AuthWindow
    from app.window import MainWindow
    from app.core import api_client

    main_window = None
    auth_window = AuthWindow()

    def show_auth():
        """Show auth window, hide main window."""
        nonlocal main_window
        if main_window:
            main_window.hide()
        auth_window.show()

    def on_auth_success(token: str, user_data: dict):
        nonlocal main_window

        has_access = user_data.get("has_access", False)

        if not has_access:
            dlg = SubscriptionExpiredDialog(auth_window)
            dlg.exec()
            return

        auth_window.hide()

        if main_window is None:
            main_window = MainWindow()
            main_window.logout_requested.connect(on_logout)

        main_window.set_user_data(token, user_data)
        main_window.show()

    def on_logout():
        api_client.clear_token()
        show_auth()

    auth_window.auth_success.connect(on_auth_success)
    auth_window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
