import sys
import os
import logging
import cv2
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtGui import QImage, QPixmap, QIcon
from PyQt5.QtCore import QTimer, Qt, QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

# Logging-Konfiguration
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class VideoPlayer(QMainWindow):
    def __init__(self, video_path):
        super().__init__()
        self.video_path = video_path
        self.video_capture = cv2.VideoCapture(self.video_path)
        self.setup_ui()
        self.setup_timers()
        self.setup_media_players()
        self.initialize_text()

    def setup_ui(self):
        self.setWindowTitle("Xc++")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.showFullScreen()
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        icon_path = "C:\\Users\\julia\\OneDrive - Gewerbeschule Lörrach\\Pictures\\software\\peharge-logo3.6.ico"
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            logging.error(f"Icon file not found at: {icon_path}")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.text_label = QLabel()
        self.text_label.setStyleSheet("font-size: 50px; color: white; font-family: 'Courier New';")
        self.text_label.setAlignment(Qt.AlignCenter)
        self.text_label.setVisible(True)
        self.layout.addWidget(self.text_label)

    def setup_timers(self):
        self.text_animation_timer = QTimer()
        self.text_animation_timer.timeout.connect(self.update_text)
        self.text_animation_timer.start(50)

        self.text_animation_timer2 = QTimer()
        self.text_animation_timer2.timeout.connect(self.update_text2)
        self.text_animation_timer2.start(15000)

        self.video_start_timer = QTimer()
        self.video_start_timer.timeout.connect(self.start_video)

        self.close_timer = QTimer()
        self.close_timer.timeout.connect(self.close)

        self.text_disappearance_timer = QTimer()
        self.text_disappearance_timer.timeout.connect(self.remove_text)

        self.text_disappearance_timer2 = QTimer()
        self.text_disappearance_timer2.timeout.connect(self.remove_text2)

        self.text_remove_sound_timer = QTimer()
        self.text_remove_sound_timer.timeout.connect(self.play_remove_sound)

    def setup_media_players(self):
        self.text_sound_player = self.create_media_player(
            "C:/Users/julia/PycharmProjects/Xcpp/interface-digital-de-texto-text-digital-interface-218128.mp3")
        self.text_remove_sound_player = self.create_media_player(
            "C:/Users/julia/PycharmProjects/Xcpp/interface-digital-de-texto-text-digital-interface-218128.mp3")
        self.video_sound_player = self.create_media_player("C:/Users/julia/PycharmProjects/Xcpp/bang-140381.mp3")

    def create_media_player(self, file_path):
        player = QMediaPlayer()
        if os.path.exists(file_path):
            player.setMedia(QMediaContent(QUrl.fromLocalFile(file_path)))
        else:
            logging.error(f"Media file not found at: {file_path}")
        return player

    def initialize_text(self):
        self.current_text_index = 0
        self.current_text_index2 = 0
        self.full_text = "        \nCuriosity Project\n\n2025\n                                            "
        self.full_text2 = "\nPeharge presents\n\nXc++\n                                            "
        self.text_display_time = 0
        self.text_animation_duration = 5000
        self.text_display_duration = 5000
        self.text_disappearance_duration = 5000
        self.text_display_time2 = 0
        self.text_animation_duration2 = 5000
        self.text_display_duration2 = 5000
        self.text_disappearance_duration2 = 5000
        self.video_started = False
        self.showing_first_text = True

    def update_text(self):
        if self.current_text_index < len(self.full_text):
            self.text_label.setText(self.full_text[:self.current_text_index + 1])
            self.current_text_index += 1
            if self.current_text_index == 1:
                self.text_sound_player.play()
        else:
            if self.text_display_time == 0:
                self.text_animation_timer.stop()
                self.text_display_time = self.text_display_duration
                self.text_disappearance_timer.start(50)
        if self.text_display_time > 0:
            self.text_display_time -= 50
            if self.text_display_time <= 0 and not self.video_started and self.showing_first_text:
                self.remove_text()
                self.showing_first_text = False

    def update_text2(self):
        if self.current_text_index2 < len(self.full_text2):
            self.text_label.setVisible(True)
            self.text_label.setText(self.full_text2[:self.current_text_index2 + 1])
            self.current_text_index2 += 1
            if self.current_text_index2 == 1:
                self.text_sound_player.play()
        else:
            if self.text_display_time2 == 0:
                self.text_animation_timer2.stop()
                self.text_display_time2 = self.text_display_duration2
                self.text_disappearance_timer2.start(50)
                self.video_start_timer.start(self.text_display_duration2)
        if self.text_display_time2 > 0:
            self.text_display_time2 -= 50
            if self.text_display_time2 <= 0 and not self.video_started:
                self.start_video()

    def remove_text(self):
        if self.current_text_index == len(self.full_text):
            self.text_remove_sound_timer.start(2600)
        if self.current_text_index > 0:
            self.current_text_index -= 1
            self.text_label.setText(self.full_text[:self.current_text_index])
        else:
            self.text_disappearance_timer.stop()
            self.text_label.setVisible(False)
            self.text_animation_timer2.start(50)

    def remove_text2(self):
        if self.current_text_index2 == len(self.full_text2):
            self.text_remove_sound_timer.start(2600)
        if self.current_text_index2 > 0:
            self.current_text_index2 -= 1
            self.text_label.setText(self.full_text2[:self.current_text_index2])
        else:
            self.text_disappearance_timer2.stop()
            self.text_label.setVisible(False)

    def play_remove_sound(self):
        self.text_remove_sound_player.play()
        self.text_remove_sound_timer.stop()

    def start_video(self):
        if not self.video_started:
            self.video_started = True
            self.text_label.setVisible(False)
            self.video_label = QLabel(self)
            self.video_label.setGeometry(self.rect())
            self.video_label.show()
            self.frame_timer = QTimer()
            self.frame_timer.timeout.connect(self.update_frame)
            self.frame_timer.start(30)
            self.close_timer.start(20000)
            self.video_sound_player.play()

    def update_frame(self):
        ret, frame = self.video_capture.read()
        if ret:
            screen_size = self.size()
            height, width, _ = frame.shape
            aspect_ratio = width / height
            new_width = screen_size.width()
            new_height = int(new_width / aspect_ratio)
            frame = cv2.resize(frame, (new_width, new_height))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, _ = frame.shape
            bytes_per_line = 3 * width
            q_img = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_img)
            self.video_label.setPixmap(
                pixmap.scaled(self.video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.video_capture.release()
            self.frame_timer.stop()
            self.video_label.setVisible(False)
            self.close_timer.start(2000)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    video_path = "C:/Users/julia/PycharmProjects/Xcpp/peharge-intro20001-0400.mkv"
    if not os.path.exists(video_path):
        logging.error(f"Video file not found at: {video_path}")
        sys.exit(1)
    player = VideoPlayer(video_path)
    player.show()
    sys.exit(app.exec_())
