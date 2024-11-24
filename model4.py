"""

(c)Peharge

"""

import logging

logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

from PyQt5.QtWidgets import QSpacerItem, QSizePolicy
from PyQt5.QtGui import QImage
import soundfile as sf
import whisper
from TTS.api import TTS
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts
from PyQt5.QtGui import QPainterPath, QRegion
from PyQt5.QtCore import QRectF
import ollama
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPen
import datetime
from PIL import Image
import psutil
import cv2
import logging
import sounddevice as sd
from PyQt5.QtWidgets import QGroupBox, QFormLayout, QSlider, QMessageBox, QComboBox
import torch
import tensorflow as tf
import pandas as pd
import pygame
import numpy as np
from transformers import __version__ as transformers_version
import time
import os
import ctypes
from PyQt5.QtWidgets import QScrollArea,QGraphicsDropShadowEffect
from PyQt5.QtGui import QPixmap, QImageReader, QPainter, QBrush, QColor, QLinearGradient
from PyQt5.QtCore import QSize, QRect
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QLabel, QProgressBar, QFrame
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtSvg import QSvgWidget
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl

class AudioThread(QThread):
    audio_signal = pyqtSignal(np.ndarray)

    def __init__(self, parent=None):
        super().__init__(parent)

    def run(self):
        try:
            fs = 16000
            silence_threshold = 0.01
            silence_duration = 1
            recording = []

            while True:
                snippet = sd.rec(int(silence_duration * fs), samplerate=fs, channels=1, dtype='float32')
                sd.wait()
                recording.append(snippet)

                volume = np.sqrt(np.mean(snippet**2))

                if volume < silence_threshold:
                    break

            final_recording = np.concatenate(recording, axis=0)
            self.audio_signal.emit(np.squeeze(final_recording))

        except Exception as e:
            logging.error(f"Error in AudioThread: {e}")



class CameraThread(QThread):
    frame_signal = pyqtSignal(np.ndarray)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.running = True
        self.fps = 120
        self.box_sizex = 800
        self.box_sizey = 600
        self.box_color = (255, 255, 255)
        self.corner_length = 35

    def run(self):
        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                logging.error("Could not open video device")
                return

            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 3840)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 2160)
            cap.set(cv2.CAP_PROP_FPS, self.fps)

            cap.set(cv2.CAP_PROP_EXPOSURE, -6)
            cap.set(cv2.CAP_PROP_AUTO_WB, 1)
            cap.set(cv2.CAP_PROP_GAIN, 0)

            while self.running:
                ret, frame = cap.read()
                if ret:
                    processed_frame = self.process_image(frame)

                    self.frame_signal.emit(processed_frame)
                else:
                    logging.error("Could not read frame")
                    break

            cap.release()
        except Exception as e:
            logging.error(f"Error in CameraThread: {e}")

    def stop(self):
        self.running = False

    def process_image(self, frame):
        height, width = frame.shape[:2]
        center_x, center_y = width // 2, height // 2

        start_x = center_x - self.box_sizex // 2
        start_y = center_y - self.box_sizey // 2
        end_x = start_x + self.box_sizex
        end_y = start_y + self.box_sizey

        frame_with_box = frame.copy()
        self.draw_box_with_corners(frame_with_box, (start_x, start_y), (end_x, end_y), self.box_color, self.corner_length)
        return frame_with_box

    def draw_box_with_corners(self, img, start_point, end_point, color, corner_length):
        x1, y1 = start_point
        x2, y2 = end_point

        cv2.line(img, (x1, y1), (x1 + corner_length, y1), color, 2)
        cv2.line(img, (x1, y1), (x1, y1 + corner_length), color, 2)

        cv2.line(img, (x2, y1), (x2 - corner_length, y1), color, 2)
        cv2.line(img, (x2, y1), (x2, y1 + corner_length), color, 2)

        cv2.line(img, (x1, y2), (x1 + corner_length, y2), color, 2)
        cv2.line(img, (x1, y2), (x1, y2 - corner_length), color, 2)

        cv2.line(img, (x2, y2), (x2 - corner_length, y2), color, 2)
        cv2.line(img, (x2, y2), (x2, y2 - corner_length), color, 2)

    def save_image(self, image):
        image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

        current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        image_path = f"C:/Users/julia/PycharmProjects/Xcpp/img/image_{current_time}.png"
        image_pil.save(image_path)



class SettingsWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setGeometry(1200, 50, 300, 300)
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.init_ui()
        self.player = QMediaPlayer()

    def init_ui(self):
        font = QFont('Segoe UI', 12)
        self.setFont(font)

        main_layout = QVBoxLayout()
        main_frame = QFrame(self)
        main_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.7);
                border-radius: 15px;
                box-shadow: 0px 0px 15px rgba(0, 0, 0, 0.5);
            }
        """)
        main_frame_layout = QVBoxLayout(main_frame)

        title_layout = QHBoxLayout()
        title_label = QLabel("Settings")
        title_label.setStyleSheet("color: #000000; font-size: 16px; font-weight: bold; background-color: rgba(255, 255, 255, 0);")
        title_layout.addWidget(title_label)
        close_button = QPushButton("×")
        close_button.clicked.connect(self.play_sound_2)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #C0392B;
                color: #FFFFFF;
                border: none;
                border-radius: 10px;
                width: 30px;
                height: 30px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #E74C3C;
            }
        """)
        close_button.clicked.connect(self.close)
        title_layout.addStretch()
        title_layout.addWidget(close_button)

        main_frame_layout.addLayout(title_layout)

        general_group = QGroupBox("General settings")
        general_group.setStyleSheet("""
            QGroupBox {
                background-color: rgba(255, 255, 255, 0);
                font-weight: bold;
                color: #000000;
                border-radius: 10px;
                margin-top: 10px;
            }
            QGroupBox::title {
                background-color: rgba(255, 255, 255, 0);
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QLabel {
                font-size: 12px;
                background-color: rgba(255, 255, 255, 0);
                color: #000000;
            }
            QSlider {
                background-color: rgba(255, 255, 255, 0);
            }
            QSlider::groove:horizontal {
                height: 6px;
                background: #000000;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                border: 3px solid #000000;
                width: 15px;  /* Breite des Handles */
                height: 15px; /* Höhe des Handles, gleich der Breite für einen Kreis */
                margin: -7px 0;  /* Platz um den Handle herum, kann je nach Bedarf angepasst werden */
                border-radius: 7px;  /* Radius für den Kreis, sollte die Hälfte von width/height sein */
                background-color: rgba(255, 255, 255, 0);  /* Hintergrundfarbe, transparent */
            }
            QSlider::add-page:horizontal {
                background-color: rgba(255, 255, 255, 0);
            }
            QSlider::sub-page:horizontal {
                background-color: rgba(255, 255, 255, 0);
            }
            QComboBox {
                background-color: #000000;
                border: 1px solid #5D6D7E;
                border-radius: 5px;
                padding: 5px;
                color: #ffffff;
            }
            QComboBox QAbstractItemView {
                background-color: #000000;
                border: 1px solid #5D6D7E;
                border-radius: 5px;
                padding: 5px;
                color: #ffffff;
            }
            QComboBox::down-arrow {
                image: url(C:/Users/julia/PycharmProjects/Xcpp/down.svg);
                width: 15px;
                height: 15px;
            }
            QListWidget {
                background-color: #000000;
                padding: 20px;
                border: 2px solid #4a4a4a;
                border-radius: 5px;
                color: #ffffff;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 2px solid #4a4a4a;
                color: #ffffff;
            }
            QListWidget::item:hover {
                border-bottom: 3px solid #0078d7;
            }
            QListWidget::item:selected {
                background-color: #0078d7;
                border-bottom: 3px solid #0078d7;
            }
            QScrollBar:vertical {
                background-color: #000000; /* Farbe der Zieh-Leiste */
                width: 10px;
                border: none; /* Entfernt eventuelle Ränder */
            }

            QScrollBar::handle:vertical {
                background-color: #ffffff; /* Farbe der Zieh-Leiste */
                min-height: 20px;
                border-radius: 5px;
            }

            QScrollBar::add-line:vertical {
                background: none;
            }

            QScrollBar::sub-line:vertical {
                background: none;
            }

            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
                background: none;
            }

            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        general_layout = QFormLayout()

        self.brightness_slider = QSlider(Qt.Horizontal)
        self.brightness_slider.setRange(0, 100)
        self.brightness_slider.setValue(50)
        general_layout.addRow(QLabel("brightness:"), self.brightness_slider)

        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        general_layout.addRow(QLabel("volume:"), self.volume_slider)

        self.contrast_slider = QSlider(Qt.Horizontal)
        self.contrast_slider.setRange(0, 100)
        self.contrast_slider.setValue(50)
        general_layout.addRow(QLabel("contrast:"), self.contrast_slider)

        self.saturation_slider = QSlider(Qt.Horizontal)
        self.saturation_slider.setRange(0, 100)
        self.saturation_slider.setValue(50)
        general_layout.addRow(QLabel("Color saturation:"), self.saturation_slider)

        self.mic_volume_slider = QSlider(Qt.Horizontal)
        self.mic_volume_slider.setRange(0, 100)
        self.mic_volume_slider.setValue(50)
        general_layout.addRow(QLabel("Microphone volume:"), self.mic_volume_slider)

        self.language_dropdown = QComboBox()
        self.language_dropdown.addItems(["German", "English", "Spanish", "French"])
        self.language_dropdown.setCurrentText("English")
        general_layout.addRow(QLabel("Language:"), self.language_dropdown)

        self.theme_dropdown = QComboBox()
        self.theme_dropdown.addItems(["Light", "Dark", "Blue", "Green"])
        general_layout.addRow(QLabel("Theme:"), self.theme_dropdown)

        self.font_size_slider = QSlider(Qt.Horizontal)
        self.font_size_slider.setRange(6, 18)
        self.font_size_slider.setValue(12)
        general_layout.addRow(QLabel("Font size:"), self.font_size_slider)

        self.audio_device_dropdown = QComboBox()
        devices = sd.query_devices()
        for device in devices:
            if device['max_input_channels'] > 0:
                self.audio_device_dropdown.addItem(device['name'])
        general_layout.addRow(QLabel("Audio input device:"), self.audio_device_dropdown)

        ram = psutil.virtual_memory().total / (1024 ** 3)

        disk = psutil.disk_usage('/').total / (1024 ** 3)

        cpu_threads = psutil.cpu_count()

        try:
            import pyopencl as cl
            platforms = cl.get_platforms()
            gpus = [device.name for platform in platforms for device in platform.get_devices()]
            gpu = ', '.join(gpus)
        except ImportError:
            gpu = "Not available (OpenCL not installed)"

        cpu_model = platform.processor()

        system_info = platform.system() + " " + platform.release()

        general_layout.addRow(QLabel(f""))
        general_layout.addRow(QLabel(f"RAM: <span style='color: blue;'>{ram:.2f} GB</span>"))
        general_layout.addRow(QLabel(f"Number of Threads: <span style='color: blue;'>{cpu_threads}</span>"))
        general_layout.addRow(QLabel(f"Chip type/CPU model: <span style='color: blue;'>{cpu_model}</span>"))
        general_layout.addRow(QLabel(f"Graphics card(s): <span style='color: blue;'>{gpu}</span>"))

        cuda_supported = torch.cuda.is_available()
        general_layout.addRow(QLabel(f"CUDA support: <span style='color: blue;'>{'Yes' if cuda_supported else 'No'}</span>"))
        general_layout.addRow(QLabel(f"Storage space: <span style='color: blue;'>{disk:.2f} GB</span>"))
        general_layout.addRow(QLabel(f"Xcpp version: <span style='color: blue;'>1</span>"))
        general_layout.addRow(QLabel(f"Peharge security: <span style='color: blue;'>active</span>"))
        general_layout.addRow(QLabel(f""))
        general_layout.addRow(QLabel(f"Maximum <span style='color: blue;'>13B</span> recommended"))

        self.parameters_dropdown = QComboBox()
        self.parameters_dropdown.addItems(["7B", "13B", "32B", "70B", "301B", "512B", "1024B", "1536B"])

        self.parameters_dropdown.setCurrentText("7B")
        general_layout.addRow(QLabel("Parameters:"), self.parameters_dropdown)

        general_layout.addRow(QLabel(f""))
        general_layout.addRow(QLabel(f"Xc++ 13B uses <span style='color: blue;'>7 GB</span> of your RAM"))
        general_layout.addRow(QLabel(f"Xc++ 13B uses <span style='color: blue;'>93%</span> of your CPU power"))
        general_layout.addRow(QLabel(f"Xc++ 13B uses <span style='color: blue;'>79 GB</span> of your disk space"))

        general_group.setLayout(general_layout)
        main_frame_layout.addWidget(general_group)

        buttons_layout = QHBoxLayout()
        self.apply_button = QPushButton()
        self.apply_button.setIcon(QIcon('C:\\Users\\julia\\PycharmProjects\\Xcpp\\agree.svg'))
        self.apply_button.setFixedSize(40, 40)
        self.apply_button.setIconSize(QSize(28, 28))
        self.apply_button.clicked.connect(self.play_sound_1)
        self.apply_button.setStyleSheet("""
            QPushButton {
                color: #000000;
                background-color: rgba(255, 255, 255, 0);
            }
            QPushButton:hover {
                color: #FFFFFF;
            }
        """)
        self.apply_button.clicked.connect(self.apply_settings)

        self.apply_button.pressed.connect(self.move_apply_button_up)
        self.apply_button.released.connect(lambda: self.move_apply_button_down(self.apply_button))

        self.apply_button.enterEvent = self.on_apply_button_hover
        self.apply_button.leaveEvent = self.on_apply_button_leave

        self.cancel_button = QPushButton()
        self.cancel_button.setIcon(QIcon('C:\\Users\\julia\\PycharmProjects\\Xcpp\\disagree.svg'))
        self.cancel_button.setFixedSize(40, 40)
        self.cancel_button.setIconSize(QSize(28, 28))
        self.cancel_button.clicked.connect(self.play_sound_2)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                color: #000000;
                background-color: rgba(255, 255, 255, 0);
            }
            QPushButton:hover {
                color: #FFFFFF;
            }
        """)
        self.cancel_button.clicked.connect(self.reject)

        self.cancel_button.pressed.connect(self.move_cancel_button_up)
        self.cancel_button.released.connect(lambda: self.move_cancel_button_down(self.cancel_button))

        self.cancel_button.enterEvent = self.on_cancel_button_hover
        self.cancel_button.leaveEvent = self.on_cancel_button_leave

        self.update_button = QPushButton()
        self.update_button.setIcon(QIcon('C:\\Users\\julia\\PycharmProjects\\Xcpp\\update.svg'))
        self.update_button.setFixedSize(40, 40)
        self.update_button.setIconSize(QSize(28, 28))
        self.update_button.clicked.connect(self.play_sound_1)
        self.update_button.setStyleSheet("""
            QPushButton {
                color: #000000;
                background-color: rgba(255, 255, 255, 0);
            }
            QPushButton:hover {
                color: #FFFFFF;
            }
        """)
        self.update_button.clicked.connect(self.reject)

        self.update_button.pressed.connect(self.move_update_button_up)
        self.update_button.released.connect(lambda: self.move_update_button_down(self.update_button))

        self.update_button.enterEvent = self.on_update_button_hover
        self.update_button.leaveEvent = self.on_update_button_leave

        self.model_button = QPushButton()
        self.model_button.setIcon(QIcon('C:\\Users\\julia\\PycharmProjects\\Xcpp\\info.svg'))
        self.model_button.setFixedSize(40, 30)
        self.model_button.setIconSize(QSize(28, 28))
        self.model_button.clicked.connect(self.play_sound_1)
        self.model_button.setStyleSheet("""
            QPushButton {
                color: #000000;
                background-color: rgba(255, 255, 255, 0);
            }
            QPushButton:hover {
                color: #FFFFFF;
            }
        """)
        self.model_button.clicked.connect(self.open_modelinfo)

        self.model_button.pressed.connect(self.move_model_button_up)
        self.model_button.released.connect(lambda: self.move_model_button_down(self.model_button))

        self.model_button.enterEvent = self.on_model_button_hover
        self.model_button.leaveEvent = self.on_model_button_leave

        self.sec_button = QPushButton()
        self.sec_button.setIcon(QIcon('C:\\Users\\julia\\PycharmProjects\\Xcpp\\sec.svg'))
        self.sec_button.setFixedSize(40, 40)
        self.sec_button.setIconSize(QSize(28, 28))
        self.sec_button.clicked.connect(self.play_sound_1)
        self.sec_button.setStyleSheet("""
            QPushButton {
                color: #000000;
                background-color: rgba(255, 255, 255, 0);
            }
            QPushButton:hover {
                color: #FFFFFF;
            }
        """)
        self.sec_button.clicked.connect(self.open_SicherheitsbewertungFenster)

        self.sec_button.pressed.connect(self.move_sec_button_up)
        self.sec_button.released.connect(lambda: self.move_sec_button_down(self.sec_button))

        self.sec_button.enterEvent = self.on_sec_button_hover
        self.sec_button.leaveEvent = self.on_sec_button_leave

        buttons_layout.addWidget(self.apply_button)
        buttons_layout.addWidget(self.cancel_button)
        buttons_layout.addWidget(self.update_button)
        buttons_layout.addWidget(self.model_button)
        buttons_layout.addWidget(self.sec_button)
        buttons_layout.setAlignment(Qt.AlignCenter)

        main_frame_layout.addLayout(buttons_layout)

        main_layout.addWidget(main_frame)
        self.setLayout(main_layout)

    def move_apply_button_up(self):
        self.apply_button.move(self.apply_button.x(), self.apply_button.y() - 3)

    def move_apply_button_down(self, button):
        button.move(button.x(), button.y() + 3)

    def on_apply_button_hover(self, event):
        self.move_apply_button_up()
        event.accept()

    def on_apply_button_leave(self, event):
        self.move_apply_button_down(self.apply_button)
        event.accept()

    def move_cancel_button_up(self):
        self.cancel_button.move(self.cancel_button.x(), self.cancel_button.y() - 3)

    def move_cancel_button_down(self, button):
        button.move(button.x(), button.y() + 3)

    def on_cancel_button_hover(self, event):
        self.move_cancel_button_up()
        event.accept()

    def on_cancel_button_leave(self, event):
        self.move_cancel_button_down(self.cancel_button)
        event.accept()

    def move_update_button_up(self):
        self.update_button.move(self.update_button.x(), self.update_button.y() - 3)

    def move_update_button_down(self, button):
        button.move(button.x(), button.y() + 3)

    def on_update_button_hover(self, event):
        self.move_update_button_up()
        event.accept()

    def on_update_button_leave(self, event):
        self.move_update_button_down(self.update_button)
        event.accept()

    def move_model_button_up(self):
        self.model_button.move(self.model_button.x(), self.model_button.y() - 3)

    def move_model_button_down(self, button):
        button.move(button.x(), button.y() + 3)

    def on_model_button_hover(self, event):
        self.move_model_button_up()
        event.accept()

    def on_model_button_leave(self, event):
        self.move_model_button_down(self.model_button)
        event.accept()

    def move_sec_button_up(self):
        self.sec_button.move(self.sec_button.x(), self.sec_button.y() - 3)

    def move_sec_button_down(self, button):
        button.move(button.x(), button.y() + 3)

    def on_sec_button_hover(self, event):
        self.move_sec_button_up()
        event.accept()

    def on_sec_button_leave(self, event):
        self.move_sec_button_down(self.sec_button)
        event.accept()

    def play_sound_1(self):
        try:
            mp3_path = "C:/Users/julia/PycharmProjects/Xcpp/decidemp3-14575.mp3"

            url = QUrl.fromLocalFile(mp3_path)
            content = QMediaContent(url)

            self.player.setMedia(content)

            self.player.play()
            print(f"Playing sound from: {mp3_path}")

        except Exception as e:
            print(f"Error while trying to play sound: {e}")

    def play_sound_2(self):
        try:
            mp3_path = "C:/Users/julia/PycharmProjects/Xcpp/tv-shut-down-185446.mp3"

            url = QUrl.fromLocalFile(mp3_path)
            content = QMediaContent(url)

            self.player.setMedia(content)

            self.player.play()
            print(f"Playing sound from: {mp3_path}")

        except Exception as e:
            print(f"Error while trying to play sound: {e}")

    def open_modelinfo(self):
        self.model_window = ModelWindow(self)
        self.model_window.exec_()

    def open_SicherheitsbewertungFenster(self):
        self.model_window = StilvollesSicherheitsfenster(self)
        self.model_window.exec_()

    def apply_settings(self):
        QMessageBox.information(self, "Einstellungen", "Einstellungen wurden angewendet.")

    def apply_settings(self):
        """self.save_settings()
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("Einstellungen wurden angewendet.")
        msg.setWindowTitle("Bestätigung")
        msg.exec_()
        self.accept()"""

    def save_settings(self):
        try:
            """brightness = self.brightness_slider.value()
            volume = self.volume_slider.value()
            contrast = self.contrast_slider.value()
            saturation = self.saturation_slider.value()
            mic_volume = self.mic_volume_slider.value()
            language = self.language_dropdown.currentText()
            theme = self.theme_dropdown.currentText()
            font_size = self.font_size_slider.value()
            audio_device = self.audio_device_dropdown.currentText()

            logging.info(f"Gespeicherte Einstellungen: Helligkeit: {brightness}, Lautstärke: {volume}, Kontrast: {contrast}, Sättigung: {saturation}, Mikrofon: {mic_volume}, Sprache: {language}, Theme: {theme}, Schriftgröße: {font_size}, Audioeingabegerät: {audio_device}")

            # Anpassen der System- oder App-Einstellungen
            self.set_camera_brightness(brightness)
            self.set_system_volume(volume)
            self.set_camera_contrast(contrast)
            self.set_camera_saturation(saturation)
            self.set_microphone_volume(mic_volume)
            self.set_application_language(language)
            self.apply_theme(theme)
            self.apply_font_size(font_size)
            self.set_audio_input_device(audio_device)"""

        except Exception as e:
            logging.error(f"Fehler beim Speichern der Einstellungen: {e}")

    def set_camera_brightness(self, brightness):
        pass

    def set_system_volume(self, volume):
        """devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(
            AudioUtilities.IID_IAudioEndpointVolume, None, None)
        volume_control = interface.QueryInterface(ISimpleAudioVolume)
        volume_control.SetMasterVolume(float(volume) / 100.0, None)"""

    def set_camera_contrast(self, contrast):
        pass

    def set_camera_saturation(self, saturation):
        pass

    def set_microphone_volume(self, mic_volume):
        """devices = AudioUtilities.GetMicrophone()
        interface = devices.Activate(
            AudioUtilities.IID_IAudioEndpointVolume, None, None)
        volume_control = interface.QueryInterface(ISimpleAudioVolume)
        volume_control.SetMasterVolume(float(mic_volume) / 100.0, None)"""

    def set_application_language(self, language):
        pass

    def apply_theme(self, theme):
        pass

    def apply_font_size(self, font_size):
        pass

    def set_audio_input_device(self, audio_device):
        """devices = sd.query_devices()
        for device in devices:
            if device['name'] == audio_device:
                sd.default.device = device['index']
                break"""



class ModelWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Xc++ Info")
        self.setGeometry(113, 50, 300, 300)
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.init_ui()
        self.player = QMediaPlayer()

    def init_ui(self):
        font = QFont('Xc++ Info', 12)
        self.setFont(font)

        main_layout = QVBoxLayout()
        main_frame = QFrame(self)
        main_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.7);
                border-radius: 15px;
                box-shadow: 0px 0px 15px rgba(0, 0, 0, 0.5);
            }
        """)
        main_frame_layout = QVBoxLayout(main_frame)

        title_layout = QHBoxLayout()
        title_label = QLabel("Xc++ Info")
        title_label.setStyleSheet("color: #000000; font-size: 16px; font-weight: bold; background-color: rgba(255, 255, 255, 0);")
        title_layout.addWidget(title_label)
        close_button = QPushButton("×")
        close_button.clicked.connect(self.play_sound_1)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #C0392B;
                color: #FFFFFF;
                border: none;
                border-radius: 10px;
                width: 30px;
                height: 30px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #E74C3C;
            }
        """)
        close_button.clicked.connect(self.close)
        title_layout.addStretch()
        title_layout.addWidget(close_button)

        main_frame_layout.addLayout(title_layout)

        general_group = QGroupBox("General informations")
        general_group.setStyleSheet("""
            QGroupBox {
                background-color: rgba(255, 255, 255, 0);
                font-weight: bold;
                color: #000000;
                border-radius: 10px;
                margin-top: 10px;
            }
            QGroupBox::title {
                background-color: rgba(255, 255, 255, 0);
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QLabel {
                font-size: 12px;
                background-color: rgba(255, 255, 255, 0);
                color: #000000;
            }
            QSlider {
                background-color: rgba(255, 255, 255, 0);
            }
            QSlider::groove:horizontal {
                height: 6px;
                background: #000000;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                border: 3px solid #000000;
                width: 15px;
                height: 15px;
                margin: -7px 0;
                border-radius: 7px;
                background-color: rgba(255, 255, 255, 0);
            }
            QSlider::add-page:horizontal {
                background-color: rgba(255, 255, 255, 0);
            }
            QSlider::sub-page:horizontal {
                background-color: rgba(255, 255, 255, 0);
            }
            QComboBox {
                background-color: #000000;
                border: 1px solid #5D6D7E;
                border-radius: 5px;
                padding: 5px;
                color: #ffffff;
            }
            QComboBox QAbstractItemView {
                background-color: #000000;
                border: 1px solid #5D6D7E;
                border-radius: 5px;
                padding: 5px;
                color: #ffffff;
            }
            QComboBox::down-arrow {
                image: url(C:/Users/julia/PycharmProjects/Xcpp/down.svg);
                width: 15px;
                height: 15px;
            }
            QListWidget {
                background-color: #000000;
                padding: 20px;
                border: 2px solid #4a4a4a;
                border-radius: 5px;
                color: #ffffff;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 2px solid #4a4a4a;
                color: #ffffff;
            }
            QListWidget::item:hover {
                border-bottom: 3px solid #0078d7;
            }
            QListWidget::item:selected {
                background-color: #0078d7;
                border-bottom: 3px solid #0078d7;
            }
            QScrollBar:vertical {
                background-color: #000000;
                width: 10px;
                border: none;
            }

            QScrollBar::handle:vertical {
                background-color: #ffffff;
                min-height: 20px;
                border-radius: 5px;
            }

            QScrollBar::add-line:vertical {
                background: none;
            }

            QScrollBar::sub-line:vertical {
                background: none;
            }

            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
                background: none;
            }

            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        general_layout = QFormLayout()

        ram = psutil.virtual_memory().total / (1024 ** 3)

        disk = psutil.disk_usage('/').total / (1024 ** 3)

        cpu_threads = psutil.cpu_count()

        try:
            import pyopencl as cl
            platforms = cl.get_platforms()
            gpus = [device.name for platform in platforms for device in platform.get_devices()]
            gpu = ', '.join(gpus)
        except ImportError:
            gpu = "Not available (OpenCL not installed)"

        cpu_model = platform.processor()

        system_info = platform.system() + " " + platform.release()

        general_layout.addRow(QLabel(f"Thank you for choosing Xc++.\n\nXc++ represents a significant advancement in natural human-computer interaction. \nIt accepts a wide range of inputs, including text, audio, and images, and can generate outputs in both text and audio formats. \nXc++ excels particularly in vision and audio comprehension, offering superior performance compared to existing models."))
        general_layout.addRow(QLabel(f""))
        general_layout.addRow(QLabel(f"RAM: <span style='color: blue;'>{ram:.2f} GB</span>"))
        general_layout.addRow(QLabel(f"Number of Threads: <span style='color: blue;'>{cpu_threads}</span>"))
        general_layout.addRow(QLabel(f"Chip type/CPU model: <span style='color: blue;'>{cpu_model}</span>"))
        general_layout.addRow(QLabel(f"Graphics card(s): <span style='color: blue;'>{gpu}</span>"))

        cuda_supported = torch.cuda.is_available()
        general_layout.addRow(QLabel(f"CUDA support: <span style='color: blue;'>{'Yes' if cuda_supported else 'No'}</span>"))
        general_layout.addRow(QLabel(f"Storage space: <span style='color: blue;'>{disk:.2f} GB</span>"))
        general_layout.addRow(QLabel(f"System: <span style='color: blue;'>{system_info}</span>"))

        general_layout.addRow(QLabel(f"Python Version: <span style='color: blue;'>{platform.python_version()}</span>"))

        general_layout.addRow(QLabel(f"PyTorch Version: <span style='color: blue;'>{torch.__version__}</span>"))

        general_layout.addRow(QLabel(f"TensorFlow Version: <span style='color: blue;'>{tf.__version__}</span>"))

        general_layout.addRow(QLabel(f"Pandas Version: <span style='color: blue;'>{pd.__version__}</span>"))

        general_layout.addRow(QLabel(f"Pygame Version: <span style='color: blue;'>{pygame.__version__}</span>"))

        general_layout.addRow(QLabel(f"NumPy Version: <span style='color: blue;'>{np.__version__}</span>"))

        general_layout.addRow(QLabel(f"Transformers Version: <span style='color: blue;'>{transformers_version}</span>"))
        general_layout.addRow(QLabel(f""))
        general_layout.addRow(QLabel(f"Xc++ Version: <span style='color: blue;'>1</span>"))
        general_layout.addRow(QLabel(f"Peharge security Version: <span style='color: blue;'>2</span>"))
        general_layout.addRow(QLabel(f""))

        general_group.setLayout(general_layout)
        main_frame_layout.addWidget(general_group)

        main_layout.addWidget(main_frame)
        self.setLayout(main_layout)

    def play_sound_1(self):
        try:
            mp3_path = "C:/Users/julia/Downloads/tv-shut-down-185446.mp3"

            url = QUrl.fromLocalFile(mp3_path)
            content = QMediaContent(url)

            self.player.setMedia(content)

            self.player.play()
            print(f"Playing sound from: {mp3_path}")

        except Exception as e:
            print(f"Error while trying to play sound: {e}")



class SicherheitsbewertungThread(QThread):
    update_progress = pyqtSignal(int)
    finished = pyqtSignal(str)

    def run(self):
        for i in range(101):
            time.sleep(0.05)
            self.update_progress.emit(i)
        self.finished.emit("Security scan completed.\nNo obvious security risks found.\n3. FutureWarnings (torch.load with weights_only=False), 1. wisper, 2.vits, 3.tts (solution: weights_only=True)\n")



class StilvollesSicherheitsfenster(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Peharge Security check")
        self.setWindowIcon(
            QIcon('C:\\Users\\julia\\OneDrive - Gewerbeschule Lörrach\\Pictures\\software\\peharge-logo3.6.ico'))
        self.setGeometry(113, 50, 400, 470)
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.init_ui()
        self.player = QMediaPlayer()

    def init_ui(self):
        font = QFont('Arial', 12)
        self.setFont(font)

        main_layout = QVBoxLayout(self)

        main_frame = QFrame(self)
        main_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.7);
                border-radius: 15px;
                box-shadow: 0px 0px 15px rgba(0, 0, 0, 0.5);
            }
        """)
        main_frame_layout = QVBoxLayout(main_frame)
        main_layout.addWidget(main_frame)

        title_layout = QHBoxLayout()
        title_label = QLabel("Peharge Security check")
        title_label.setStyleSheet("color: #000000; font-size: 16px; font-weight: bold; background-color: rgba(255, 255, 255, 0);")
        title_layout.addWidget(title_label)
        title_layout.addStretch()

        close_button = QPushButton("×")
        close_button.clicked.connect(self.play_sound_2)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #C0392B;
                color: #FFFFFF;
                border: none;
                border-radius: 10px;
                width: 30px;
                height: 30px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #E74C3C;
            }
        """)
        close_button.clicked.connect(self.close)
        title_layout.addWidget(close_button)

        main_frame_layout.addLayout(title_layout)

        content_layout = QVBoxLayout()
        main_frame_layout.addLayout(content_layout)

        svg_widget = QSvgWidget('C:\\Users\\julia\\PycharmProjects\\Xcpp\\sec.svg', self)
        svg_widget.setFixedSize(100, 100)
        svg_widget.setStyleSheet("background: transparent;")
        content_layout.addWidget(svg_widget)
        content_layout.setAlignment(svg_widget, Qt.AlignCenter)

        titel_label = QLabel("\nSafety assessment\n", self)
        titel_label.setFont(QFont("Arial", 16, QFont.Bold))
        titel_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                background-color: rgba(255, 255, 255, 0);
                color: #000000;
            }
        """)
        titel_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(titel_label)

        self.sicherheitsbewertung_label = QLabel("Security code evaluation:", self)
        self.sicherheitsbewertung_label.setFont(font)
        self.sicherheitsbewertung_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                background-color: rgba(255, 255, 255, 0);
                color: #000000;
            }
        """)
        content_layout.addWidget(self.sicherheitsbewertung_label)

        self.sicherheitsstatus_label = QLabel("", self)
        self.sicherheitsstatus_label.setFont(font)
        self.sicherheitsstatus_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                background-color: rgba(255, 255, 255, 0);
                color: #000000;
            }
        """)
        self.sicherheitsstatus_label.setWordWrap(True)
        content_layout.addWidget(self.sicherheitsstatus_label)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                background: transparent;
                border-radius: 10px;
                text-align: center;
            }

            QProgressBar::chunk {
                background-color: blue;
                width: 20px;
                height: 20px;
                border-radius: 3px;
                margin: 0 5px;
            }

            QProgressBar::chunk {
                animation: progress 2s linear infinite;
            }

            @keyframes progress {
                0% {
                    background-color: #007BFF;
                }
                50% {
                    background-color: #0056b3;
                }
                100% {
                    background-color: #007BFF;
                }
            }
        """)
        content_layout.addWidget(self.progress_bar)

        self.bewertung_btn = QPushButton()
        self.bewertung_btn.setIcon(QIcon('C:\\Users\\julia\\PycharmProjects\\Xcpp\\run-sec.svg'))
        self.bewertung_btn.clicked.connect(self.play_sound_1)
        self.bewertung_btn.setFixedSize(50, 50)
        self.bewertung_btn.setIconSize(QSize(38, 38))
        self.bewertung_btn.setFont(QFont("Arial", 10, QFont.Bold))
        #bewertung_btn.setFont(font)
        self.bewertung_btn.setStyleSheet("""
            QPushButton {
                color: #000000;
                background-color: rgba(255, 255, 255, 0);
            }
            QPushButton:hover {
                color: #FFFFFF;
            }
        """)
        self.bewertung_btn.clicked.connect(self.start_sicherheitsbewertung)

        self.bewertung_btn.pressed.connect(self.move_bewertung_btn_up)
        self.bewertung_btn.released.connect(lambda: self.move_bewertung_btn_down(self.bewertung_btn))

        self.bewertung_btn.enterEvent = self.on_bewertung_btn_hover
        self.bewertung_btn.leaveEvent = self.on_bewertung_btn_leave

        content_layout.addWidget(self.bewertung_btn)
        content_layout.setAlignment(self.bewertung_btn, Qt.AlignCenter)

    def move_bewertung_btn_up(self):
        self.bewertung_btn.move(self.bewertung_btn.x(), self.bewertung_btn.y() - 3)

    def move_bewertung_btn_down(self, button):
        button.move(button.x(), button.y() + 3)

    def on_bewertung_btn_hover(self, event):
        self.move_bewertung_btn_up()
        event.accept()

    def on_bewertung_btn_leave(self, event):
        self.move_bewertung_btn_down(self.bewertung_btn)
        event.accept()

    def play_sound_1(self):
        try:
            mp3_path = "C:/Users/julia/Downloads/downfall-3-208028.mp3"

            url = QUrl.fromLocalFile(mp3_path)
            content = QMediaContent(url)

            self.player.setMedia(content)

            self.player.play()
            print(f"Playing sound from: {mp3_path}")

        except Exception as e:
            print(f"Error while trying to play sound: {e}")

    def play_sound_2(self):
        try:
            mp3_path = "C:/Users/julia/Downloads/tv-shut-down-185446.mp3"

            url = QUrl.fromLocalFile(mp3_path)
            content = QMediaContent(url)

            self.player.setMedia(content)

            self.player.play()
            print(f"Playing sound from: {mp3_path}")

        except Exception as e:
            print(f"Error while trying to play sound: {e}")

    def start_sicherheitsbewertung(self):
        self.progress_bar.setValue(0)
        self.sicherheitsstatus_label.setText("Security check in progress...")
        self.sicherheitsstatus_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                background-color: rgba(255, 255, 255, 0);
                color: #000000;
            }
        """)

        self.thread = SicherheitsbewertungThread()
        self.thread.update_progress.connect(self.progress_bar.setValue)
        self.thread.finished.connect(self.zeige_ergebnis)
        self.thread.start()

    def zeige_ergebnis(self, nachricht):
        self.sicherheitsstatus_label.setText(nachricht)



