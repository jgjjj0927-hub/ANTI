from PyQt6.QtWidgets import QWidget, QVBoxLayout, QCheckBox, QPushButton, QLabel
from core.config import load_config, save_config
from ui.approval_dialog import ApprovalDialog

class SettingsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cfg = load_config()
        
        layout = QVBoxLayout(self)
        
        self.rt_cb = QCheckBox("Защита в реальном времени (RT)")
        self.rt_cb.setChecked(self.cfg.get("rt_enabled", True))
        self.rt_cb.toggled.connect(self._save_rt)
        layout.addWidget(self.rt_cb)

        # Симуляция запроса от админа
        btn_approve_demo = QPushButton("Запросить изменение у пользователя (Демо)")
        btn_approve_demo.clicked.connect(self._show_approval)
        layout.addWidget(btn_approve_demo)
        layout.addStretch()

    def _save_rt(self, val):
        self.cfg["rt_enabled"] = val
        save_config(self.cfg)

    def _show_approval(self):
        dlg = ApprovalDialog("настройки защиты")
        if dlg.exec():
            self.rt_cb.setChecked(True)
