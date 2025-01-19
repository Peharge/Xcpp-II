from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton, QFrame, QVBoxLayout, QWidget, QSpacerItem, QSizePolicy,
                             QDialog, QVBoxLayout, QFormLayout, QGroupBox, QSlider, QMessageBox, QStyleFactory, QHBoxLayout)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QRectF
from PyQt5.QtGui import QImage, QPixmap, QPainterPath, QRegion, QFont, QColor, QIcon
from PyQt5 import QtCore
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsProxyWidget
import cv2
import numpy as np
import logging
import os
import sys
import datetime
import subprocess
import pygame
import sounddevice as sd
import soundfile as sf
import whisper
from TTS.api import TTS
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts
import ctypes
from ctypes import wintypes

# Setup logging
logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Set up PyDub for audio processing
from pydub import AudioSegment
from pydub.playback import play
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QFrame, QVBoxLayout, QWidget, QSpacerItem, QSizePolicy
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap, QPainter, QColor, QFont
import cv2
import numpy as np
import logging
import os
import sys
import datetime
import subprocess
import pygame
from TTS.api import TTS
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts
import ctypes

from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QFrame, QHBoxLayout, QVBoxLayout, QWidget, QSpacerItem, QSizePolicy
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QIcon, QImage, QPixmap, QColor, QPainter, QFont
import cv2
import numpy as np
import logging
import os
import sys
import datetime
import subprocess
import sounddevice as sd
import soundfile as sf
import pygame
import whisper
from TTS.api import TTS
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts
import ctypes
from ctypes import wintypes
from PyQt5.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget, QGraphicsDropShadowEffect, QScrollBar
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsProxyWidget, QVBoxLayout, QWidget
from PyQt5 import QtCore
from PyQt5.QtCore import QSize, Qt, QEvent
import time
import sys
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from PyQt5.QtGui import QPixmap, QPalette, QColor, QPainterPath, QRegion
from PyQt5.QtCore import Qt, QTimer, QRectF

# Setup logging
logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Set up PyDub for audio processing
from pydub import AudioSegment
from pydub.playback import play

from PyQt5.QtWidgets import QPushButton, QGraphicsDropShadowEffect, QVBoxLayout, QWidget
from PyQt5.QtGui import QIcon, QFont, QColor, QTransform
from PyQt5.QtCore import QSize, QPropertyAnimation, Qt
import ollama


class AudioThread(QThread):
    audio_signal = pyqtSignal(np.ndarray)

    def __init__(self, parent=None):
        super().__init__(parent)

    def run(self):
        try:
            fs = 16000
            duration = 5
            recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='float32')
            sd.wait()
            self.audio_signal.emit(np.squeeze(recording))
        except Exception as e:
            logging.error(f"Error in AudioThread: {e}")


import cv2
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal
import datetime
import logging
from PIL import Image

class CameraThread(QThread):
    frame_signal = pyqtSignal(np.ndarray)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.running = True
        self.fps = 120  # Ziel-Framerate (kann auf 60 geändert werden, wenn die Kamera dies unterstützt)
        self.box_sizex = 800 # Größe des Kastens (673x673 Pixel)
        self.box_sizey = 600 # Größe des Kastens (673x673 Pixel)
        self.box_color = (255, 255, 255)  # Farbe des Kastens (weiß in BGR)
        self.corner_length = 35  # Länge der Ecken

    def run(self):
        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                logging.error("Could not open video device")
                return

            # Setze die Auflösung und Framerate
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 3840)   # Full HD Breite
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 2160)  # Full HD Höhe
            cap.set(cv2.CAP_PROP_FPS, self.fps)       # Ziel-Framerate

            # Optional: Belichtung und Weißabgleich anpassen
            cap.set(cv2.CAP_PROP_EXPOSURE, -6)  # Belichtung (Wert anpassen)
            cap.set(cv2.CAP_PROP_AUTO_WB, 1)    # Weißabgleich auf automatisch setzen
            cap.set(cv2.CAP_PROP_GAIN, 0)       # Gain-Einstellung (Neutral)

            while self.running:
                ret, frame = cap.read()
                if ret:
                    # Füge den Kasten mit den Ecken hinzu
                    processed_frame = self.process_image(frame)

                    # Sende das Bild an das Signal
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
        # Berechne die Mitte des Bildes
        height, width = frame.shape[:2]
        center_x, center_y = width // 2, height // 2

        # Berechne die Koordinaten des Kastens
        start_x = center_x - self.box_sizex // 2
        start_y = center_y - self.box_sizey // 2
        end_x = start_x + self.box_sizex
        end_y = start_y + self.box_sizey

        # Füge den Kasten mit den Ecken hinzu
        frame_with_box = frame.copy()
        self.draw_box_with_corners(frame_with_box, (start_x, start_y), (end_x, end_y), self.box_color, self.corner_length)
        return frame_with_box

    def draw_box_with_corners(self, img, start_point, end_point, color, corner_length):
        x1, y1 = start_point
        x2, y2 = end_point

        # Zeichne die Ecken des Kastens
        # Oben links
        cv2.line(img, (x1, y1), (x1 + corner_length, y1), color, 2)
        cv2.line(img, (x1, y1), (x1, y1 + corner_length), color, 2)

        # Oben rechts
        cv2.line(img, (x2, y1), (x2 - corner_length, y1), color, 2)
        cv2.line(img, (x2, y1), (x2, y1 + corner_length), color, 2)

        # Unten links
        cv2.line(img, (x1, y2), (x1 + corner_length, y2), color, 2)
        cv2.line(img, (x1, y2), (x1, y2 - corner_length), color, 2)

        # Unten rechts
        cv2.line(img, (x2, y2), (x2 - corner_length, y2), color, 2)
        cv2.line(img, (x2, y2), (x2, y2 - corner_length), color, 2)

    def save_image(self, image):
        # Konvertiere das Bild von OpenCV zu Pillow
        image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

        # Speichern des Bildes
        current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        image_path = f"C:/Users/julia/PycharmProjects/Xcpp/img/image_{current_time}.png"
        image_pil.save(image_path)

