import sys
import os
import logging
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QWidget, QPushButton
from PyQt5.QtGui import QIcon, QPainterPath, QRegion
from PyQt5.QtCore import QTimer, Qt

class CustomWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

        # Timer für automatisches Schließen nach 15 Sekunden
        self.close_timer = QTimer()
        self.close_timer.timeout.connect(self.close)
        self.close_timer.start(15000)  # Timer auf 15 Sekunden setzen

    def initUI(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)  # Fensterrahmen entfernen
        self.setGeometry(560, 315, 800, 450)  # Fenstergröße und Position festlegen

        # Hintergrund transparent machen
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setStyleSheet("background: transparent;")  # Hintergrundfarbe auf transparent setzen

        # Abgerundete Ecken setzen
        self.set_rounded_corners(30)  # 30 Pixel Radius für die abgerundeten Ecken

        # Logo hinzufügen und oben rechts positionieren
        icon_path = "C:\\Users\\julia\\OneDrive - Gewerbeschule Lörrach\\Pictures\\software\\peharge-logo3.6.ico"
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            logging.error(f"Icon file not found at: {icon_path}")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Beispiel für statischen Inhalt
        self.label = QLabel("Willkommen zu meiner Anwendung!")
        self.label.setStyleSheet("font-size: 24px; color: white;")  # Beispiel Styling
        self.layout.addWidget(self.label)

        self.button = QPushButton("Klick mich")
        self.layout.addWidget(self.button)

    def set_rounded_corners(self, radius):
        # Setzt eine runde Maske für das Fenster
        path = QPainterPath()
        path.addRoundedRect(self.rect(), radius, radius)
        mask = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(mask)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CustomWindow()
    window.show()
    sys.exit(app.exec_())
