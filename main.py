import sys
import threading
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

from ui.main_window import MainWindow
from core.protection import RealTimeProtection
from telegram.bot import poll_loop

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("ANTI-VURUS")
    
    # Запуск RT-защиты
    rtp = RealTimeProtection()
    rtp.start()
    
    # Запуск бота в фоне
    threading.Thread(target=poll_loop, daemon=True).start()
    
    win = MainWindow()
    win.show()
    
    exit_code = app.exec()
    rtp.stop()
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