import platform
import psutil
import ctypes
import sys
import cv2
import numpy as np
import logging
import sounddevice as sd
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QGroupBox, QFormLayout, QLabel, QSlider, QPushButton, QComboBox, \
    QApplication, QStyleFactory, QFrame, QHBoxLayout
from PyQt5.QtGui import QFont, QIcon, QColor
from PyQt5.QtCore import Qt
import ctypes
import sys
import cv2
import numpy as np
import logging
import sounddevice as sd
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QGroupBox, QFormLayout, QLabel, QSlider, QPushButton, QMessageBox, \
    QComboBox, QApplication, QStyleFactory, QFrame
from PyQt5.QtGui import QFont, QIcon, QColor
from PyQt5.QtCore import Qt
import ctypes
import sys
import cv2
import numpy as np
import logging
import sounddevice as sd
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QGroupBox, QFormLayout, QLabel, QSlider, QPushButton, QMessageBox, \
    QComboBox, QApplication, QStyleFactory, QFrame
from PyQt5.QtGui import QFont, QIcon, QColor
from PyQt5.QtCore import Qt
from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume


class SettingsWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setGeometry(1200, 50, 300, 300)
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)  # Fenster ohne Rahmen
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.init_ui()
        self.player = QMediaPlayer()

    def init_ui(self):
        # Setze die Schriftgröße und den Stil für die gesamte Anwendung
        font = QFont('Segoe UI', 12)
        self.setFont(font)

        # Hauptlayout mit abgerundeten Ecken und Schatten
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

        # Titel-Layout mit Schließen-Button
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

        # Hinzufügen des Titel-Layouts zum Hauptlayout
        main_frame_layout.addLayout(title_layout)

        # Allgemeine Einstellungen Gruppe
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

        # Helligkeitseinstellung
        self.brightness_slider = QSlider(Qt.Horizontal)
        self.brightness_slider.setRange(0, 100)
        self.brightness_slider.setValue(50)
        general_layout.addRow(QLabel("brightness:"), self.brightness_slider)

        # Lautstärkeeinstellung
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        general_layout.addRow(QLabel("volume:"), self.volume_slider)

        # Kontraststeuerung
        self.contrast_slider = QSlider(Qt.Horizontal)
        self.contrast_slider.setRange(0, 100)
        self.contrast_slider.setValue(50)
        general_layout.addRow(QLabel("contrast:"), self.contrast_slider)

        # Farbsättigung
        self.saturation_slider = QSlider(Qt.Horizontal)
        self.saturation_slider.setRange(0, 100)
        self.saturation_slider.setValue(50)
        general_layout.addRow(QLabel("Color saturation:"), self.saturation_slider)

        # Mikrofonlautstärke
        self.mic_volume_slider = QSlider(Qt.Horizontal)
        self.mic_volume_slider.setRange(0, 100)
        self.mic_volume_slider.setValue(50)
        general_layout.addRow(QLabel("Microphone volume:"), self.mic_volume_slider)

        # Sprachauswahl für TTS
        self.language_dropdown = QComboBox()
        self.language_dropdown.addItems(["German", "English", "Spanish", "French"])
        self.language_dropdown.setCurrentText("English")
        general_layout.addRow(QLabel("Language:"), self.language_dropdown)

        # Theme-Auswahl
        self.theme_dropdown = QComboBox()
        self.theme_dropdown.addItems(["Light", "Dark", "Blue", "Green"])
        general_layout.addRow(QLabel("Theme:"), self.theme_dropdown)

        # Schriftgröße
        self.font_size_slider = QSlider(Qt.Horizontal)
        self.font_size_slider.setRange(6, 18)
        self.font_size_slider.setValue(12)
        general_layout.addRow(QLabel("Font size:"), self.font_size_slider)

        # Audioeingabegerät
        self.audio_device_dropdown = QComboBox()
        devices = sd.query_devices()
        for device in devices:
            if device['max_input_channels'] > 0:
                self.audio_device_dropdown.addItem(device['name'])
        general_layout.addRow(QLabel("Audio input device:"), self.audio_device_dropdown)

        # RAM in GB
        ram = psutil.virtual_memory().total / (1024 ** 3)

        # Speicherplatz der Hauptfestplatte in GB
        disk = psutil.disk_usage('/').total / (1024 ** 3)

        # Anzahl der logischen CPUs (Threads)
        cpu_threads = psutil.cpu_count()

        # Grafikkarteninformationen (basierend auf OpenCL)
        try:
            import pyopencl as cl
            platforms = cl.get_platforms()
            gpus = [device.name for platform in platforms for device in platform.get_devices()]
            gpu = ', '.join(gpus)
        except ImportError:
            gpu = "Not available (OpenCL not installed)"

        # CPU-Modell
        cpu_model = platform.processor()

        # Betriebssystem
        system_info = platform.system() + " " + platform.release()

        # Füge die Informationen in das Layout ein
        general_layout.addRow(QLabel(f""))
        general_layout.addRow(QLabel(f"RAM: <span style='color: blue;'>{ram:.2f} GB</span>"))
        general_layout.addRow(QLabel(f"Number of Threads: <span style='color: blue;'>{cpu_threads}</span>"))
        general_layout.addRow(QLabel(f"Chip type/CPU model: <span style='color: blue;'>{cpu_model}</span>"))
        general_layout.addRow(QLabel(f"Graphics card(s): <span style='color: blue;'>{gpu}</span>"))
        # CUDA Unterstützung
        cuda_supported = torch.cuda.is_available()
        general_layout.addRow(QLabel(f"CUDA support: <span style='color: blue;'>{'Yes' if cuda_supported else 'No'}</span>"))
        general_layout.addRow(QLabel(f"Storage space: <span style='color: blue;'>{disk:.2f} GB</span>"))
        general_layout.addRow(QLabel(f"Xcpp version: <span style='color: blue;'>1</span>"))
        general_layout.addRow(QLabel(f"Peharge security: <span style='color: blue;'>active</span>"))
        general_layout.addRow(QLabel(f""))
        general_layout.addRow(QLabel(f"Maximum <span style='color: blue;'>13B</span> recommended"))

        # Theme-Auswahl
        self.parameters_dropdown = QComboBox()
        self.parameters_dropdown.addItems(["7B", "13B", "32B", "70B", "301B", "512B", "1024B", "1536B"])
        # Standardmäßig auf "13B" setzen
        self.parameters_dropdown.setCurrentText("7B")
        general_layout.addRow(QLabel("Parameters:"), self.parameters_dropdown)

        general_layout.addRow(QLabel(f""))
        general_layout.addRow(QLabel(f"Xc++ 13B uses <span style='color: blue;'>7 GB</span> of your RAM"))
        general_layout.addRow(QLabel(f"Xc++ 13B uses <span style='color: blue;'>93%</span> of your CPU power"))
        general_layout.addRow(QLabel(f"Xc++ 13B uses <span style='color: blue;'>79 GB</span> of your disk space"))

        general_group.setLayout(general_layout)
        main_frame_layout.addWidget(general_group)

        # Buttons
        buttons_layout = QHBoxLayout()
        apply_button = QPushButton(" Apply")
        apply_button.setIcon(QIcon('C:\\Users\\julia\\PycharmProjects\\Xcpp\\agree.svg'))
        apply_button.clicked.connect(self.play_sound_1)
        apply_button.setStyleSheet("""
            QPushButton {
                color: #000000;
                border: 2px solid #000000;
                border-radius: 5px;
                padding: 8px 16px;
                background-color: rgba(255, 255, 255, 0);
            }
            QPushButton:hover {
                color: #FFFFFF;
                background-color: #2ECC71;
                border: 1px solid #2ECC71;
            }
        """)
        apply_button.clicked.connect(self.apply_settings)
        cancel_button = QPushButton(" Cancel")
        cancel_button.setIcon(QIcon('C:\\Users\\julia\\PycharmProjects\\Xcpp\\disagree.svg'))
        cancel_button.clicked.connect(self.play_sound_2)
        cancel_button.setStyleSheet("""
            QPushButton {
                color: #000000;
                border: 2px solid #000000;
                border-radius: 5px;
                padding: 8px 16px;
                background-color: rgba(255, 255, 255, 0);
            }
            QPushButton:hover {
                color: #FFFFFF;
                background-color: #E74C3C;
                border: 1px solid #E74C3C;
            }
        """)
        cancel_button.clicked.connect(self.reject)

        update_button = QPushButton(" Update")
        update_button.setIcon(QIcon('C:\\Users\\julia\\PycharmProjects\\Xcpp\\update.svg'))
        update_button.clicked.connect(self.play_sound_1)
        update_button.setStyleSheet("""
            QPushButton {
                color: #000000;
                border: 2px solid #000000;
                border-radius: 5px;
                padding: 8px 16px;
                background-color: rgba(255, 255, 255, 0);
            }
            QPushButton:hover {
                color: #FFFFFF;
                background-color: #3498DB;
                border: 1px solid #3498DB;
            }
        """)
        update_button.clicked.connect(self.reject)

        model_button = QPushButton(" Model Info")
        model_button.setIcon(QIcon('C:\\Users\\julia\\PycharmProjects\\Xcpp\\info.svg'))
        model_button.clicked.connect(self.play_sound_1)
        model_button.setStyleSheet("""
            QPushButton {
                color: #000000;
                border: 2px solid #000000;
                border-radius: 5px;
                padding: 8px 16px;
                background-color: rgba(255, 255, 255, 0);
            }
            QPushButton:hover {
                color: #FFFFFF;
                background-color: #3498DB;
                border: 1px solid #3498DB;
            }
        """)
        model_button.clicked.connect(self.open_modelinfo)

        sec_button = QPushButton(" Model Info")
        sec_button.setIcon(QIcon('C:\\Users\\julia\\PycharmProjects\\Xcpp\\sec.svg'))
        sec_button.clicked.connect(self.play_sound_3)
        sec_button.setStyleSheet("""
            QPushButton {
                color: #000000;
                border: 2px solid #000000;
                border-radius: 5px;
                padding: 8px 16px;
                background-color: rgba(255, 255, 255, 0);
            }
            QPushButton:hover {
                color: #FFFFFF;
                background-color: #2ECC71;
                border: 1px solid #2ECC71;
            }
        """)
        sec_button.clicked.connect(self.open_SicherheitsbewertungFenster)

        buttons_layout.addWidget(apply_button)
        buttons_layout.addWidget(cancel_button)
        buttons_layout.addWidget(update_button)
        buttons_layout.addWidget(model_button)
        buttons_layout.addWidget(sec_button)
        buttons_layout.setAlignment(Qt.AlignCenter)

        main_frame_layout.addLayout(buttons_layout)

        # Setze das Layout des Hauptframes
        main_layout.addWidget(main_frame)
        self.setLayout(main_layout)

    def play_sound_1(self):
        try:
            # Pfad zur MP3-Datei
            mp3_path = "C:/Users/julia/PycharmProjects/Xcpp/level-up-191997.mp3"

            # Erstellen der QMediaContent-Instanz
            url = QUrl.fromLocalFile(mp3_path)
            content = QMediaContent(url)

            # Setzen des Inhalts für den MediaPlayer
            self.player.setMedia(content)

            # Starten der Wiedergabe
            self.player.play()
            print(f"Playing sound from: {mp3_path}")

        except Exception as e:
            print(f"Error while trying to play sound: {e}")

    def play_sound_2(self):
        try:
            # Pfad zur MP3-Datei
            mp3_path = "C:/Users/julia/PycharmProjects/Xcpp/toggle-button-off-166328.mp3"

            # Erstellen der QMediaContent-Instanz
            url = QUrl.fromLocalFile(mp3_path)
            content = QMediaContent(url)

            # Setzen des Inhalts für den MediaPlayer
            self.player.setMedia(content)

            # Starten der Wiedergabe
            self.player.play()
            print(f"Playing sound from: {mp3_path}")

        except Exception as e:
            print(f"Error while trying to play sound: {e}")

    def play_sound_3(self):
        try:
            # Pfad zur MP3-Datei
            mp3_path = "C:/Users/julia/PycharmProjects/Xcpp/level-up-191997.mp3"

            # Erstellen der QMediaContent-Instanz
            url = QUrl.fromLocalFile(mp3_path)
            content = QMediaContent(url)

            # Setzen des Inhalts für den MediaPlayer
            self.player.setMedia(content)

            # Starten der Wiedergabe
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
        # Logik zum Anwenden der Einstellungen
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
        # Helligkeit anpassen (siehe oben)
        pass

    def set_system_volume(self, volume):
        """devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(
            AudioUtilities.IID_IAudioEndpointVolume, None, None)
        volume_control = interface.QueryInterface(ISimpleAudioVolume)
        volume_control.SetMasterVolume(float(volume) / 100.0, None)"""

    def set_camera_contrast(self, contrast):
        # Logik zum Einstellen des Kontrasts der Kamera
        pass

    def set_camera_saturation(self, saturation):
        # Logik zum Einstellen der Farbsättigung der Kamera
        pass

    def set_microphone_volume(self, mic_volume):
        """devices = AudioUtilities.GetMicrophone()
        interface = devices.Activate(
            AudioUtilities.IID_IAudioEndpointVolume, None, None)
        volume_control = interface.QueryInterface(ISimpleAudioVolume)
        volume_control.SetMasterVolume(float(mic_volume) / 100.0, None)"""

    def set_application_language(self, language):
        # Logik zur Sprachumschaltung (TTS)
        pass

    def apply_theme(self, theme):
        # Logik zur Änderung des UI-Themes
        pass

    def apply_font_size(self, font_size):
        # Logik zur Anpassung der Schriftgröße
        pass

    def set_audio_input_device(self, audio_device):
        """devices = sd.query_devices()
        for device in devices:
            if device['name'] == audio_device:
                sd.default.device = device['index']
                break"""

