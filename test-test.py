import sys
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from PyQt5.QtGui import QPixmap, QPalette, QColor, QPainterPath, QRegion
from PyQt5.QtCore import Qt, QTimer, QRectF

class SplashScreen(QWidget):
    def __init__(self, image_path, logo_path):
        super().__init__()

        self.setWindowFlags(Qt.FramelessWindowHint)  # Fensterrahmen entfernen
        self.setGeometry(607, 323, 706, 434)  # Fenstergröße und Position festlegen

        # Hintergrundfarbe auf weiß setzen
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(Qt.white))
        self.setPalette(palette)

        # Layout und Label für das Bild erstellen
        layout = QVBoxLayout()
        self.label = QLabel(self)
        pixmap = QPixmap(image_path)
        self.label.setPixmap(pixmap.scaled(706, 434, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        layout.addWidget(self.label)
        self.setLayout(layout)

        # Logo hinzufügen und oben rechts positionieren
        self.logo_label = QLabel(self)
        logo_pixmap = QPixmap(logo_path).scaled(30, 30, Qt.KeepAspectRatio, Qt.SmoothTransformation)  # Skaliere das Logo auf 30x30 Pixel
        self.logo_label.setPixmap(logo_pixmap)
        logo_x = self.width() - logo_pixmap.width() - 10  # Abstand von 30 Pixel vom rechten Rand
        logo_y = 10  # Abstand von 30 Pixel vom oberen Rand
        self.logo_label.setGeometry(logo_x, logo_y, logo_pixmap.width(), logo_pixmap.height())
        self.logo_label.raise_()  # Sicherstellen, dass das Logo über dem Bild liegt

        # Erstellen einer Maske für abgerundete Ecken
        self.set_rounded_corners(20)  # 20 Pixel Radius für die abgerundeten Ecken

        # Timer erstellen, um das Fenster nach 15 Sekunden zu schließen
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.close_splash)
        self.timer.start(15000)  # Timer auf 15 Sekunden setzen

    def set_rounded_corners(self, radius):
        # Erstellen eines QPainterPath für die abgerundeten Ecken
        path = QPainterPath()
        rect = QRectF(self.rect())  # Konvertieren von QRect zu QRectF
        path.addRoundedRect(rect, radius, radius)

        # Die Region aus dem QPainterPath erstellen
        region = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region)

    def close_splash(self):
        self.timer.stop()
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    splash = SplashScreen(
        "C:/Users/julia/PycharmProjects/Xcpp/xc++2.png",
        "C:/Users/julia/OneDrive - Gewerbeschule Lörrach/Pictures/software/peharge-logo3.6.ico"  # Pfad zum Logo
    )
    splash.show()

    sys.exit(app.exec_())
