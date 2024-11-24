import sys
import os
import logging
import cv2
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtGui import QImage, QPixmap, QIcon
from PyQt5.QtCore import QTimer, Qt, QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

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

        # Timer für das Wegschreiben des Textes
        self.text_disappearance_timer = QTimer()
        self.text_disappearance_timer.timeout.connect(self.remove_text)

        # Timer für das Verzögerte Abspielen des Entfernungs-Sounds
        self.text_remove_sound_timer = QTimer()
        self.text_remove_sound_timer.timeout.connect(self.play_remove_sound)

        self.current_text_index = 0  # Index für die Textanimation
        self.full_text = "       \nPeharge Presents\n\nXc++\n                                            "  # Vollständiger Text
        self.text_display_time = 0  # Zeit, die der Text angezeigt wird
        self.text_animation_duration = 5000  # Textanimation 5 Sekunden lang
        self.text_display_duration = 5000  # Text wird für 5 Sekunden angezeigt
        self.text_disappearance_duration = 5000  # Text wird für 5 Sekunden weggeschrieben
        self.video_started = False  # Flag zum Überprüfen, ob das Video gestartet wurde

        # Initialize media players for sound effects
        self.text_sound_player = QMediaPlayer()
        text_sound_url = QUrl.fromLocalFile("C:/Users/julia/PycharmProjects/Xcpp/interface-digital-de-texto-text-digital-interface-218128.mp3")  # Pfad zur Typ-Schreib-Sounddatei
        self.text_sound_player.setMedia(QMediaContent(text_sound_url))

        self.text_remove_sound_player = QMediaPlayer()
        remove_sound_url = QUrl.fromLocalFile("C:/Users/julia/PycharmProjects/Xcpp/interface-digital-de-texto-text-digital-interface-218128.mp3")  # Pfad zur Ton-Datei beim Entfernen des Textes
        self.text_remove_sound_player.setMedia(QMediaContent(remove_sound_url))

        self.video_sound_player = QMediaPlayer()
        video_sound_url = QUrl.fromLocalFile("C:/Users/julia/PycharmProjects/Xcpp/bang-140381.mp3")  # Pfad zur Video-Sounddatei
        self.video_sound_player.setMedia(QMediaContent(video_sound_url))

    def initUI(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)  # Fensterrahmen entfernen
        self.showFullScreen()  # Fenster im Vollbildmodus anzeigen

        # Hintergrund transparent machen
        self.setAttribute(Qt.WA_TranslucentBackground, True)

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

        # Textanzeige (initial sichtbar)
        self.text_label = QLabel()
        self.text_label.setStyleSheet("font-size: 50px; color: white; font-family: 'Courier New';")  # Terminal-Stil
        self.text_label.setAlignment(Qt.AlignCenter)
        self.text_label.setVisible(True)
        self.layout.addWidget(self.text_label)

    def update_text(self):
        if self.current_text_index < len(self.full_text):
            # Zeige den Text Buchstabe für Buchstabe an
            current_text = self.full_text[:self.current_text_index + 1]
            self.text_label.setText(current_text)
            self.current_text_index += 1

            # Play typing sound immediately
            if self.current_text_index == 1:  # Play sound only once at the beginning
                self.text_sound_player.play()

        else:
            # Wenn die Textanimation abgeschlossen ist
            if self.text_display_time == 0:
                # Text vollständig angezeigt
                self.text_animation_timer.stop()
                self.text_display_time = self.text_display_duration

                # Start disappearance timer after displaying text for 5 seconds
                self.text_disappearance_timer.start(50)  # Update alle 50 ms
                self.video_start_timer.start(self.text_display_duration)  # Startet den Timer, um das Video zu starten

        if self.text_display_time > 0:
            self.text_display_time -= 50  # Reduziere die verbleibende Zeit alle 50 ms

            if self.text_display_time <= 0 and not self.video_started:
                self.start_video()

    def remove_text(self):
        if self.current_text_index == len(self.full_text):
            # Starte den Timer für das Abspielen des Entfernungs-Sounds nach 5 Sekunden
            self.text_remove_sound_timer.start(2600)

        if self.current_text_index > 0:
            # Entfernen Sie den letzten Buchstaben
            self.current_text_index -= 1
            current_text = self.full_text[:self.current_text_index]
            self.text_label.setText(current_text)
        else:
            # Wenn der gesamte Text entfernt wurde
            self.text_disappearance_timer.stop()
            self.text_label.setVisible(False)  # Verstecke den Text nach dem Wegschreiben

    def play_remove_sound(self):
        self.text_remove_sound_player.play()
        self.text_remove_sound_timer.stop()  # Stoppe den Timer nach dem Abspielen des Sounds

    def start_video(self):
        if not self.video_started:
            self.video_started = True
            self.text_label.setVisible(False)  # Verstecke den Text
            self.video_label = QLabel(self)
            self.video_label.setGeometry(self.rect())  # Video im Vollbildmodus
            self.video_label.show()

            self.frame_timer = QTimer()
            self.frame_timer.timeout.connect(self.update_frame)
            self.frame_timer.start(30)  # Update alle 30 ms

            # Timer für das automatische Schließen nach dem Video
            self.close_timer.start(20000)  # Beispielzeit: 20 Sekunden, anpassen, falls notwendig

            # Optional: Play background sound for the video
            self.video_sound_player.play()

    def update_frame(self):
        ret, frame = self.video_capture.read()
        if ret:
            # Resize frame to fit the screen while maintaining aspect ratio
            screen_size = self.size()
            height, width, _ = frame.shape
            aspect_ratio = width / height
            new_width = screen_size.width()
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
            self.video_label.setPixmap(
                pixmap.scaled(self.video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            # Video ist zu Ende
            self.video_capture.release()
            self.frame_timer.stop()
            self.video_label.setVisible(False)  # Video-Label ausblenden
            self.close_timer.start(2000)  # Schließe das Fenster nach 2 Sekunden


if __name__ == "__main__":
    app = QApplication(sys.argv)
    video_path = "C:/Users/julia/PycharmProjects/Xcpp/peharge-intro20001-0400.mkv"  # Video-Pfad
    player = VideoPlayer(video_path)
    player.show()
    sys.exit(app.exec_())