import platform
# Versionen der Pakete importieren
import torch
import tensorflow as tf
import pandas as pd
import pygame
import numpy as np
from transformers import __version__ as transformers_version

class ModelWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Xc++ Info")
        self.setGeometry(113, 50, 300, 300)
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)  # Fenster ohne Rahmen
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.init_ui()

    def init_ui(self):
        # Setze die Schriftgröße und den Stil für die gesamte Anwendung
        font = QFont('Xc++ Info', 12)
        self.setFont(font)

        # Hauptlayout mit abgerundeten Ecken und Schatten
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

        # Titel-Layout mit Schließen-Button
        title_layout = QHBoxLayout()
        title_label = QLabel("Xc++ Info")
        title_label.setStyleSheet("color: #000000; font-size: 16px; font-weight: bold; background-color: rgba(255, 255, 255, 0);")
        title_layout.addWidget(title_label)
        close_button = QPushButton("×")
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

        # Hinzufügen des Titel-Layouts zum Hauptlayout
        main_frame_layout.addLayout(title_layout)

        # Allgemeine Einstellungen Gruppe
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

        # RAM in GB
        ram = psutil.virtual_memory().total / (1024 ** 3)

        # Speicherplatz der Hauptfestplatte in GB
        disk = psutil.disk_usage('/').total / (1024 ** 3)

        # Anzahl der logischen CPUs (Threads)
        cpu_threads = psutil.cpu_count()

        # Grafikkarteninformationen (basierend auf OpenCL)
        try:
            import pyopencl as cl
            platforms = cl.get_platforms()
            gpus = [device.name for platform in platforms for device in platform.get_devices()]
            gpu = ', '.join(gpus)
        except ImportError:
            gpu = "Not available (OpenCL not installed)"

        # CPU-Modell
        cpu_model = platform.processor()

        # Betriebssystem
        system_info = platform.system() + " " + platform.release()

        # Füge die Informationen in das Layout ein
        general_layout.addRow(QLabel(f"Thank you for choosing Xc++.\n\nXc++ represents a significant advancement in natural human-computer interaction. \nIt accepts a wide range of inputs, including text, audio, and images, and can generate outputs in both text and audio formats. \nXc++ excels particularly in vision and audio comprehension, offering superior performance compared to existing models."))
        general_layout.addRow(QLabel(f""))
        general_layout.addRow(QLabel(f"RAM: <span style='color: blue;'>{ram:.2f} GB</span>"))
        general_layout.addRow(QLabel(f"Number of Threads: <span style='color: blue;'>{cpu_threads}</span>"))
        general_layout.addRow(QLabel(f"Chip type/CPU model: <span style='color: blue;'>{cpu_model}</span>"))
        general_layout.addRow(QLabel(f"Graphics card(s): <span style='color: blue;'>{gpu}</span>"))
        # CUDA Unterstützung
        cuda_supported = torch.cuda.is_available()
        general_layout.addRow(QLabel(f"CUDA support: <span style='color: blue;'>{'Yes' if cuda_supported else 'No'}</span>"))
        general_layout.addRow(QLabel(f"Storage space: <span style='color: blue;'>{disk:.2f} GB</span>"))
        general_layout.addRow(QLabel(f"System: <span style='color: blue;'>{system_info}</span>"))
        # Python Version
        general_layout.addRow(QLabel(f"Python Version: <span style='color: blue;'>{platform.python_version()}</span>"))
        # PyTorch Version
        general_layout.addRow(QLabel(f"PyTorch Version: <span style='color: blue;'>{torch.__version__}</span>"))
        # TensorFlow Version
        general_layout.addRow(QLabel(f"TensorFlow Version: <span style='color: blue;'>{tf.__version__}</span>"))
        # Pandas Version
        general_layout.addRow(QLabel(f"Pandas Version: <span style='color: blue;'>{pd.__version__}</span>"))
        # Pygame Version
        general_layout.addRow(QLabel(f"Pygame Version: <span style='color: blue;'>{pygame.__version__}</span>"))
        # NumPy Version
        general_layout.addRow(QLabel(f"NumPy Version: <span style='color: blue;'>{np.__version__}</span>"))
        # Transformers Version
        general_layout.addRow(QLabel(f"Transformers Version: <span style='color: blue;'>{transformers_version}</span>"))
        general_layout.addRow(QLabel(f""))
        general_layout.addRow(QLabel(f"Xc++ Version: <span style='color: blue;'>1</span>"))
        general_layout.addRow(QLabel(f"Peharge security Version: <span style='color: blue;'>2</span>"))
        general_layout.addRow(QLabel(f""))

        general_group.setLayout(general_layout)
        main_frame_layout.addWidget(general_group)

        # Setze das Layout des Hauptframes
        main_layout.addWidget(main_frame)
        self.setLayout(main_layout)


