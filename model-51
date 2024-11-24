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


class CameraThread(QThread):
    frame_signal = pyqtSignal(np.ndarray)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.running = True

    def run(self):
        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                logging.error("Could not open video device")
                return

            while self.running:
                ret, frame = cap.read()
                if ret:
                    self.frame_signal.emit(frame)
                else:
                    logging.error("Could not read frame")
                    break

            cap.release()
        except Exception as e:
            logging.error(f"Error in CameraThread: {e}")

    def stop(self):
        self.running = False


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
        self.setWindowTitle("Einstellungen")
        self.setStyle(QStyleFactory.create('Fusion'))
        self.init_ui()

    def init_ui(self):
        # Setze die Schriftgröße für die gesamte Anwendung auf 12px
        font = QFont('Arial', 14)
        self.setFont(font)

        # Hauptlayout
        main_layout = QVBoxLayout()
        general_group = QGroupBox("\n\nAllgemeine Einstellungen\n\n")
        general_layout = QFormLayout()

        # Setze das Fenster-Icon
        self.setWindowIcon(QIcon(
            'C:\\Users\\julia\\OneDrive - Gewerbeschule Lörrach\\Pictures\\software\\peharge-logo3.6.ico'))

        # Setze die App-ID für das Windows-Taskleisten-Icon
        myappid = u'mycompany.myproduct.subproduct.version'  # Arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

        background_color = QColor(255, 255, 255)
        self.setStyleSheet("background-color: rgb({},{},{})".format(
            background_color.red(), background_color.green(),
            background_color.blue()))

        #self.setWindowOpacity(0.75)

        glass_frame = QFrame(self)
        glass_frame.setGeometry(0, 0, 1920, 1000)
        glass_frame.setStyleSheet("""
            background-color: rgb(255, 255, 255);
            color: #000000;
            border-radius: 10px;
        """)


        # Setze das Hauptfenster-Design
        self.setStyleSheet("""
            SettingsWindow {
                background-color: rgba(255, 255, 255);  /* Hintergrundfarbe mit Transparenz */
                color: #333333;
            }
            QLabel {
                color: #000000;
            }
            QComboBox {
                background-color: #ffffff;
                border: 1px solid #555555;
                border-radius: 5px;
                padding: 2px;
                color: #333333;
                min-width: 100px;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                border: 1px solid #555555;
                subcontrol-position: top right;
                width: 20px;
                border-left-width: 1px;
                border-left-color: #555555;
                border-left-style: solid;
                border-top-right-radius: 5px;
                border-bottom-right-radius: 5px;
            }
            QComboBox::down-arrow {
                width: 10px;
                height: 10px;
            }
            QComboBox QAbstractItemView {
                background-color: #ffffff;
                border: 1px solid #555555;
                border-radius: 5px;
                padding: 5px;
                color: #333333;
                min-width: 100px;
            }
            QPushButton {
                background-color: #333333;
                color: #ffffff;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #444444;
            }
            QSlider::groove:horizontal {
                background: #999999;
                height: 6px;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #333333;
                border: 1px solid #555555;
                width: 14px;
                margin: -5px 0;
                border-radius: 7px;
            }
        """)

        # Helligkeitseinstellung
        self.brightness_slider = QSlider(Qt.Horizontal)
        self.brightness_slider.setRange(0, 100)
        self.brightness_slider.setValue(50)
        self.brightness_slider.setTickInterval(10)
        self.brightness_slider.setTickPosition(QSlider.TicksBelow)
        general_layout.addRow(QLabel("Helligkeit:"), self.brightness_slider)

        # Lautstärkeeinstellung
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.setTickInterval(10)
        self.volume_slider.setTickPosition(QSlider.TicksBelow)
        general_layout.addRow(QLabel("Lautstärke:"), self.volume_slider)

        # Kontraststeuerung
        self.contrast_slider = QSlider(Qt.Horizontal)
        self.contrast_slider.setRange(0, 100)
        self.contrast_slider.setValue(50)
        self.contrast_slider.setTickInterval(10)
        self.contrast_slider.setTickPosition(QSlider.TicksBelow)
        general_layout.addRow(QLabel("Kontrast:"), self.contrast_slider)

        # Farbsättigung
        self.saturation_slider = QSlider(Qt.Horizontal)
        self.saturation_slider.setRange(0, 100)
        self.saturation_slider.setValue(50)
        self.saturation_slider.setTickInterval(10)
        self.saturation_slider.setTickPosition(QSlider.TicksBelow)
        general_layout.addRow(QLabel("Farbsättigung:"), self.saturation_slider)

        # Mikrofonlautstärke
        self.mic_volume_slider = QSlider(Qt.Horizontal)
        self.mic_volume_slider.setRange(0, 100)
        self.mic_volume_slider.setValue(50)
        self.mic_volume_slider.setTickInterval(10)
        self.mic_volume_slider.setTickPosition(QSlider.TicksBelow)
        general_layout.addRow(QLabel("Mikrofon Lautstärke:"), self.mic_volume_slider)

        # Sprachauswahl für TTS
        self.language_dropdown = QComboBox()
        self.language_dropdown.addItems(["Deutsch", "Englisch", "Spanisch", "Französisch"])
        general_layout.addRow(QLabel("Sprache:"), self.language_dropdown)

        # Theme-Auswahl
        self.theme_dropdown = QComboBox()
        self.theme_dropdown.addItems(["Hell", "Dunkel", "Blau", "Grün"])
        general_layout.addRow(QLabel("Theme:"), self.theme_dropdown)

        # Schriftgröße
        self.font_size_slider = QSlider(Qt.Horizontal)
        self.font_size_slider.setRange(8, 32)
        self.font_size_slider.setValue(12)
        self.font_size_slider.setTickInterval(2)
        self.font_size_slider.setTickPosition(QSlider.TicksBelow)
        general_layout.addRow(QLabel("Schriftgröße:"), self.font_size_slider)

        # Audioeingabegerät
        self.audio_device_dropdown = QComboBox()
        devices = sd.query_devices()
        for device in devices:
            if device['max_input_channels'] > 0:
                self.audio_device_dropdown.addItem(device['name'])
        general_layout.addRow(QLabel("Audioeingabegerät:"), self.audio_device_dropdown)

        general_group.setLayout(general_layout)
        main_layout.addWidget(general_group)

        # Buttons
        buttons_layout = QHBoxLayout()  # Ändere hier von QVBoxLayout zu QHBoxLayout
        apply_button = QPushButton(" Anwenden")
        apply_button.setIcon(QIcon('C:\\Users\\julia\\PycharmProjects\\Xcpp\\agree.svg'))
        apply_button.setFixedSize(85, 35)
        apply_button.clicked.connect(self.apply_settings)
        cancel_button = QPushButton(" Abbrechen")
        cancel_button.setIcon(QIcon('C:\\Users\\julia\\PycharmProjects\\Xcpp\\disagree.svg'))
        cancel_button.setFixedSize(85, 35)
        cancel_button.clicked.connect(self.reject)
        # Füge die Buttons dem Layout hinzu
        buttons_layout.addWidget(apply_button)
        buttons_layout.addWidget(cancel_button)

        # Zentriere das Layout innerhalb des Hauptlayouts
        buttons_layout.setAlignment(Qt.AlignHCenter)

        main_layout.addLayout(buttons_layout)
        self.setLayout(main_layout)

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
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(
            AudioUtilities.IID_IAudioEndpointVolume, None, None)
        volume_control = interface.QueryInterface(ISimpleAudioVolume)
        volume_control.SetMasterVolume(float(volume) / 100.0, None)

    def set_camera_contrast(self, contrast):
        # Logik zum Einstellen des Kontrasts der Kamera
        pass

    def set_camera_saturation(self, saturation):
        # Logik zum Einstellen der Farbsättigung der Kamera
        pass

    def set_microphone_volume(self, mic_volume):
        devices = AudioUtilities.GetMicrophone()
        interface = devices.Activate(
            AudioUtilities.IID_IAudioEndpointVolume, None, None)
        volume_control = interface.QueryInterface(ISimpleAudioVolume)
        volume_control.SetMasterVolume(float(mic_volume) / 100.0, None)

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
        devices = sd.query_devices()
        for device in devices:
            if device['name'] == audio_device:
                sd.default.device = device['index']
                break


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.camera_thread = CameraThread()
        self.camera_thread.frame_signal.connect(self.update_camera_view)
        self.camera_thread.start()

    def initUI(self):
        self.setWindowTitle("Xc++")
        self.setWindowFlags(Qt.FramelessWindowHint)  # Fensterrahmen entfernen
        self.setGeometry(310, 28, 1300, 975)
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
        self.glass_frame.setFixedSize(1300, 975)

        # UI container frame
        self.glass_frame2 = QFrame(self)
        self.glass_frame2.setStyleSheet("""
            background-color: rgba(255, 255, 255, 150);
            border-radius: 20px;
            color: #000000;
        """)
        self.glass_frame2.setFixedSize(500, 160)

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
        self.label = QLabel("Press the button and speak", self.glass_frame)
        self.label.setAlignment(Qt.AlignBottom | Qt.AlignHCenter)
        self.label.setStyleSheet("color: #000000;")
        self.label.setFont(QFont('Arial', 14, QFont.Bold))
        self.glass_frame_layout.addWidget(self.label)

        self.button_layout = QHBoxLayout()

        # Create buttons // Button 1
        self.button1 = QPushButton(self.glass_frame)
        self.button1.setIcon(QIcon('C:\\Users\\julia\\PycharmProjects\\Xcpp\\run.svg'))
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
        self.button3.setIcon(QIcon('C:\\Users\\julia\\PycharmProjects\\Xcpp\\peharge-p-logo.svg'))
        self.shadow_effect3 = QGraphicsDropShadowEffect(self)
        self.shadow_effect3.setBlurRadius(10)
        self.shadow_effect3.setColor(QColor(0, 0, 0, 160))  # Schwarze Farbe für den Schatten
        self.shadow_effect3.setOffset(7, 7)
        self.button3.setGraphicsEffect(self.shadow_effect3)

        # Setze die Größe und das Layout des Buttons
        self.button3.setIconSize(QSize(57, 57))
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
        self.button4.setIcon(QIcon('C:\\Users\\julia\\PycharmProjects\\Xcpp\\settings.svg'))
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

        # Container-Layout für die Buttons erstellen
        self.button_container = QWidget(self.glass_frame)
        self.button_layout = QHBoxLayout(self.button_container)
        self.button_layout.setContentsMargins(0, 0, 0, 0)
        self.button_container.setLayout(self.button_layout)

        # Abstand von 50 Pixeln zwischen den Buttons hinzufügen
        self.button_layout.addWidget(self.button3)
        self.button_layout.addSpacing(5)
        self.button_layout.addWidget(self.button1)
        self.button_layout.addSpacing(20)
        self.button_layout.addWidget(self.button2)
        self.button_layout.addSpacing(5)
        self.button_layout.addWidget(self.button4)



        self.glass_frame_layout.addWidget(self.button_container, alignment=Qt.AlignCenter)

        self.result_label = QLabel("", self.glass_frame)
        self.result_label.setStyleSheet("color: #ffffff;")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.glass_frame_layout.addWidget(self.result_label)

        # Ensure the glass frame is always on top of the camera view
        self.glass_frame.raise_()

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

    def open_settings(self):
        self.settings_window = SettingsWindow(self)
        self.settings_window.exec_()

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

            self.label.setText("Processing with Xc++...")
            image_path = self.capture_image()

            if not image_path:
                self.label.setText("Error taking picture.")
                return

            llama3_output = run_command_and_get_output("ollama run llava:13b", text + f" : {image_path} ")
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

            ret, frame = cap.read()
            if not ret:
                raise Exception("Could not read frame")

            cap.release()

            current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            image_path = f"C:/Users/julia/PycharmProjects/Xcpp/image_{current_time}.png"
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


def run_command_and_get_output(command, text_input):
    try:
        result = subprocess.run(command, input=text_input, shell=True, check=True, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, text=True, encoding='utf-8')
        return result.stdout
    except subprocess.CalledProcessError as e:
        logging.error(f"Error executing command '{command}': {e}")
        return "Fehler beim Ausführen des Befehls: " + str(e)


if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        model = whisper.load_model("base")
        window = MainWindow()
        window.show()
        sys.exit(app.exec_())

    except Exception as e:
        logging.error(f"Error in main execution: {e}")
        print(f"Error in main execution: {e}")