class ImageGallery(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.image_folder = r"C:\Users\julia\PycharmProjects\Xcpp\img"  # Standardordner
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.setGeometry(0, 400, 1728, 400)
        self.setWindowIcon(QIcon('C:\\Users\\julia\\OneDrive - Gewerbeschule Lörrach\\Pictures\\software\\peharge-logo3.6.ico'))

        myappid = u'mycompany.myproduct.subproduct.version'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background: rgba(255, 255, 255, 0);")

        self.setWindowOpacity(0)

        glass_frame = QFrame(self)
        glass_frame.setGeometry(0, 0, 1728, 350)
        glass_frame.setStyleSheet("""
            background-color: rgba(255, 255, 255, 0);
            color: #000000;
            border-radius: 10px;
        """)

        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.scroll_content = QWidget()
        self.scroll_layout = QHBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setSpacing(0)

        scroll_area.setWidget(self.scroll_content)
        layout.addWidget(scroll_area)

        self.load_images()

    def set_image_folder(self, folder_path):
        self.image_folder = folder_path
        self.load_images()

    def load_images(self):
        if not os.path.exists(self.image_folder):
            print(f"Image folder does not exist: {self.image_folder}")
            return

        supported_formats = QImageReader.supportedImageFormats()
        supported_extensions = [str(fmt.data(), 'utf-8').lower() for fmt in supported_formats]

        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        try:
            image_files = [f for f in os.listdir(self.image_folder) if any(f.lower().endswith(ext) for ext in supported_extensions)]
            image_files.sort(reverse=True)  # Sortiere die Bilddateien umgekehrt, neueste zuerst

            for img_name in image_files:
                img_path = os.path.join(self.image_folder, img_name)

                pixmap = QPixmap(img_path)
                if pixmap.isNull():
                    print(f"Failed to load image: {img_path}")
                    continue

                pixmap = pixmap.scaled(400, 300, aspectRatioMode=Qt.KeepAspectRatio, transformMode=Qt.SmoothTransformation)

                label = QLabel(self)
                label.setPixmap(pixmap)

                shadow_effect = QGraphicsDropShadowEffect()
                shadow_effect.setBlurRadius(15)
                shadow_effect.setColor(QColor(0, 0, 0, 0))
                shadow_effect.setOffset(0, 0)

                label.setGraphicsEffect(shadow_effect)

                self.scroll_layout.addWidget(label)

        except Exception as e:
            print(f"An error occurred while loading images: {e}")

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)

        gradient = QLinearGradient(self.width() - 100, 0, self.width(), 0)
        gradient.setColorAt(0, QColor(0, 0, 0, 0))
        gradient.setColorAt(1, QColor(0, 0, 0, 0))

        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        painter.drawRect(QRect(self.width() - 100, 0, 100, self.height()))

    def resizeEvent(self, event):
        super().resizeEvent(event)



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.camera_thread = CameraThread()
        self.camera_thread.frame_signal.connect(self.update_camera_view)
        self.camera_thread.start()
        self.image_gallery = None
        self.gallery_active = False
        self.player = QMediaPlayer()
        self.voice_window = None

    def initUI(self):
        self.setWindowTitle("Xc++")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setGeometry(96, 29, 1728, 972)
        self.set_rounded_corners(20)

        self.logo_label = QLabel(self)
        icon_path = "C:/Users/julia/PycharmProjects/Xcpp/peharge-logo3.6.ico"
        if not os.path.exists(icon_path):
            logging.error(f"Icon file not found at: {icon_path}")
        self.setWindowIcon(QIcon(icon_path))

        self.setStyleSheet("background-color: white; border-radius: 20px;")

        myappid = u'mycompany.myproduct.subproduct.version'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

        self.setStyleSheet("background: transparent;")

        self.setStyleSheet("background-color: white; border-radius: 20px;")

        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)
        self.main_layout = QVBoxLayout(self.main_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.camera_view = QLabel(self)
        self.camera_view.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.camera_view)

        self.glass_frame = QFrame(self)
        self.glass_frame.setStyleSheet("""
            background-color: rgba(255, 255, 255, 0);
            border-radius: 20px;
            color: #000000;
        """)
        self.glass_frame.setFixedSize(1728, 972)

        self.glass_frame2 = QFrame(self)
        self.glass_frame2.setStyleSheet("""
            background-color: rgba(255, 255, 255, 150);
            border-radius: 20px;
            color: #000000;
        """)
        self.glass_frame2.setFixedSize(700, 165)

        parent_width = self.width()
        frame_width = self.glass_frame2.width()
        x_position = (parent_width - frame_width) // 2
        y_position = 780

        self.glass_frame2.move(x_position, y_position)

        self.glass_frame_layout = QVBoxLayout(self.glass_frame)
        self.glass_frame_layout.setContentsMargins(0, 0, 30, 30)

        self.glass_frame_spacer = QSpacerItem(30, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.glass_frame_layout.addItem(self.glass_frame_spacer)

        self.label = QLabel("Press the green receiver and speak", self.glass_frame)
        self.label.setAlignment(Qt.AlignBottom | Qt.AlignHCenter)
        self.label.setStyleSheet("color: #000000;")
        self.label.setFont(QFont('Arial', 17, QFont.Bold))
        self.glass_frame_layout.addWidget(self.label)

        self.button_layout = QHBoxLayout()

        self.button1 = QPushButton(self.glass_frame)
        self.button1.setIcon(QIcon('C:\\Users\\julia\\PycharmProjects\\Xcpp\\run.svg'))
        self.button1.setFixedSize(85, 85)
        self.shadow_effect1 = QGraphicsDropShadowEffect(self)
        self.shadow_effect1.setBlurRadius(10)
        self.shadow_effect1.setColor(QColor(0, 0, 0, 160))
        self.shadow_effect1.setOffset(7, 7)
        self.button1.setIconSize(QSize(71, 71))
        self.button1.setGraphicsEffect(self.shadow_effect1)
        self.button1.setFont(QFont('Arial', 20, QFont.Bold))
        self.button1.setStyleSheet("""
             QPushButton {
                 color: #000000;
                 border-radius: 25px;
                 padding: 10px 20px;
                 font-size: 16px;
                 font-weight: bold;
             }
         """)
        self.button1.setFixedSize(85, 85)
        self.button_layout.addWidget(self.button1)
        self.button1.clicked.connect(self.start_listening)

        self.button1.pressed.connect(self.move_button1_up)
        self.button1.released.connect(lambda: self.move_button1_down(self.button1))

        self.button1.enterEvent = self.on_button1_hover
        self.button1.leaveEvent = self.on_button1_leave

        self.button2 = QPushButton(self.glass_frame)
        self.button2.setIcon(QIcon('C:\\Users\\julia\\PycharmProjects\\Xcpp\\close.svg'))
        self.button2.clicked.connect(self.play_sound_2)
        self.shadow_effect2 = QGraphicsDropShadowEffect(self)
        self.shadow_effect2.setBlurRadius(10)
        self.shadow_effect2.setColor(QColor(0, 0, 0, 160))
        self.shadow_effect2.setOffset(7, 7)
        self.button2.setGraphicsEffect(self.shadow_effect2)

        self.button2.setIconSize(QSize(71, 71))
        self.button2.setFixedSize(85, 85)
        self.button2.setFont(QFont('Arial', 20, QFont.Bold))
        self.button2.setStyleSheet("""
             QPushButton {
                 color: #000000;
                 border-radius: 25px;
                 padding: 10px 20px;
                 font-size: 16px;
                 font-weight: bold;
             }
         """)
        self.button_layout.addWidget(self.button2)
        self.button2.clicked.connect(self.close_window)

        self.button2.pressed.connect(self.move_button2_up)
        self.button2.released.connect(lambda: self.move_button2_down(self.button2))

        self.button2.enterEvent = self.on_button2_hover
        self.button2.leaveEvent = self.on_button2_leave


        """        self.button3.clicked.connect(self.restart) // C:\\Users\\julia\\PycharmProjects\\Xcpp\\peharge-p-logo.svg"""

        self.button3 = QPushButton(self.glass_frame)
        self.button3.setIcon(QIcon('C:\\Users\\julia\\PycharmProjects\\Xcpp\\peharge-logo-p-10.svg'))
        self.button3.clicked.connect(self.play_sound_3)
        self.shadow_effect3 = QGraphicsDropShadowEffect(self)
        self.shadow_effect3.setBlurRadius(10)
        self.shadow_effect3.setColor(QColor(0, 0, 0, 160))
        self.shadow_effect3.setOffset(7, 7)
        self.button3.setGraphicsEffect(self.shadow_effect3)

        self.button3.setIconSize(QSize(68, 68))
        self.button3.setFixedSize(85, 85)
        self.button3.setFont(QFont('Arial', 20, QFont.Bold))
        self.button3.setStyleSheet("""
             QPushButton {
                 color: #000000;
                 border-radius: 25px;
                 padding: 10px 20px;
                 font-size: 16px;
                 font-weight: bold;
             }
         """)
        self.button_layout.addWidget(self.button3)
        self.button3.clicked.connect(self.restart)

        self.button3.pressed.connect(self.move_button3_up)
        self.button3.released.connect(lambda: self.move_button3_down(self.button3))

        self.button3.enterEvent = self.on_button3_hover
        self.button3.leaveEvent = self.on_button3_leave

        """C:\\Users\\julia\\PycharmProjects\\Xcpp\\settings.svg //         self.button4.clicked.connect(self.open_settings)"""

        self.button4 = QPushButton(self.glass_frame)
        self.button4.setIcon(QIcon('C:\\Users\\julia\\PycharmProjects\\Xcpp\\settings2.svg'))
        self.button4.clicked.connect(self.play_sound_4)
        self.shadow_effect4 = QGraphicsDropShadowEffect(self)
        self.shadow_effect4.setBlurRadius(10)
        self.shadow_effect4.setColor(QColor(0, 0, 0, 160))
        self.shadow_effect4.setOffset(7, 7)
        self.button4.setGraphicsEffect(self.shadow_effect4)

        self.button4.setIconSize(QSize(68, 68))
        self.button4.setFixedSize(85, 85)
        self.button4.setFont(QFont('Arial', 20, QFont.Bold))
        self.button4.setStyleSheet("""
             QPushButton {
                 color: #000000;
                 border-radius: 25px;
                 padding: 10px 20px;
                 font-size: 16px;
                 font-weight: bold;
             }
         """)
        self.button_layout.addWidget(self.button4)
        self.button4.clicked.connect(self.open_settings)

        self.button4.pressed.connect(self.move_button4_up)
        self.button4.released.connect(lambda: self.move_button4_down(self.button4))

        self.button4.enterEvent = self.on_button4_hover
        self.button4.leaveEvent = self.on_button4_leave

        self.button5 = QPushButton(self.glass_frame)
        self.button5.setIcon(QIcon('C:\\Users\\julia\\PycharmProjects\\Xcpp\\img6.svg'))
        self.button5.clicked.connect(self.play_sound_5)

        self.shadow_effect5 = QGraphicsDropShadowEffect(self)
        self.shadow_effect5.setBlurRadius(10)
        self.shadow_effect5.setColor(QColor(0, 0, 0, 160))
        self.shadow_effect5.setOffset(7, 7)
        self.button5.setGraphicsEffect(self.shadow_effect5)

        self.button5.setIconSize(QSize(66, 66))
        self.button5.setFixedSize(85, 85)
        self.button5.setFont(QFont('Arial', 20, QFont.Bold))
        self.button5.setStyleSheet("""
            QPushButton {
                color: #000000;
                border-radius: 42px;
                padding: 0px;
                font-size: 16px;
                font-weight: bold;
                background: transparent;
                border: 25px solid #000000;
            }
        """)
        self.button_layout.addWidget(self.button5)
        self.button5.clicked.connect(self.show_gallery)

        self.button5.pressed.connect(self.move_button5_up)
        self.button5.released.connect(lambda: self.move_button5_down(self.button5))

        self.button5.enterEvent = self.on_button5_hover
        self.button5.leaveEvent = self.on_button5_leave

        self.button6 = QPushButton(self.glass_frame)
        self.button6.setIcon(QIcon('C:\\Users\\julia\\PycharmProjects\\Xcpp\\audio2.svg'))
        self.button6.clicked.connect(self.play_sound_5)

        self.shadow_effect6 = QGraphicsDropShadowEffect(self)
        self.shadow_effect6.setBlurRadius(10)
        self.shadow_effect6.setColor(QColor(0, 0, 0, 160))
        self.shadow_effect6.setOffset(7, 7)
        self.button6.setGraphicsEffect(self.shadow_effect6)

        self.button6.setIconSize(QSize(68, 68))
        self.button6.setFixedSize(85, 85)
        self.button6.setFont(QFont('Arial', 20, QFont.Bold))
        self.button6.setStyleSheet("""
            QPushButton {
                color: #000000;
                border-radius: 42px;
                padding: 0px;
                font-size: 16px;
                font-weight: bold;
                background: transparent;
                border: 25px solid #000000;
            }
        """)
        self.button_layout.addWidget(self.button6)
        self.button6.clicked.connect(self.open_AudioFenster)

        self.button6.pressed.connect(self.move_button6_up)
        self.button6.released.connect(lambda: self.move_button6_down(self.button6))

        self.button6.enterEvent = self.on_button6_hover
        self.button6.leaveEvent = self.on_button6_leave

        self.button_container = QWidget(self.glass_frame)
        self.button_layout = QHBoxLayout(self.button_container)
        self.button_layout.setContentsMargins(0, 0, 0, 0)
        self.button_container.setLayout(self.button_layout)

        self.button_layout.addWidget(self.button3)
        self.button_layout.addSpacing(5)
        self.button_layout.addWidget(self.button1)
        self.button_layout.addSpacing(5)
        self.button_layout.addWidget(self.button2)
        self.button_layout.addSpacing(5)
        self.button_layout.addWidget(self.button5)
        self.button_layout.addSpacing(5)
        self.button_layout.addWidget(self.button6)
        self.button_layout.addSpacing(5)
        self.button_layout.addWidget(self.button4)

        self.glass_frame_layout.addWidget(self.button_container, alignment=Qt.AlignCenter)

        self.result_label = QLabel("", self.glass_frame)
        self.result_label.setStyleSheet("color: #ffffff;")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.glass_frame_layout.addWidget(self.result_label)

        self.glass_frame.raise_()

    def open_AudioFenster(self):
        if self.voice_window is None:
            self.voice_window = VoiceAnimationWindow()
            self.voice_window.show()
        else:
            self.voice_window.close()
            self.voice_window = None

    def play_sound_2(self):
        try:
            mp3_path = "C:/Users/julia/PycharmProjects/Xcpp/tv-shut-down-185446.mp3"

            url = QUrl.fromLocalFile(mp3_path)
            content = QMediaContent(url)

            self.player.setMedia(content)

            self.player.play()
            print(f"Playing sound from: {mp3_path}")

        except Exception as e:
            print(f"Error while trying to play sound: {e}")

    def play_sound_3(self):
        try:
            mp3_path = "C:/Users/julia/PycharmProjects/Xcpp/decidemp3-14575.mp3"

            url = QUrl.fromLocalFile(mp3_path)
            content = QMediaContent(url)

            self.player.setMedia(content)

            self.player.play()
            print(f"Playing sound from: {mp3_path}")

        except Exception as e:
            print(f"Error while trying to play sound: {e}")

    def play_sound_4(self):
        try:
            mp3_path = "C:/Users/julia/PycharmProjects/Xcpp/decidemp3-14575.mp3"

            url = QUrl.fromLocalFile(mp3_path)
            content = QMediaContent(url)

            self.player.setMedia(content)

            self.player.play()
            print(f"Playing sound from: {mp3_path}")

        except Exception as e:
            print(f"Error while trying to play sound: {e}")

    def play_sound_5(self):
        try:
            mp3_path = "C:/Users/julia/PycharmProjects/Xcpp/decidemp3-14575.mp3"

            url = QUrl.fromLocalFile(mp3_path)
            content = QMediaContent(url)

            self.player.setMedia(content)

            self.player.play()
            print(f"Playing sound from: {mp3_path}")

        except Exception as e:
            print(f"Error while trying to play sound: {e}")

    def move_button1_up(self):
        self.button1.move(self.button1.x(), self.button1.y() - 5)

    def move_button1_down(self, button):
        button.move(button.x(), button.y() + 5)

    def on_button1_hover(self, event):
        self.shadow_effect1.setOffset(2, 7)
        self.move_button1_up()
        event.accept()

    def on_button1_leave(self, event):
        self.shadow_effect1.setOffset(7, 7)
        self.move_button1_down(self.button1)
        event.accept()

    def move_button2_up(self):
        self.button2.move(self.button2.x(), self.button2.y() - 5)

    def move_button2_down(self, button):
        button.move(button.x(), button.y() + 5)

    def on_button2_hover(self, event):
        self.shadow_effect2.setOffset(2, 7)
        self.move_button2_up()
        event.accept()

    def on_button2_leave(self, event):
        self.shadow_effect2.setOffset(7, 7)
        self.move_button2_down(self.button2)
        event.accept()

    def move_button3_up(self):
        self.button3.move(self.button3.x(), self.button3.y() - 5)

    def move_button3_down(self, button):
        button.move(button.x(), button.y() + 5)

    def on_button3_hover(self, event):
        self.shadow_effect3.setOffset(2, 7)
        self.move_button3_up()
        event.accept()

    def on_button3_leave(self, event):
        self.shadow_effect3.setOffset(7, 7)
        self.move_button3_down(self.button3)
        event.accept()

    def move_button4_up(self):
        self.button4.move(self.button4.x(), self.button4.y() - 5)

    def move_button4_down(self, button):
        button.move(button.x(), button.y() + 5)

    def on_button4_hover(self, event):
        self.shadow_effect4.setOffset(2, 7)
        self.move_button4_up()
        event.accept()

    def on_button4_leave(self, event):
        self.shadow_effect4.setOffset(7, 7)
        self.move_button4_down(self.button4)
        event.accept()

    def move_button5_up(self):
        self.button5.move(self.button5.x(), self.button5.y() - 5)

    def move_button5_down(self, button):
        button.move(button.x(), button.y() + 5)

    def on_button5_hover(self, event):
        self.shadow_effect5.setOffset(2, 7)
        self.move_button5_up()
        event.accept()

    def on_button5_leave(self, event):
        self.shadow_effect5.setOffset(7, 7)
        self.move_button5_down(self.button5)
        event.accept()

    def move_button6_up(self):
        self.button6.move(self.button6.x(), self.button6.y() - 5)

    def move_button6_down(self, button):
        button.move(button.x(), button.y() + 5)

    def on_button6_hover(self, event):
        self.shadow_effect6.setOffset(2, 7)
        self.move_button6_up()
        event.accept()

    def on_button6_leave(self, event):
        self.shadow_effect6.setOffset(7, 7)
        self.move_button6_down(self.button6)
        event.accept()

    def open_settings(self):
        self.settings_window = SettingsWindow(self)
        self.settings_window.exec_()

    def show_gallery(self):
        image_folder = r"C:\Users\julia\PycharmProjects\Xcpp\img"

        if self.gallery_active:
            if self.image_gallery is not None:
                self.layout().removeWidget(self.image_gallery)
                self.image_gallery.setParent(None)
                self.image_gallery.deleteLater()
                self.image_gallery = None

            self.gallery_active = False
        else:
            self.image_gallery = ImageGallery(parent=self)
            self.image_gallery.set_image_folder(image_folder)
            self.layout().addWidget(self.image_gallery)

            self.gallery_active = True

    def update_camera_view(self, frame):
        pass

    def set_rounded_corners(self, radius):
        path = QPainterPath()
        path.addRoundedRect(self.rect(), radius, radius)
        mask = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(mask)


    def set_rounded_corners(self, radius):
        path = QPainterPath()
        rect = QRectF(self.rect())
        path.addRoundedRect(rect, radius, radius)

        region = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region)

    def close_window(self):
        QTimer.singleShot(350, self.close)

    def restart(self):
        print("Der Code wird ausgeführt...")
        time.sleep(5)

        print("Das Skript wird neu gestartet...")
        time.sleep(1)
        python = sys.executable
        os.execl(python, python, *sys.argv)

    def start_listening(self):
        try:
            self.label.setText("Listening...")
            self.audio_thread = AudioThread()
            self.audio_thread.audio_signal.connect(self.process_audio)
            self.audio_thread.start()
        except Exception as e:
            logging.error(f"Error in start_listening: {e}")

    def process_audio(self, audio):
        try:
            self.label.setText("Transcribing with Xc++...")
            result = model.transcribe(audio, fp16=False)
            text = result["text"]
            print(text)

            self.label.setText("Processing with Xc++...")
            image_path = self.capture_image()

            if not image_path:
                self.label.setText("Error taking picture.")
                return

            res = ollama.chat(
                model="llava:7b",
                messages=[
                    {
                        'role': 'user',
                        'content': text,
                        'images': [image_path]
                    }
                ]
            )

            llama3_output = res['message']['content']
            self.result_label.setText(llama3_output.strip())
            print(llama3_output)

            self.process_with_professional_tool(llama3_output.strip())
            self.button.setEnabled(True)
        except Exception as e:
            logging.error(f"Error in process_audio: {e}")

    def capture_image(self):
        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                raise Exception("Could not open video device")

            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

            ret, frame = cap.read()
            if not ret:
                raise Exception("Could not read frame")

            cap.release()

            current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            image_path = f"C:/Users/julia/PycharmProjects/Xcpp/img/image_{current_time}.png"
            cv2.imwrite(image_path, frame)
            return image_path
        except Exception as e:
            logging.error(f"Error in capture_image: {e}")
            return ""

    def update_camera_view(self, frame):
        try:
            height, width, channel = frame.shape
            bytes_per_line = 3 * width
            qt_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_BGR888)

            self.camera_view.setPixmap(QPixmap.fromImage(qt_image).scaled(self.camera_view.size(), Qt.KeepAspectRatio))

        except Exception as e:
            logging.error(f"Error in update_camera_view: {e}")

    def process_with_professional_tool(self, text_output, language="en"):
        try:
            if language == "en":
                model_name = "tts_models/en/ljspeech/vits" #tts_models/en/ljspeech/glow-tts // tts_models/en/ljspeech/vits // Nicht installiert: tts_models/en/ljspeech/fastspeech2 // tts_models/en/ljspeech/tacotron2_wavenet
            elif language == "de":
                model_name = "tts_models/de/thorsten/tacotron2-DCA" #tts_models/de/thorsten/tacotron2-DCA

            tts = TTS(model_name=model_name, progress_bar=False, gpu=False)
            current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            output_filename = f"output_{current_time}.wav"
            tts.tts_to_file(text=text_output, file_path=output_filename)

            config = XttsConfig()
            config.load_json(os.path.join("C:/Users/julia/PycharmProjects/Xcpp/xtts-v2", "config.json"))
            xtts_model = Xtts(config)
            xtts_model.load_checkpoint(config, checkpoint_dir="C:/Users/julia/Downloads/xtts-v2", eval=True)

            speaker_wav_path = os.path.join("C:/Users/julia/PycharmProjects/Xcpp/marsorbit-79697.mp3")

            if not os.path.exists(speaker_wav_path):
                raise FileNotFoundError(
                    f"Die Datei {speaker_wav_path} existiert nicht. Bitte überprüfen Sie den Pfad und versuchen Sie es erneut.")

            outputs = xtts_model.synthesize(
                text_output,
                config,
                speaker_wav=speaker_wav_path,
                gpt_cond_len=3,
                language="en",
            )

            output_file = f"C:/Users/julia/PycharmProjects/Xcpp/output_{current_time}_xtts.wav"
            if "wav" in outputs.keys():
                sample_rate = config.audio['sample_rate']
                with sf.SoundFile(output_file, "w", samplerate=sample_rate, channels=1) as file:
                    file.write(outputs["wav"])
                logging.info(f"Die Audiodatei wurde erfolgreich gespeichert unter: {output_file}")

                pygame.mixer.init()
                pygame.mixer.music.load(output_file)
                pygame.mixer.music.play()

                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)

            else:
                raise KeyError("Output dictionary does not contain 'wav'")

            if os.path.exists(output_filename):
                os.remove(output_filename)

            if os.path.exists(output_file):
                os.remove(output_file)

        except FileNotFoundError as e:
            logging.error(f"FileNotFoundError: {e}")
        except KeyError as e:
            logging.error(f"KeyError: {e}")
        except Exception as e:
            logging.error(f"Error in process_with_professional_tool: {e}")


