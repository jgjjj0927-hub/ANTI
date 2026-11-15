from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from core.config import APP_NAME, APP_VERSION, get_pc_name, get_hwid

class AboutTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        v = QVBoxLayout(self)
        v.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        v.addWidget(QLabel(f"<h1>{APP_NAME} {APP_VERSION}</h1>"))
        v.addWidget(QLabel("Демонстрационный антивирус. Все функции — симуляция."))
        v.addWidget(QLabel(f"🖥️ Компьютер: {get_pc_name()}"))
        v.addWidget(QLabel(f"🔑 HWID: {get_hwid()}"))
        
        site_lbl = QLabel('🌐 Официальный сайт: <a href="https://jgjjj0927-hub.github.io/ANTO/" style="color:#00ff41;">jgjjj0927-hub.github.io/ANTO</a>')
        site_lbl.setOpenExternalLinks(True)
        v.addWidget(site_lbl)
        
        v.addWidget(QLabel("🛠 Поддержка: @chameleonAnti"))
        v.addStretch(1)