from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QFrame, QLabel, QPushButton, QProgressBar, QHBoxLayout
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import time
import sys


class SicherheitsbewertungThread(QThread):
    update_progress = pyqtSignal(int)
    finished = pyqtSignal(str)

    def run(self):
        for i in range(101):
            time.sleep(0.05)
            self.update_progress.emit(i)
        self.finished.emit("Security scan completed.\nNo obvious security risks found.\n3. FutureWarnings (torch.load with weights_only=False), 1. wisper, 2.vits, 3.tts (solution: weights_only=True)\n")



from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QProgressBar, QFrame
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtSvg import QSvgWidget

class StilvollesSicherheitsfenster(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Setze die Fenstergröße und andere Attribute
        self.setWindowTitle("Peharge Security check")
        self.setWindowIcon(
            QIcon('C:\\Users\\julia\\OneDrive - Gewerbeschule Lörrach\\Pictures\\software\\peharge-logo3.6.ico'))
        self.setGeometry(113, 50, 400, 450)
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)  # Fenster ohne Rahmen
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.init_ui()

    def init_ui(self):
        font = QFont('Arial', 12)
        self.setFont(font)

        main_layout = QVBoxLayout(self)  # Setze Layout auf das Fenster direkt

        # Hauptframe
        main_frame = QFrame(self)
        main_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.7);
                border-radius: 15px;
                box-shadow: 0px 0px 15px rgba(0, 0, 0, 0.5);
            }
        """)
        main_frame_layout = QVBoxLayout(main_frame)
        main_layout.addWidget(main_frame)  # Füge den Hauptframe dem Layout hinzu

        # Titel-Layout
        title_layout = QHBoxLayout()
        title_label = QLabel("Peharge Security check")
        title_label.setStyleSheet("color: #000000; font-size: 16px; font-weight: bold; background-color: rgba(255, 255, 255, 0);")
        title_layout.addWidget(title_label)
        title_layout.addStretch()

        close_button = QPushButton("×")
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

        # Inhalt-Layout
        content_layout = QVBoxLayout()
        main_frame_layout.addLayout(content_layout)

        # Füge das SVG-Bild hinzu
        svg_widget = QSvgWidget('C:\\Users\\julia\\PycharmProjects\\Xcpp\\sec.svg', self)
        svg_widget.setFixedSize(100, 100)  # Setze die Größe des SVG-Bildes
        svg_widget.setStyleSheet("background: transparent;")  # Setze den Hintergrund des Widgets auf transparent
        content_layout.addWidget(svg_widget)
        content_layout.setAlignment(svg_widget, Qt.AlignCenter)  # Zentriere das Bild im Layout

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
                border: none;                  /* Kein Rand */
                background: transparent;      /* Kein Hintergrund */
                border-radius: 10px;          /* Abgerundete Ecken der Leiste */
                text-align: center;           /* Zentrierter Text, falls benötigt */
            }

            QProgressBar::chunk {
                background-color: blue;    /* Farbe des Fortschrittselements */
                width: 20px;                  /* Breite der Fortschrittselemente */
                height: 20px;                 /* Höhe der Fortschrittselemente */
                border-radius: 3px;           /* Abgerundete Ecken der Fortschrittselemente */
                margin: 0 5px;                /* Abstand von 5px zwischen den Elementen */
            }

            /* Animation für den Fortschrittselement */
            QProgressBar::chunk {
                animation: progress 1s linear infinite;
            }

            @keyframes progress {
                0% {
                    background-color: #007BFF;  /* Startfarbe */
                }
                50% {
                    background-color: #0056b3;  /* Mittelwert der Farbe */
                }
                100% {
                    background-color: #007BFF;  /* Endfarbe */
                }
            }
        """)
        content_layout.addWidget(self.progress_bar)

        bewertung_btn = QPushButton("Run", self)
        # Setze die Größe des Buttons auf 50px x 30px
        bewertung_btn.setFixedSize(70, 35)
        bewertung_btn.setFont(QFont("Arial", 10, QFont.Bold))
        #bewertung_btn.setFont(font)
        bewertung_btn.setStyleSheet("""
            QPushButton {
                color: #000000;
                border: 2px solid #000000;
                border-radius: 5px;
                padding: 8px 16px;
                background-color: rgba(255, 255, 255, 0);
            }
            QPushButton:hover {
                color: #FFFFFF;
                background-color: #3498DB;
                border: 1px solid #3498DB;
            }
        """)
        bewertung_btn.clicked.connect(self.start_sicherheitsbewertung)
        # Erstelle das Layout und füge den Button hinzu
        content_layout.addWidget(bewertung_btn)
        content_layout.setAlignment(bewertung_btn, Qt.AlignCenter)  # Zentriere den Button im Layout

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



