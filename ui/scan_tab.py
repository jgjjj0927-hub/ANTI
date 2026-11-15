from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QProgressBar, QListWidget, QListWidgetItem, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
import threading
from core.scanner import ScanEngine
from core.quarantine import add_to_quarantine

class ScanTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.target = ""
        layout = QVBoxLayout(self)
        
        # Верхняя панель
        top = QHBoxLayout()
        self.path_lbl = QLabel("Цель: не выбрана")
        self.path_lbl.setStyleSheet("color: #888;")
        top.addWidget(self.path_lbl, 1)
        
        self.btn_folder = QPushButton("Выбрать папку")
        self.btn_folder.clicked.connect(self._choose_folder)
        top.addWidget(self.btn_folder)

        self.btn_file = QPushButton("Выбрать файл")
        self.btn_file.clicked.connect(self._choose_file)
        top.addWidget(self.btn_file)
        
        layout.addLayout(top)

        # Прогресс
        self.progress = QProgressBar()
        self.progress.setStyleSheet("""
            QProgressBar { border: 1px solid #333; border-radius: 8px; background: #111; text-align: center; color: white;}
            QProgressBar::chunk { background: #00ff41; border-radius: 8px; }
        """)
        self.progress.setValue(0)
        layout.addWidget(self.progress)

        # Результаты
        self.results = QListWidget()
        self.results.setStyleSheet("""
            QListWidget { background: #0a0a0a; border: 1px solid #222; border-radius: 10px; padding: 5px;}
            QListWidget::item { padding: 10px; border-bottom: 1px solid #1a1a1a; color: white;}
            QListWidget::item:selected { background: #1a1a1a; }
        """)
        layout.addWidget(self.results, 1)

        # Кнопки действий
        btns = QHBoxLayout()
        self.btn_scan = QPushButton("Сканировать")
        self.btn_scan.setStyleSheet("background: #00ff41; color: black; font-weight: bold; border-radius: 8px; padding: 10px;")
        self.btn_scan.clicked.connect(self._start_scan)
        btns.addWidget(self.btn_scan)

        self.btn_stop = QPushButton("Стоп")
        self.btn_stop.setStyleSheet("background: #ff3333; color: white; border-radius: 8px; padding: 10px;")
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self._stop_scan)
        btns.addWidget(self.btn_stop)

        self.btn_quarantine = QPushButton("В карантин")
        self.btn_quarantine.setStyleSheet("background: #222; color: white; border: 1px solid #444; border-radius: 8px; padding: 10px;")
        self.btn_quarantine.clicked.connect(self._to_quarantine)
        btns.addWidget(self.btn_quarantine)
        layout.addLayout(btns)

        # Ядро сканера
        self.engine = ScanEngine(self._on_progress, self._on_found, self._on_done)
        
        # Сигналы для потоков
        self.engine.found_cb = lambda x: self._emit_found(x)
        self.found_signal = pyqtSignal(dict)
        self.found_signal.connect(self._add_result)

    def _emit_found(self, threat):
        self.found_signal.emit(threat)

    def _choose_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Выберите папку")
        if path:
            self.target = path
            self.path_lbl.setText(f"Цель: {path}")

    def _choose_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Выберите файл")
        if path:
            self.target = path
            self.path_lbl.setText(f"Цель: {path}")

    def _start_scan(self):
        if not self.target:
            QMessageBox.warning(self, "Ошибка", "Выберите папку или файл!")
            return
        self.results.clear()
        self.progress.setValue(0)
        self.btn_scan.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.engine.start(self.target)

    def _stop_scan(self):
        self.engine.stop()
        self.btn_scan.setEnabled(True)
        self.btn_stop.setEnabled(False)

    def _on_progress(self, val):
        self.progress.setValue(val)

    def _on_found(self, threat):
        pass # Заменено на сигнал

    def _add_result(self, threat):
        item = QListWidgetItem(f"[{threat['severity']}] {threat['name']} — {threat['reason']}")
        item.setData(Qt.ItemDataRole.UserRole, threat)
        if threat['severity'] == "Высокая":
            item.setForeground(Qt.GlobalColor.red)
        self.results.addItem(item)

    def _on_done(self, found, stopped):
        self.btn_scan.setEnabled(True)
        self.btn_stop.setEnabled(False)
        if stopped:
            self.results.addItem("— Остановлено —")
        else:
            self.progress.setValue(100)
            self.results.addItem(f"— Завершено. Найдено: {len(found)} —")

    def _to_quarantine(self):
        item = self.results.currentItem()
        if not item: return
        data = item.data(Qt.ItemDataRole.UserRole)
        if data and add_to_quarantine(data):
            QMessageBox.information(self, "Карантин", f"Файл {data['name']} перемещен в карантин.")
            self.results.takeItem(self.results.row(item))
