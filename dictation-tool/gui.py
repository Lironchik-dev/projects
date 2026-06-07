from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QBrush, QFont
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QComboBox, QCheckBox, QTabWidget, QTableWidget, QTableWidgetItem,
    QHeaderView, QListWidget, QGroupBox, QMessageBox, QSystemTrayIcon, QMenu,
    QAction, QInputDialog, QScrollArea,
)

from app import (
    STATE_LOADING, STATE_IDLE, STATE_RECORDING, STATE_TRANSCRIBING, STATE_ERROR,
)


LANG_DISPLAY = {
    "he": "עברית 🇮🇱",
    "en": "English 🇺🇸",
    "ru": "Русский 🇷🇺",
}
LANG_CODES = ["he", "en", "ru"]
MODEL_SIZES = ["tiny", "base", "small", "medium", "large-v3"]
DEVICES = [("auto", "אוטומטי"), ("cuda", "GPU (CUDA)"), ("cpu", "מעבד (CPU)")]


STATE_COLOR = {
    STATE_LOADING: "#fbbf24",
    STATE_IDLE: "#10b981",
    STATE_RECORDING: "#ef4444",
    STATE_TRANSCRIBING: "#3b82f6",
    STATE_ERROR: "#6b7280",
}
STATE_LABEL = {
    STATE_LOADING: "טוען...",
    STATE_IDLE: "מוכן",
    STATE_RECORDING: "מקליט...",
    STATE_TRANSCRIBING: "מתמלל...",
    STATE_ERROR: "שגיאה",
}
RECORD_BUTTON_TEXT = {
    STATE_LOADING: "🔄 טוען...",
    STATE_IDLE: "🎤 לחץ להקלטה",
    STATE_RECORDING: "⏹ לחץ לעצירה",
    STATE_TRANSCRIBING: "📝 מתמלל...",
    STATE_ERROR: "🎤 לחץ להקלטה",
}


def make_status_icon(color_hex, size=64):
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)
    p = QPainter(pixmap)
    p.setRenderHint(QPainter.Antialiasing)
    p.setBrush(QBrush(QColor(color_hex)))
    p.setPen(Qt.NoPen)
    margin = 6
    p.drawEllipse(margin, margin, size - 2 * margin, size - 2 * margin)
    p.end()
    return QIcon(pixmap)