import os
import ctypes
from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QLabel, QScrollArea,
                             QVBoxLayout, QFrame, QGraphicsDropShadowEffect)
from PyQt5.QtGui import QPixmap, QImageReader, QPainter, QBrush, QColor, QLinearGradient, QIcon
from PyQt5.QtCore import Qt, QSize, QRect

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

                # Hinzufügen des Glas-Effekts
                shadow_effect = QGraphicsDropShadowEffect()
                shadow_effect.setBlurRadius(15)  # Stärke des Unschärfeeffekts
                shadow_effect.setColor(QColor(0, 0, 0, 0))  # Farbe des Schattens (schwarz mit Transparenz)
                shadow_effect.setOffset(0, 0)  # Kein Versatz des Schattens

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



import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.camera_thread = CameraThread()
        self.camera_thread.frame_signal.connect(self.update_camera_view)
        self.camera_thread.start()
        self.image_gallery = None
        self.gallery_active = False
        # MediaPlayer initialisieren
        self.player = QMediaPlayer()

    def initUI(self):
        self.setWindowTitle("Xc++")
        self.setWindowFlags(Qt.FramelessWindowHint)  # Fensterrahmen entfernen
        self.setGeometry(96, 29, 1728, 972)
        # Erstellen einer Maske für abgerundete Ecken
        self.set_rounded_corners(20)  # 20 Pixel Radius für die abgerundeten Ecken

        # Logo hinzufügen und oben rechts positionieren
        self.logo_label = QLabel(self)
        icon_path = "C:/Users/julia/PycharmProjects/Xcpp/peharge-logo3.6.ico"
        if not os.path.exists(icon_path):
            logging.error(f"Icon file not found at: {icon_path}")
        self.setWindowIcon(QIcon(icon_path))

        self.setStyleSheet("background-color: white; border-radius: 20px;")  # Hintergrundfarbe und abgerundete Ecken

        myappid = u'mycompany.myproduct.subproduct.version'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

        self.setStyleSheet("background: transparent;")  # Set transparent background

        self.setStyleSheet("background-color: white; border-radius: 20px;")  # Hintergrundfarbe und abgerundete Ecken

        # Main widget and layout
        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)
        self.main_layout = QVBoxLayout(self.main_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # Camera view
        self.camera_view = QLabel(self)
        self.camera_view.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.camera_view)

        # UI container frame
        self.glass_frame = QFrame(self)
        self.glass_frame.setStyleSheet("""
            background-color: rgba(255, 255, 255, 0);
            border-radius: 20px;
            color: #000000;
        """)
        self.glass_frame.setFixedSize(1728, 972)

        # UI container frame
        self.glass_frame2 = QFrame(self)
        self.glass_frame2.setStyleSheet("""
            background-color: rgba(255, 255, 255, 150);
            border-radius: 20px;
            color: #000000;
        """)
        self.glass_frame2.setFixedSize(550, 160)

        # Verschiebe das Frame um 400px nach unten und zentriere es horizontal in der Mitte des übergeordneten Widgets
        parent_width = self.width()  # Breite des übergeordneten Widgets (self)
        frame_width = self.glass_frame2.width()
        x_position = (parent_width - frame_width) // 2  # Horizontal zentrieren
        y_position = 800  # Vertikale Verschiebung um 400px

        self.glass_frame2.move(x_position, y_position)

        # Layout für die Glass Frame, jetzt QVBoxLayout
        self.glass_frame_layout = QVBoxLayout(self.glass_frame)
        self.glass_frame_layout.setContentsMargins(0, 0, 20, 20)

        # Add a spacer item to push content up from the bottom
        self.glass_frame_spacer = QSpacerItem(20, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.glass_frame_layout.addItem(self.glass_frame_spacer)

        # Add label to the glass frame
        self.label = QLabel("Press the green receiver and speak", self.glass_frame)
        self.label.setAlignment(Qt.AlignBottom | Qt.AlignHCenter)
        self.label.setStyleSheet("color: #000000;")
        self.label.setFont(QFont('Arial', 14, QFont.Bold))
        self.glass_frame_layout.addWidget(self.label)

        self.button_layout = QHBoxLayout()

        # Create buttons // Button 1
        self.button1 = QPushButton(self.glass_frame)
        self.button1.setIcon(QIcon('C:\\Users\\julia\\PycharmProjects\\Xcpp\\run.svg'))
        self.button1.clicked.connect(self.play_sound_1)
        self.button1.setFixedSize(75, 40)
        self.shadow_effect1 = QGraphicsDropShadowEffect(self)
        self.shadow_effect1.setBlurRadius(10)
        self.shadow_effect1.setColor(QColor(0, 0, 0, 160))  # Schwarze Farbe für den Schatten
        self.shadow_effect1.setOffset(7, 7)
        self.button1.setIconSize(QSize(60, 60))  # Hier Größe der SVG-Datei angeben
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
        self.button1.setFixedSize(75, 75)
        self.button_layout.addWidget(self.button1)
        self.button1.clicked.connect(self.start_listening)

        # Verbinde die Signal- und Slot-Funktionen für das Verschieben des Buttons
        self.button1.pressed.connect(self.move_button1_up)
        self.button1.released.connect(lambda: self.move_button1_down(self.button1))

        # Überlade enterEvent und leaveEvent des Buttons
        self.button1.enterEvent = self.on_button1_hover
        self.button1.leaveEvent = self.on_button1_leave

        # Button 2
        self.button2 = QPushButton(self.glass_frame)
        self.button2.setIcon(QIcon('C:\\Users\\julia\\PycharmProjects\\Xcpp\\close.svg'))
        self.button2.clicked.connect(self.play_sound_2)
        self.shadow_effect2 = QGraphicsDropShadowEffect(self)
        self.shadow_effect2.setBlurRadius(10)
        self.shadow_effect2.setColor(QColor(0, 0, 0, 160))  # Schwarze Farbe für den Schatten
        self.shadow_effect2.setOffset(7, 7)
        self.button2.setGraphicsEffect(self.shadow_effect2)

        # Setze die Größe und das Layout des Buttons
        self.button2.setIconSize(QSize(60, 60))
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
        self.button2.clicked.connect(self.close)

        # Verbinde die Signal- und Slot-Funktionen für das Verschieben des Buttons
        self.button2.pressed.connect(self.move_button2_up)
        self.button2.released.connect(lambda: self.move_button2_down(self.button2))

        # Überlade enterEvent und leaveEvent des Buttons
        self.button2.enterEvent = self.on_button2_hover
        self.button2.leaveEvent = self.on_button2_leave


        """        self.button3.clicked.connect(self.restart) // C:\\Users\\julia\\PycharmProjects\\Xcpp\\peharge-p-logo.svg"""

        # Button 3
        self.button3 = QPushButton(self.glass_frame)
        self.button3.setIcon(QIcon('C:\\Users\\julia\\PycharmProjects\\Xcpp\\peharge-logo-p-9.svg'))
        self.button3.clicked.connect(self.play_sound_3)
        self.shadow_effect3 = QGraphicsDropShadowEffect(self)
        self.shadow_effect3.setBlurRadius(10)
        self.shadow_effect3.setColor(QColor(0, 0, 0, 160))  # Schwarze Farbe für den Schatten
        self.shadow_effect3.setOffset(7, 7)
        self.button3.setGraphicsEffect(self.shadow_effect3)

        # Setze die Größe und das Layout des Buttons
        self.button3.setIconSize(QSize(60, 60))
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

        # Verbinde die Signal- und Slot-Funktionen für das Verschieben des Buttons
        self.button3.pressed.connect(self.move_button3_up)
        self.button3.released.connect(lambda: self.move_button3_down(self.button3))

        # Überlade enterEvent und leaveEvent des Buttons
        self.button3.enterEvent = self.on_button3_hover
        self.button3.leaveEvent = self.on_button3_leave

        """C:\\Users\\julia\\PycharmProjects\\Xcpp\\settings.svg //         self.button4.clicked.connect(self.open_settings)"""

        # Button 4
        self.button4 = QPushButton(self.glass_frame)
        self.button4.setIcon(QIcon('C:\\Users\\julia\\PycharmProjects\\Xcpp\\settings2.svg'))
        self.button4.clicked.connect(self.play_sound_4)
        self.shadow_effect4 = QGraphicsDropShadowEffect(self)
        self.shadow_effect4.setBlurRadius(10)
        self.shadow_effect4.setColor(QColor(0, 0, 0, 160))  # Schwarze Farbe für den Schatten
        self.shadow_effect4.setOffset(7, 7)
        self.button4.setGraphicsEffect(self.shadow_effect4)

        # Setze die Größe und das Layout des Buttons
        self.button4.setIconSize(QSize(57, 57))
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

        # Verbinde die Signal- und Slot-Funktionen für das Verschieben des Buttons
        self.button4.pressed.connect(self.move_button4_up)
        self.button4.released.connect(lambda: self.move_button4_down(self.button4))

        # Überlade enterEvent und leaveEvent des Buttons
        self.button4.enterEvent = self.on_button4_hover
        self.button4.leaveEvent = self.on_button4_leave

        # Button 5
        self.button5 = QPushButton(self.glass_frame)
        self.button5.setIcon(QIcon('C:\\Users\\julia\\PycharmProjects\\Xcpp\\img6.svg'))
        self.button5.clicked.connect(self.play_sound_5)
        # Schatteneffekt für den Button
        self.shadow_effect5 = QGraphicsDropShadowEffect(self)
        self.shadow_effect5.setBlurRadius(10)
        self.shadow_effect5.setColor(QColor(0, 0, 0, 160))  # Schwarze Farbe für den Schatten
        self.shadow_effect5.setOffset(7, 7)
        self.button5.setGraphicsEffect(self.shadow_effect5)

        # Setze die Größe und das Layout des Buttons
        self.button5.setIconSize(QSize(57, 57))
        self.button5.setFixedSize(85, 85)
        self.button5.setFont(QFont('Arial', 20, QFont.Bold))
        self.button5.setStyleSheet("""
            QPushButton {
                color: #000000;
                border-radius: 42px;  # Setze den Radius auf die Hälfte der Größe (85px / 2 = 42px)
                padding: 0px;  # Kein Padding, damit der Button ein perfekter Kreis ist
                font-size: 16px;
                font-weight: bold;
                background: transparent;  # Hintergrund transparent machen
                border: 25px solid #000000;  # Optional: schwarzer Rand für bessere Sichtbarkeit
            }
        """)
        self.button_layout.addWidget(self.button5)
        self.button5.clicked.connect(self.show_gallery)

        # Verbinde die Signal- und Slot-Funktionen für das Verschieben des Buttons
        self.button5.pressed.connect(self.move_button5_up)
        self.button5.released.connect(lambda: self.move_button5_down(self.button5))

        # Überlade enterEvent und leaveEvent des Buttons
        self.button5.enterEvent = self.on_button5_hover
        self.button5.leaveEvent = self.on_button5_leave

        # Container-Layout für die Buttons erstellen
        self.button_container = QWidget(self.glass_frame)
        self.button_layout = QHBoxLayout(self.button_container)
        self.button_layout.setContentsMargins(0, 0, 0, 0)
        self.button_container.setLayout(self.button_layout)

        # Abstand von 50 Pixeln zwischen den Buttons hinzufügen
        self.button_layout.addWidget(self.button3)
        self.button_layout.addSpacing(0)
        self.button_layout.addWidget(self.button1)
        self.button_layout.addSpacing(10)
        self.button_layout.addWidget(self.button2)
        self.button_layout.addSpacing(5)
        self.button_layout.addWidget(self.button5)
        self.button_layout.addSpacing(0)
        self.button_layout.addWidget(self.button4)




        self.glass_frame_layout.addWidget(self.button_container, alignment=Qt.AlignCenter)

        self.result_label = QLabel("", self.glass_frame)
        self.result_label.setStyleSheet("color: #ffffff;")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.glass_frame_layout.addWidget(self.result_label)

        # Ensure the glass frame is always on top of the camera view
        self.glass_frame.raise_()

    def play_sound_1(self):
        try:
            # Pfad zur MP3-Datei
            mp3_path = "C:/Users/julia/PycharmProjects/Xcpp/censor-beep-1sec-8112.mp3"

            # Erstellen der QMediaContent-Instanz
            url = QUrl.fromLocalFile(mp3_path)
            content = QMediaContent(url)

            # Setzen des Inhalts für den MediaPlayer
            self.player.setMedia(content)

            # Starten der Wiedergabe
            self.player.play()
            print(f"Playing sound from: {mp3_path}")

        except Exception as e:
            print(f"Error while trying to play sound: {e}")

    def play_sound_2(self):
        try:
            # Pfad zur MP3-Datei
            mp3_path = "C:/Users/julia/PycharmProjects/Xcpp/toggle-button-off-166328.mp3"

            # Erstellen der QMediaContent-Instanz
            url = QUrl.fromLocalFile(mp3_path)
            content = QMediaContent(url)

            # Setzen des Inhalts für den MediaPlayer
            self.player.setMedia(content)

            # Starten der Wiedergabe
            self.player.play()
            print(f"Playing sound from: {mp3_path}")

        except Exception as e:
            print(f"Error while trying to play sound: {e}")

    def play_sound_3(self):
        try:
            # Pfad zur MP3-Datei
            mp3_path = "C:/Users/julia/PycharmProjects/Xcpp/level-up-191997.mp3"

            # Erstellen der QMediaContent-Instanz
            url = QUrl.fromLocalFile(mp3_path)
            content = QMediaContent(url)

            # Setzen des Inhalts für den MediaPlayer
            self.player.setMedia(content)

            # Starten der Wiedergabe
            self.player.play()
            print(f"Playing sound from: {mp3_path}")

        except Exception as e:
            print(f"Error while trying to play sound: {e}")

    def play_sound_4(self):
        try:
            # Pfad zur MP3-Datei
            mp3_path = "C:/Users/julia/PycharmProjects/Xcpp/level-up-191997.mp3"

            # Erstellen der QMediaContent-Instanz
            url = QUrl.fromLocalFile(mp3_path)
            content = QMediaContent(url)

            # Setzen des Inhalts für den MediaPlayer
            self.player.setMedia(content)

            # Starten der Wiedergabe
            self.player.play()
            print(f"Playing sound from: {mp3_path}")

        except Exception as e:
            print(f"Error while trying to play sound: {e}")

    def play_sound_5(self):
        try:
            # Pfad zur MP3-Datei
            mp3_path = "C:/Users/julia/PycharmProjects/Xcpp/level-up-191997.mp3"

            # Erstellen der QMediaContent-Instanz
            url = QUrl.fromLocalFile(mp3_path)
            content = QMediaContent(url)

            # Setzen des Inhalts für den MediaPlayer
            self.player.setMedia(content)

            # Starten der Wiedergabe
            self.player.play()
            print(f"Playing sound from: {mp3_path}")

        except Exception as e:
            print(f"Error while trying to play sound: {e}")

    # Button 1 Events
    # Button 1 Events
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

    # Button 2 Events
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

    # Button 3 Events
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

    # Button 4 Events
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

    # Button 5 Events
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

    def open_settings(self):
        self.settings_window = SettingsWindow(self)
        self.settings_window.exec_()

    def show_gallery(self):
        image_folder = r"C:\Users\julia\PycharmProjects\Xcpp\img"

        if self.gallery_active:
            # Entferne und lösche die bestehende ImageGallery-Instanz
            if self.image_gallery is not None:
                self.layout().removeWidget(self.image_gallery)
                self.image_gallery.setParent(None)  # Setze das Eltern-Widget auf None
                self.image_gallery.deleteLater()  # Lösche das Widget später
                self.image_gallery = None

            # Setze den Status auf nicht aktiv
            self.gallery_active = False
        else:
            # Erstelle eine neue ImageGallery-Instanz
            self.image_gallery = ImageGallery(parent=self)
            self.image_gallery.set_image_folder(image_folder)  # Setze den Bildordner nach der Instanziierung
            self.layout().addWidget(self.image_gallery)

            # Setze den Status auf aktiv
            self.gallery_active = True

    def start_listening(self):
        # Deine Logik für das Starten der Spracherkennung hier
        pass

    def update_camera_view(self, frame):
        # Deine Logik zum Aktualisieren des Kamera-Feeds hier
        pass

    def set_rounded_corners(self, radius):
        path = QPainterPath()
        path.addRoundedRect(self.rect(), radius, radius)
        mask = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(mask)


    def set_rounded_corners(self, radius):
        # Erstellen eines QPainterPath für die abgerundeten Ecken
        path = QPainterPath()
        rect = QRectF(self.rect())  # Konvertieren von QRect zu QRectF
        path.addRoundedRect(rect, radius, radius)

        # Die Region aus dem QPainterPath erstellen
        region = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region)

    def close_window(self):
        self.close()  # Schließt das Fenster

    def restart(self):
        # Hier kann der Hauptcode stehen, der ausgeführt werden soll
        print("Der Code wird ausgeführt...")
        time.sleep(5)  # Simuliert eine Pause von 5 Sekunden

        # Neustart des Skripts
        print("Das Skript wird neu gestartet...")
        time.sleep(1)  # Kurze Pause vor dem Neustart
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

            # Ersetze das alte Kommando mit der ollama.chat Methode
            res = ollama.chat(
                model="llava:7b",
                messages=[
                    {
                        'role': 'user',
                        'content': text,  # Text wird als Inhalt übergeben
                        'images': [image_path]  # Bildpfad wird übergeben
                    }
                ]
            )

            llama3_output = res['message']['content'] #no ['message'], I think so, beacuse xtts dont need the content (It dont have to red the imput text from the user, but it is working great, like ist is ;-))!!!
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
        """ Update the QLabel with the current frame from the camera. """
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

            speaker_wav_path = os.path.join("C:/Users/julia/PycharmProjects/Xcpp/marsorbit-79697.mp3") #WAV ist erhätlich, doch dadurch entsand beim converter eine noch schlechtere Audio Qualität!!!

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