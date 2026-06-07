import sys

from config import load_config
from transcriber import Transcriber


STYLESHEET = """
QMainWindow, QWidget { background-color: #1e1e2e; color: #e4e4e7; }
QLabel { color: #e4e4e7; }
QGroupBox {
    border: 1px solid #3f3f5a;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 10px;
}
QGroupBox::title {
    color: #a78bfa;
    subcontrol-origin: margin;
    subcontrol-position: top right;
    padding: 0 8px;
}
QComboBox, QLineEdit {
    background: #2a2a3e;
    color: #e4e4e7;
    border: 1px solid #3f3f5a;
    border-radius: 4px;
    padding: 6px;
}
QComboBox QAbstractItemView {
    background: #2a2a3e;
    color: #e4e4e7;
    selection-background-color: #a78bfa;
}
QPushButton {
    background: #3b1d5e;
    color: #f0abfc;
    border: 1px solid #a78bfa;
    border-radius: 6px;
    padding: 8px 16px;
}
QPushButton:hover { background: #4a1d7e; }
QPushButton:disabled {
    background: #2a2a3e;
    color: #6b7280;
    border-color: #3f3f5a;
}
QTabWidget::pane { border: 1px solid #3f3f5a; border-radius: 6px; }
QTabBar::tab {
    background: #2a2a3e;
    color: #e4e4e7;
    padding: 8px 16px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
}
QTabBar::tab:selected { background: #3b1d5e; color: #f0abfc; }
QTableWidget {
    background: #2a2a3e;
    color: #e4e4e7;
    gridline-color: #3f3f5a;
}
QTableWidget::item:selected { background: #3b1d5e; }
QHeaderView::section {
    background: #1f2937;
    color: #a78bfa;
    padding: 6px;
    border: 1px solid #3f3f5a;
}
QListWidget {
    background: #2a2a3e;
    color: #e4e4e7;
    border: 1px solid #3f3f5a;
}
QListWidget::item:selected { background: #3b1d5e; color: #f0abfc; }
QCheckBox { color: #e4e4e7; padding: 4px; }
QCheckBox::indicator { width: 18px; height: 18px; }
QScrollArea { border: none; }
"""


def main():
    print("=" * 60)
    print("  כלי הכתבה - Dictation Tool")
    print("=" * 60)

    # ---- Phase 1: Load config and transcriber BEFORE touching Qt or keyboard ----
    # This is the safest order. Loading Whisper inside the same Python state as
    # PyQt + Windows keyboard hooks caused hard crashes. Loading first, alone,
    # mirrors the MVP setup that worked.
    config = load_config()
    print(f"[Main] Config loaded. Model: {config['model_size']}, language: {config['language']}")

    print("[Main] Loading transcriber (this may take a while on first run)...")
    transcriber = Transcriber(config["model_size"], config.get("device", "auto"))
    print("[Main] Transcriber ready.")

    # ---- Phase 2: Now bring in Qt + keyboard ----
    from PyQt5.QtCore import Qt, QObject, QTimer
    from PyQt5.QtWidgets import QApplication, QSystemTrayIcon
    import keyboard
    from app import DictationApp
    from gui import MainWindow, TrayIcon

    qt_app = QApplication(sys.argv)
    qt_app.setApplicationName("כלי הכתבה")
    qt_app.setQuitOnLastWindowClosed(False)
    qt_app.setLayoutDirection(Qt.RightToLeft)
    qt_app.setStyleSheet(STYLESHEET)

    dictation_app = DictationApp(config, transcriber)
    window = MainWindow(dictation_app)
    tray = TrayIcon(window)
    tray.show()

    class HotkeyManager(QObject):
        def __init__(self):
            super().__init__()
            self.current_hotkey = None

        def register(self, hk):
            self.unregister()
            try:
                keyboard.add_hotkey(hk, dictation_app.toggle_recording)
                self.current_hotkey = hk
                print(f"[Hotkey] Registered: {hk}")
            except Exception as e:
                print(f"[Hotkey] Failed to register '{hk}': {e}")

        def unregister(self):
            if self.current_hotkey:
                try:
                    keyboard.remove_hotkey(self.current_hotkey)
                except Exception:
                    pass
                self.current_hotkey = None

    hotkey_mgr = HotkeyManager()

    def show_window():
        window.show()
        window.raise_()
        window.activateWindow()

    def real_quit():
        hotkey_mgr.unregister()
        window.force_quit()
        qt_app.quit()

    def reregister_hotkey():
        new_hk = dictation_app.config.get("hotkey", "ctrl+shift+space")
        if new_hk != hotkey_mgr.current_hotkey:
            hotkey_mgr.register(new_hk)

    tray.open_requested.connect(show_window)
    tray.toggle_requested.connect(dictation_app.toggle_recording)
    tray.quit_requested.connect(real_quit)
    dictation_app.state_changed.connect(tray.set_state)
    window.hotkey_change_requested.connect(reregister_hotkey)

    hotkey_mgr.register(config.get("hotkey", "ctrl+shift+space"))
    show_window()

    # Now that the window is showing, push the initial "ready" state
    dictation_app.emit_initial_state()

    QTimer.singleShot(500, lambda: tray.showMessage(
        "כלי הכתבה",
        f"מוכן. לחץ {config.get('hotkey')} להקלטה.",
        QSystemTrayIcon.Information,
        3000,
    ))

    sys.exit(qt_app.exec_())


if __name__ == "__main__":
    main()
