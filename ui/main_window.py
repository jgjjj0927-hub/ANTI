from PyQt6.QtWidgets import QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from ui.scan_tab import ScanTab
from ui.quarantine_tab import QuarantineTab
from ui.settings import SettingsTab
from ui.about_tab import AboutTab

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ANTI-VURUS ADMIN PANEL")
        self.resize(900, 650)
        
        # Темный стиль (как на скринах)
        self.setStyleSheet("""
            QMainWindow, QWidget { background-color: #0a0a0a; color: white; font-family: 'Segoe UI', Arial; }
            QLabel { color: white; }
            QPushButton { background-color: #1a1a1a; color: white; border: 1px solid #333; border-radius: 8px; padding: 8px 15px; }
            QPushButton:hover { background-color: #252525; }
            QCheckBox { color: white; font-size: 14px; }
            QTabWidget::pane { border: 1px solid #222; background: #111; border-radius: 10px; margin: 5px; }
            QTabBar::tab { background: #0a0a0a; color: #888; padding: 10px 20px; border: 1px solid #222; border-radius: 8px; margin: 2px; }
            QTabBar::tab:selected { background: #1a1a1a; color: #00ff41; font-weight: bold; border: 1px solid #333; }
        """)

        central = QWidget()
        layout = QVBoxLayout(central)
        
        header = QLabel("ANTI-VURUS")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: white; padding: 10px;")
        layout.addWidget(header)

        tabs = QTabWidget()
        tabs.addTab(ScanTab(), "Сканирование")
        tabs.addTab(QuarantineTab(), "Карантин")
        tabs.addTab(SettingsTab(), "Настройки")
        tabs.addTab(AboutTab(), "О программе")
        
        layout.addWidget(tabs)
        self.setCentralWidget(central)
