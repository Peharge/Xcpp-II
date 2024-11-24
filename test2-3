import sys
import os
import logging
import cv2
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtGui import QImage, QPixmap, QIcon, QPainterPath, QRegion
from PyQt5.QtCore import QTimer, Qt, QRectF

class VideoPlayer(QMainWindow):
    def __init__(self, video_path):
        super().__init__()
        self.video_path = video_path
        self.video_capture = cv2.VideoCapture(self.video_path)
        self.initUI()

        # Timer für Textanimation
        self.text_animation_timer = QTimer()
        self.text_animation_timer.timeout.connect(self.update_text)
        self.text_animation_timer.start(50)  # Text wird alle 50 ms aktualisiert

        # Timer für das Abspielen des Videos nach der Textanzeige
        self.video_start_timer = QTimer()
        self.video_start_timer.timeout.connect(self.start_video)

        # Timer für das automatische Schließen nach dem Video
        self.close_timer = QTimer()
        self.close_timer.timeout.connect(self.close)

        self.current_text_index = 0  # Index für die Textanimation
        self.full_text = "Peharge Presents\n\nXc++"  # Vollständiger Text
        self.text_display_time = 0  # Zeit, die der Text angezeigt wird
        self.text_animation_duration = 3000  # Textanimation 2 Sekunden lang
        self.text_display_duration = 5000  # Text wird für 5 Sekunden angezeigt
        self.video_started = False  # Flag zum Überprüfen, ob das Video gestartet wurde

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

        # Textanzeige (initial versteckt)
        self.text_label = QLabel()
        self.text_label.setStyleSheet("font-size: 50px; color: white; font-family: 'Courier New';")  # Terminal-Stil
        self.text_label.setAlignment(Qt.AlignCenter)
        self.text_label.setVisible(True)  # Text initial sichtbar
        self.layout.addWidget(self.text_label)

    def set_rounded_corners(self, radius):
        # Setzt eine runde Maske für das Fenster
        path = QPainterPath()
        rect = QRectF(self.rect())  # Konvertiere QRect in QRectF
        path.addRoundedRect(rect, radius, radius)
        mask = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(mask)

    def update_text(self):
        if self.current_text_index < len(self.full_text):
            # Zeige den Text Buchstabe für Buchstabe an
            current_text = self.full_text[:self.current_text_index + 1]
            self.text_label.setText(current_text)
            self.current_text_index += 1
        else:
            # Wenn die Textanimation abgeschlossen ist, starte den Timer für die Anzeige des Textes
            if self.text_display_time == 0:
                self.text_animation_timer.stop()
                self.text_display_time = self.text_display_duration
                self.video_start_timer.start(self.text_display_duration)  # Startet den Timer, um das Video zu starten

        if self.text_display_time > 0:
            self.text_display_time -= 50  # Reduziere die verbleibende Zeit alle 50 ms

            if self.text_display_time <= 0 and not self.video_started:
                self.start_video()

    def start_video(self):
        if not self.video_started:
            self.video_started = True
            self.text_label.setVisible(False)  # Verstecke den Text
            self.video_label = QLabel(self)
            self.video_label.setGeometry(0, 0, 800, 450)  # Video im Vollbildmodus
            self.video_label.setStyleSheet("background: black;")  # Hintergrund auf schwarz setzen
            self.video_label.show()

            self.frame_timer = QTimer()
            self.frame_timer.timeout.connect(self.update_frame)
            self.frame_timer.start(30)  # Update alle 30 ms

            # Timer für das automatische Schließen nach dem Video
            self.close_timer.start(20000)  # Beispielzeit: 20 Sekunden, anpassen, falls notwendig

    def update_frame(self):
        ret, frame = self.video_capture.read()
        if ret:
            # Resize frame to fit the width of 800px while maintaining aspect ratio
            window_width = 800
            height, width, _ = frame.shape
            aspect_ratio = width / height
            new_width = window_width
            new_height = int(new_width / aspect_ratio)

            frame = cv2.resize(frame, (new_width, new_height))

            # Convert the frame from BGR to RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Convert the frame to QImage
            height, width, _ = frame.shape
            bytes_per_line = 3 * width
            q_img = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_img)

            # Scale pixmap to fit the label
            self.video_label.setPixmap(pixmap.scaled(self.video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            # Video ist zu Ende
            self.video_capture.release()
            self.frame_timer.stop()
            self.video_label.setVisible(False)  # Video-Label ausblenden
            self.close_timer.start(2000)  # Schließe das Fenster nach 2 Sekunden

if __name__ == "__main__":
    app = QApplication(sys.argv)
    video_path = "C:/Users/julia/PycharmProjects/Xcpp/peharge-intro20001-0400.mkv" #peharge-intro4.5.mp4 / peharge-intro20001-0400.mkv
    player = VideoPlayer(video_path)
    player.show()
    sys.exit(app.exec_())