class MainWindow(QMainWindow):
    closing = pyqtSignal()
    hotkey_change_requested = pyqtSignal()

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setWindowTitle("כלי הכתבה")
        self.setLayoutDirection(Qt.RightToLeft)
        self.resize(620, 720)

        self._build_ui()
        self._connect_signals()
        self._refresh_from_config()
        self._set_state(app.state)

        self._force_quit = False

    # ----------------------------- UI BUILDING -----------------------------

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        outer = QVBoxLayout(central)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

        inner = QWidget()
        scroll.setWidget(inner)
        layout = QVBoxLayout(inner)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Status line
        self.status_label = QLabel("טוען...")
        self.status_label.setAlignment(Qt.AlignCenter)
        status_font = QFont()
        status_font.setPointSize(14)
        status_font.setBold(True)
        self.status_label.setFont(status_font)
        layout.addWidget(self.status_label)

        self.info_label = QLabel("")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet("color: #9ca3af;")
        layout.addWidget(self.info_label)

        # Big record button
        self.record_btn = QPushButton("🎤 לחץ להקלטה")
        self.record_btn.setMinimumHeight(120)
        big_font = QFont()
        big_font.setPointSize(22)
        big_font.setBold(True)
        self.record_btn.setFont(big_font)
        self.record_btn.clicked.connect(self._on_record_clicked)
        layout.addWidget(self.record_btn)

        # Last transcription display
        last_box = QGroupBox("טקסט אחרון")
        last_layout = QVBoxLayout(last_box)
        self.last_raw_label = QLabel("(עוד לא הוקלט שום דבר)")
        self.last_raw_label.setWordWrap(True)
        self.last_raw_label.setStyleSheet("color: #9ca3af; font-size: 13px;")
        self.last_processed_label = QLabel("")
        self.last_processed_label.setWordWrap(True)
        self.last_processed_label.setStyleSheet("color: #10b981; font-size: 15px; font-weight: bold;")
        last_layout.addWidget(QLabel("גולמי:"))
        last_layout.addWidget(self.last_raw_label)
        last_layout.addWidget(QLabel("אחרי עיבוד:"))
        last_layout.addWidget(self.last_processed_label)
        layout.addWidget(last_box)

        # Settings tabs
        tabs = QTabWidget()
        tabs.addTab(self._build_general_tab(), "כללי")
        tabs.addTab(self._build_dictionary_tab(), "מילון אישי")
        tabs.addTab(self._build_fillers_tab(), "מילות מילוי")
        layout.addWidget(tabs)

        # Bottom save button
        save_row = QHBoxLayout()
        self.save_btn = QPushButton("💾 שמור שינויים")
        self.save_btn.setMinimumHeight(40)
        save_font = QFont()
        save_font.setPointSize(12)
        save_font.setBold(True)
        self.save_btn.setFont(save_font)
        self.save_btn.clicked.connect(self._on_save_clicked)
        save_row.addStretch()
        save_row.addWidget(self.save_btn)
        save_row.addStretch()
        layout.addLayout(save_row)

    def _build_general_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)

        # Language
        row = QHBoxLayout()
        row.addWidget(QLabel("שפה:"))
        self.lang_combo = QComboBox()
        for code in LANG_CODES:
            self.lang_combo.addItem(LANG_DISPLAY[code], code)
        row.addWidget(self.lang_combo, 1)
        layout.addLayout(row)

        # Model
        row = QHBoxLayout()
        row.addWidget(QLabel("מודל Whisper:"))
        self.model_combo = QComboBox()
        for m in MODEL_SIZES:
            self.model_combo.addItem(m, m)
        row.addWidget(self.model_combo, 1)
        layout.addLayout(row)

        # Device
        row = QHBoxLayout()
        row.addWidget(QLabel("מכשיר עיבוד:"))
        self.device_combo = QComboBox()
        for code, label in DEVICES:
            self.device_combo.addItem(label, code)
        row.addWidget(self.device_combo, 1)
        layout.addLayout(row)

        # Hotkey
        row = QHBoxLayout()
        row.addWidget(QLabel("קיצור הקלטה:"))
        self.hotkey_label = QLabel("---")
        self.hotkey_label.setStyleSheet(
            "background: #1f2937; color: #f0abfc; padding: 6px 14px; border-radius: 6px; font-family: Consolas;"
        )
        row.addWidget(self.hotkey_label, 1)
        self.hotkey_btn = QPushButton("שנה")
        self.hotkey_btn.clicked.connect(self._on_change_hotkey)
        row.addWidget(self.hotkey_btn)
        layout.addLayout(row)

        # Checkboxes
        self.cb_fillers = QCheckBox("הסר מילות מילוי")
        self.cb_dict = QCheckBox("השתמש במילון אישי")
        layout.addWidget(self.cb_fillers)
        layout.addWidget(self.cb_dict)

        layout.addStretch()
        return widget

    def _build_dictionary_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        info = QLabel(
            "כאן אפשר להגדיר החלפות אוטומטיות. למשל: 'קלוד' → 'Claude'."
            " ההחלפה תקרה לאחר התמלול ולפני ההדבקה."
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: #9ca3af;")
        layout.addWidget(info)

        self.dict_table = QTableWidget(0, 2)
        self.dict_table.setHorizontalHeaderLabels(["מקור (כפי שיתומלל)", "יעד (מה להחליף)"])
        self.dict_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.dict_table.verticalHeader().setVisible(False)
        layout.addWidget(self.dict_table)

        btn_row = QHBoxLayout()
        self.add_dict_btn = QPushButton("➕ הוסף שורה")
        self.add_dict_btn.clicked.connect(self._add_dict_row)
        self.remove_dict_btn = QPushButton("🗑 מחק שורה נבחרת")
        self.remove_dict_btn.clicked.connect(self._remove_dict_row)
        btn_row.addWidget(self.add_dict_btn)
        btn_row.addWidget(self.remove_dict_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        return widget

    def _build_fillers_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        info = QLabel(
            "מילות מילוי שיוסרו אוטומטית מהטקסט (כמו 'אה', 'כאילו', 'um'). מילה לכל שורה."
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: #9ca3af;")
        layout.addWidget(info)

        inner_tabs = QTabWidget()
        self.filler_lists = {}
        for code in LANG_CODES:
            container = QWidget()
            v = QVBoxLayout(container)
            lst = QListWidget()
            v.addWidget(lst)

            btn_row = QHBoxLayout()
            add_btn = QPushButton("➕ הוסף")
            rm_btn = QPushButton("🗑 מחק נבחר")
            add_btn.clicked.connect(lambda _, c=code: self._add_filler(c))
            rm_btn.clicked.connect(lambda _, c=code: self._remove_filler(c))
            btn_row.addWidget(add_btn)
            btn_row.addWidget(rm_btn)
            btn_row.addStretch()
            v.addLayout(btn_row)

            self.filler_lists[code] = lst
            inner_tabs.addTab(container, LANG_DISPLAY[code])

        layout.addWidget(inner_tabs)
        return widget

    # ----------------------------- SIGNAL WIRING -----------------------------

    def _connect_signals(self):
        self.app.state_changed.connect(self._on_state_changed)
        self.app.info_changed.connect(self._on_info_changed)
        self.app.transcription_done.connect(self._on_transcription_done)
        self.app.error_occurred.connect(self._on_error)

    # ----------------------------- HANDLERS -----------------------------

    def _on_record_clicked(self):
        self.app.toggle_recording()

    def _on_save_clicked(self):
        new_config = self._gather_config()
        self.app.update_config(new_config)
        QMessageBox.information(self, "נשמר", "ההגדרות נשמרו בהצלחה.")
        self.hotkey_change_requested.emit()

    def _on_change_hotkey(self):
        self.hotkey_btn.setText("...לחץ צירוף")
        self.hotkey_btn.setEnabled(False)

        import threading
        import keyboard

        def capture():
            try:
                combo = keyboard.read_hotkey(suppress=False)
            except Exception:
                combo = None
            QTimer.singleShot(0, lambda: self._on_hotkey_captured(combo))

        threading.Thread(target=capture, daemon=True).start()

    def _on_hotkey_captured(self, combo):
        self.hotkey_btn.setText("שנה")
        self.hotkey_btn.setEnabled(True)
        if combo:
            self.hotkey_label.setText(combo)

    def _on_state_changed(self, state):
        self._set_state(state)

    def _on_info_changed(self, text):
        self.info_label.setText(text)

    def _on_transcription_done(self, raw, processed):
        self.last_raw_label.setText(raw or "(ריק)")
        self.last_processed_label.setText(processed or "(ריק)")

    def _on_error(self, msg):
        self.info_label.setText(f"⚠ {msg}")

    def _set_state(self, state):
        color = STATE_COLOR.get(state, "#6b7280")
        label = STATE_LABEL.get(state, state)
        self.status_label.setText(f"● {label}")
        self.status_label.setStyleSheet(f"color: {color};")
        btn_text = RECORD_BUTTON_TEXT.get(state, "🎤 לחץ להקלטה")
        self.record_btn.setText(btn_text)
        self.record_btn.setStyleSheet(self._button_style(color))
        self.record_btn.setEnabled(state not in (STATE_LOADING, STATE_TRANSCRIBING))

    @staticmethod
    def _button_style(color):
        return (
            f"QPushButton {{ background-color: {color}; color: white; border: none; "
            f"border-radius: 14px; padding: 14px; }} "
            f"QPushButton:hover {{ background-color: {color}; opacity: 0.85; }} "
            f"QPushButton:disabled {{ background-color: #4b5563; }}"
        )

    # ----------------------------- DICT / FILLERS HELPERS -----------------------------

    def _add_dict_row(self):
        row = self.dict_table.rowCount()
        self.dict_table.insertRow(row)
        self.dict_table.setItem(row, 0, QTableWidgetItem(""))
        self.dict_table.setItem(row, 1, QTableWidgetItem(""))
        self.dict_table.editItem(self.dict_table.item(row, 0))

    def _remove_dict_row(self):
        row = self.dict_table.currentRow()
        if row >= 0:
            self.dict_table.removeRow(row)

    def _add_filler(self, lang_code):
        text, ok = QInputDialog.getText(self, "מילת מילוי חדשה", "מילה:")
        if ok and text.strip():
            self.filler_lists[lang_code].addItem(text.strip())

    def _remove_filler(self, lang_code):
        lst = self.filler_lists[lang_code]
        row = lst.currentRow()
        if row >= 0:
            lst.takeItem(row)

    # ----------------------------- CONFIG <-> UI -----------------------------

    def _refresh_from_config(self):
        cfg = self.app.config

        idx = LANG_CODES.index(cfg.get("language", "he"))
        self.lang_combo.setCurrentIndex(idx)

        m = cfg.get("model_size", "large-v3")
        if m in MODEL_SIZES:
            self.model_combo.setCurrentIndex(MODEL_SIZES.index(m))

        dev = cfg.get("device", "auto")
        for i, (code, _) in enumerate(DEVICES):
            if code == dev:
                self.device_combo.setCurrentIndex(i)
                break

        self.hotkey_label.setText(cfg.get("hotkey", "ctrl+shift+space"))
        self.cb_fillers.setChecked(cfg.get("remove_filler_words", True))
        self.cb_dict.setChecked(cfg.get("use_custom_dictionary", True))

        # Dictionary
        self.dict_table.setRowCount(0)
        for src, tgt in cfg.get("custom_dictionary", {}).items():
            r = self.dict_table.rowCount()
            self.dict_table.insertRow(r)
            self.dict_table.setItem(r, 0, QTableWidgetItem(src))
            self.dict_table.setItem(r, 1, QTableWidgetItem(tgt))

        # Filler words
        filler_map = cfg.get("filler_words", {})
        for code, lst in self.filler_lists.items():
            lst.clear()
            for word in filler_map.get(code, []):
                lst.addItem(word)

    def _gather_config(self):
        # Dictionary from table
        dictionary = {}
        for r in range(self.dict_table.rowCount()):
            src_item = self.dict_table.item(r, 0)
            tgt_item = self.dict_table.item(r, 1)
            src = src_item.text().strip() if src_item else ""
            tgt = tgt_item.text().strip() if tgt_item else ""
            if src:
                dictionary[src] = tgt

        # Filler words from lists
        fillers = {}
        for code, lst in self.filler_lists.items():
            fillers[code] = [lst.item(i).text() for i in range(lst.count())]

        return {
            "language": self.lang_combo.currentData(),
            "model_size": self.model_combo.currentData(),
            "device": self.device_combo.currentData(),
            "hotkey": self.hotkey_label.text(),
            "remove_filler_words": self.cb_fillers.isChecked(),
            "use_custom_dictionary": self.cb_dict.isChecked(),
            "custom_dictionary": dictionary,
            "filler_words": fillers,
        }

    # ----------------------------- WINDOW BEHAVIOR -----------------------------

    def closeEvent(self, event):
        if self._force_quit:
            event.accept()
            return
        event.ignore()
        self.hide()
        self.closing.emit()

    def force_quit(self):
        self._force_quit = True
        self.close()


class TrayIcon(QSystemTrayIcon):
    open_requested = pyqtSignal()
    quit_requested = pyqtSignal()
    toggle_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_menu()
        self.setIcon(make_status_icon(STATE_COLOR[STATE_LOADING]))
        self.setToolTip("כלי הכתבה - טוען...")
        self.activated.connect(self._on_activated)

    def _build_menu(self):
        menu = QMenu()
        open_action = QAction("פתח חלון", menu)
        toggle_action = QAction("התחל/עצור הקלטה", menu)
        quit_action = QAction("יציאה", menu)

        open_action.triggered.connect(self.open_requested.emit)
        toggle_action.triggered.connect(self.toggle_requested.emit)
        quit_action.triggered.connect(self.quit_requested.emit)

        menu.addAction(open_action)
        menu.addAction(toggle_action)
        menu.addSeparator()
        menu.addAction(quit_action)
        self.setContextMenu(menu)

    def _on_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.open_requested.emit()

    def set_state(self, state):
        color = STATE_COLOR.get(state, "#6b7280")
        label = STATE_LABEL.get(state, state)
        self.setIcon(make_status_icon(color))
        self.setToolTip(f"כלי הכתבה - {label}")
