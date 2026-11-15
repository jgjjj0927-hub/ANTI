from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QMessageBox
from core.quarantine import list_quarantine, restore_file, delete_permanently

class QuarantineTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        
        self.list = QListWidget()
        self.list.setStyleSheet("""
            QListWidget { background: #0a0a0a; border: 1px solid #222; border-radius: 10px; padding: 5px;}
            QListWidget::item { padding: 10px; border-bottom: 1px solid #1a1a1a; color: white;}
        """)
        layout.addWidget(self.list, 1)

        btns = QHBoxLayout()
        btn_refresh = QPushButton("Обновить")
        btn_refresh.clicked.connect(self.refresh)
        btns.addWidget(btn_refresh)

        btn_restore = QPushButton("Восстановить")
        btn_restore.setStyleSheet("background: #00ff41; color: black;")
        btn_restore.clicked.connect(self._restore)
        btns.addWidget(btn_restore)

        btn_delete = QPushButton("Удалить навсегда")
        btn_delete.setStyleSheet("background: #ff3333; color: white;")
        btn_delete.clicked.connect(self._delete)
        btns.addWidget(btn_delete)
        layout.addLayout(btns)
        
        self.refresh()

    def refresh(self):
        self.list.clear()
        for i in list_quarantine():
            self.list.addItem(f"{i['name']} | {i['date_added'][:16]} | {i['path']}")

    def _restore(self):
        row = self.list.currentRow()
        if row >= 0 and restore_file(row):
            self.refresh()
            QMessageBox.information(self, "OK", "Файл восстановлен.")

    def _delete(self):
        row = self.list.currentRow()
        if row >= 0 and delete_permanently(row):
            self.refresh()
            QMessageBox.information(self, "OK", "Файл удален.")