"""
def run_command_and_get_output(command, text_input):
    try:
        result = subprocess.run(command, input=text_input, shell=True, check=True, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, text=True, encoding='utf-8')
        return result.stdout
    except subprocess.CalledProcessError as e:
        logging.error(f"Error executing command '{command}': {e}")
        return "Fehler beim Ausführen des Befehls: " + str(e)
"""



class WaveformWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.data = np.zeros(1024)

    def update_waveform(self, data):
        if len(data) != len(self.data):
            self.data = np.zeros(len(self.data))
        else:
            self.data = data
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        pen = QPen(QColor(255, 255, 255))
        pen.setWidth(2)
        painter.setPen(pen)

        width = self.size().width()
        height = self.size().height()
        middle = height / 2

        step = width / len(self.data)
        for i in range(1, len(self.data)):
            x1 = int((i - 1) * step)
            y1 = int(middle - self.data[i - 1] * middle)
            x2 = int(i * step)
            y2 = int(middle - self.data[i] * middle)
            painter.drawLine(x1, y1, x2, y2)



class VoiceAnimationWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sprachanimation")
        self.setGeometry(460, 355, 1000, 400)
        self.initUI()
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.audio_data = np.zeros(1024)
        self.stream = sd.InputStream(channels=1, callback=self.audio_callback, blocksize=1024, samplerate=44100)
        self.stream.start()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_waveform)
        self.timer.start(30)

        self.threshold = 0.05

    def initUI(self):
        self.container = QWidget(self)
        self.setCentralWidget(self.container)

        self.layout = QVBoxLayout(self.container)
        self.waveform_widget = WaveformWidget()
        self.layout.addWidget(self.waveform_widget)

    def audio_callback(self, indata, frames, time, status):
        if status:
            print(status)
        max_val = np.max(np.abs(indata))
        if max_val > 0:
            self.audio_data = np.squeeze(indata) / max_val
        else:
            self.audio_data = np.squeeze(indata)

    def update_waveform(self):
        self.waveform_widget.update_waveform(self.audio_data)

    def closeEvent(self, event):
        self.timer.stop()
        self.stream.stop()
        self.stream.close()
        super().closeEvent(event)



if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        model = whisper.load_model("medium.en") #tiny base small medium large
        window = MainWindow()
        window.show()
        sys.exit(app.exec_())

    except Exception as e:
        logging.error(f"Error in main execution: {e}")
        print(f"Error in main execution: {e}")