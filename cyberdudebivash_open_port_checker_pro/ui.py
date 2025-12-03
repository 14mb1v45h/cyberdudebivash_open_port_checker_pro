import sys
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from pathlib import Path
import json

class ScanThread(QThread):
    update_progress = pyqtSignal(int)
    update_results = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, target, ports, is_pro, use_shodan):
        super().__init__()
        self.target = target
        self.ports = ports
        self.is_pro = is_pro
        self.use_shodan = use_shodan

    def run(self):
        from scanner import run_scan
        run_scan(
            self.target,
            self.ports,
            self.is_pro,
            self.update_progress.emit,
            self.update_results.emit,
            self.use_shodan
        )
        self.finished.emit()


class MainWindow(QMainWindow):
    def __init__(self, is_pro=False):
        super().__init__()
        self.setWindowTitle("CYBERDUDEBIVASH OPEN PORT CHECKER PRO v1.0")
        self.setGeometry(100, 100, 900, 700)
        self.is_pro = is_pro

        container = QWidget()
        layout = QVBoxLayout()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Logo
        logo = QLabel()
        try:
            pixmap = QPixmap("resources/skull.png").scaled(120, 120, Qt.AspectRatioMode.KeepAspectRatio)
            logo.setPixmap(pixmap)
        except:
            logo.setText("CYBERDUDEBIVASH")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo)

        # Target
        self.target = QLineEdit("127.0.0.1")
        layout.addWidget(QLabel("Target:"))
        layout.addWidget(self.target)

        # Ports
        self.ports = QLineEdit("22,80,443,3389,445")
        layout.addWidget(QLabel("Ports:"))
        layout.addWidget(self.ports)

        # Shodan (Pro)
        if self.is_pro:
            h = QHBoxLayout()
            self.key_input = QLineEdit()
            self.key_input.setEchoMode(QLineEdit.EchoMode.Password)
            save = QPushButton("Save Key")
            save.clicked.connect(self.save_key)
            self.shodan_on = QCheckBox("Enable Shodan Intel")
            h.addWidget(QLabel("Shodan Key:"))
            h.addWidget(self.key_input)
            h.addWidget(save)
            h.addWidget(self.shodan_on)
            layout.addLayout(h)

        # Start button
        btn = QPushButton("START SCAN")
        btn.clicked.connect(self.start_scan)
        layout.addWidget(btn)

        # Progress
        self.progress = QProgressBar()
        layout.addWidget(self.progress)

        # Output
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        layout.addWidget(self.output)

        # Keep thread reference
        self.thread = None

    def save_key(self):
        key = self.key_input.text().strip()
        if not key:
            return
        config = Path.home() / ".cyberdudebivash"
        config.mkdir(exist_ok=True)
        with open(config / "config.json", "w") as f:
            json.dump({"shodan_key": key}, f)
        QMessageBox.information(self, "Success", "Key saved!")

    def start_scan(self):
        t = self.target.text().strip()
        p = self.ports.text().strip()
        if not t or not p:
            return

        self.output.clear()
        use_shodan = self.is_pro and hasattr(self, 'shodan_on') and self.shodan_on.isChecked()

        # KEEP THREAD ALIVE (THIS FIXES YOUR CRASH)
        self.thread = ScanThread(t, p, self.is_pro, use_shodan)
        self.thread.update_progress.connect(self.progress.setValue)
        self.thread.update_results.connect(self.output.append)
        self.thread.start()


def run_ui():
    app = QApplication(sys.argv)
    win = MainWindow("--pro" in sys.argv)
    win.show()
    sys.exit(app.exec())
