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

# Setup logging
logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Set up PyDub for audio processing
from pydub import AudioSegment
from pydub.playback import play

ffmpeg_path = "C:\\Users\\julia\\anaconda3\\envs\\peharge_chatpp\\Library\\bin\\ffmpeg.exe"
AudioSegment.converter = ffmpeg_path

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

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.camera_thread = CameraThread()
        self.camera_thread.frame_signal.connect(self.update_camera_view)
        self.camera_thread.start()

    def initUI(self):
        self.setWindowTitle("Voice to Voice Application")
        self.setFixedSize(800, 600)

        icon_path = "C:\\Users\\julia\\OneDrive - Gewerbeschule Lörrach\\Pictures\\software\\peharge-logo3.6.ico"
        if not os.path.exists(icon_path):
            logging.error(f"Icon file not found at: {icon_path}")
        self.setWindowIcon(QIcon(icon_path))

        myappid = u'mycompany.myproduct.subproduct.version'  # Arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

        background_color = QColor(255, 255, 255)
        self.setStyleSheet("background-color: rgb({},{},{})".format(
            background_color.red(), background_color.green(),
            background_color.blue()))

        self.setWindowOpacity(0.9)

        glass_frame = QFrame(self)
        glass_frame.setGeometry(0, 0, 1920, 1000)
        glass_frame.setStyleSheet("""
            background-color: rgb(255, 255, 255);
            color: #ffffff;
        """)

        self.setStyleSheet("background: transparent;")  # Set transparent background

        # Main widget and layout
        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)
        self.main_layout = QVBoxLayout(self.main_widget)
        self.main_layout.setContentsMargins(0, 10, 0, 0)

        # Spacer to push the camera view down
        self.main_layout.addItem(QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Camera view with rounded corners
        self.camera_view = QLabel(self)
        self.camera_view.setFixedSize(700, 500)  # Adjust size
        self.camera_view.setAlignment(Qt.AlignCenter)
        self.camera_view.setStyleSheet("""
            background: white;  # Background color to make camera view more visible
        """)
        self.main_layout.addWidget(self.camera_view, alignment=Qt.AlignCenter)

        # Spacer to push the button down
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.main_layout.addItem(spacer)

        # Glass frame
        self.glass_frame = QFrame(self)
        self.glass_frame.setStyleSheet("""
            background-color: rgba(225,255,255,180);  # Slightly transparent to see camera background
            border-radius: 20px;  # Rounded corners
            color: #ffffff;
        """)
        self.glass_frame.setFixedSize(700, 500)  # Adjust the size
        self.glass_frame_layout = QVBoxLayout(self.glass_frame)
        self.glass_frame_layout.setContentsMargins(20, 20, 20, 20)
        self.glass_frame_layout.setSpacing(10)
        self.glass_frame.setLayout(self.glass_frame_layout)
        self.main_layout.addWidget(self.glass_frame, alignment=Qt.AlignCenter)

        # Assuming self.glass_frame and self.glass_frame_layout are already defined
        self.label = QLabel("Press the button and speak", self.glass_frame)
        self.label.setAlignment(Qt.AlignBottom | Qt.AlignHCenter)  # Align text to the bottom and center horizontally
        self.label.setStyleSheet("color: #ffffff;")
        self.label.setFont(QFont('Arial', 12, QFont.Bold))
        self.glass_frame_layout.addWidget(self.label)

        button_layout = QHBoxLayout()

        self.button = QPushButton("Runn", self.glass_frame)
        shadow_effect = QGraphicsDropShadowEffect(self)
        shadow_effect.setBlurRadius(10)
        shadow_effect.setColor(QColor(255, 0, 0, 160))  # Schwarze Farbe für den Schatten
        shadow_effect.setOffset(5, 5)
        self.button.setGraphicsEffect(shadow_effect)
        self.button.setFont(QFont('Arial', 20, QFont.Bold))
        self.button.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #000000;
                border-radius: 10px;
                border: 4px solid qlineargradient(x1: 0, y1: 0, x2: 0, y2: 0, stop: 0 rgba(255, 0, 0, 160), stop: 1 rgba(255, 0, 0, 160));
                padding: 10px 20px;
                font-size: 16px;
                font-weight: bold;
                transition: background-color 0.3s, border 0.3s, box-shadow 0.3s;
            }
            QPushButton:hover {
                background-color:rgba(255, 0, 0, 160);
                border: 4px solid qlineargradient(x1: 0, y1: 0, x2: 0, y2: 0, stop: 0 rgba(255, 0, 0, 160), stop: 1 rgba(255, 0, 0, 160));
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            }
            QPushButton:pressed {
                background-color:rgba(255, 0, 0, 160);
                border: 4px solid qlineargradient(x1: 0, y1: 0, x2: 0, y2: 0, stop: 0 rgba(255, 0, 0, 160), stop: 1 rgba(255, 0, 0, 160));
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
            }

        """)
        self.glass_frame_layout.addWidget(self.button, alignment=Qt.AlignCenter)
        self.button.setFixedSize(130, 50)  # Adjust size
        self.button.clicked.connect(self.start_listening)

        # Define a function to move the button up by 10px.
        def move_button_up():
            self.button.move(self.button.x(), self.button.y() - 5)

        # Define a function to move the button down by 10px.
        def move_button_down(button):
            if not button.isChecked():
                button.move(button.x(), button.y() + 5)

        # Connect the functions to the respective signals.
        self.button.pressed.connect(move_button_up)
        self.button.released.connect(lambda: move_button_down(self.button))

        # Connect enterEvent and leaveEvent with the functions.
        self.button.enterEvent = lambda event: move_button_up()
        self.button.leaveEvent = lambda event: move_button_down(self.button)

        self.setLayout(button_layout)

        # Result label
        self.result_label = QLabel("", self.glass_frame)
        self.result_label.setStyleSheet("color: #ffffff;")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.glass_frame_layout.addWidget(self.result_label)

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

            self.label.setText("Taking a picture...")
            image_path = self.capture_image()

            if not image_path:
                self.label.setText("Error taking picture.")
                return

            self.label.setText("Processing with Xc++...")
            llama3_output = run_command_and_get_output("ollama run llava:13b", text + f" :(C:/Users/julia/PycharmProjects/Xcpp/{image_path})")
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
            image_path = f"image_{current_time}.png"
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

            # Create a QPixmap with the rounded corners
            rounded_pixmap = QPixmap(qt_image.size())
            rounded_pixmap.fill(Qt.transparent)

            painter = QPainter(rounded_pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setBrush(Qt.black)
            painter.setPen(Qt.NoPen)

            # Draw a rounded rectangle
            painter.drawRoundedRect(rounded_pixmap.rect(), 20, 20)

            painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
            painter.drawImage(0, 0, qt_image)
            painter.end()

            self.camera_view.setPixmap(rounded_pixmap.scaled(self.camera_view.size(), Qt.KeepAspectRatio))

        except Exception as e:
            logging.error(f"Error in update_camera_view: {e}")

    def process_with_professional_tool(self, text_output, language="de"):
        try:
            if language == "de":
                model_name = "tts_models/de/thorsten/tacotron2-DCA"
            elif language == "en":
                model_name = "path/to/english/tts/model"

            tts = TTS(model_name=model_name, progress_bar=False, gpu=False)
            current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            output_filename = f"output_{current_time}.wav"
            tts.tts_to_file(text=text_output, file_path=output_filename)

            config = XttsConfig()
            config.load_json(os.path.join("C:/Users/julia/Downloads/xtts-v2", "config.json"))
            xtts_model = Xtts(config)
            xtts_model.load_checkpoint(config, checkpoint_dir="C:/Users/julia/Downloads/xtts-v2", eval=True)

            speaker_wav_path = os.path.join("C:\\Users\\julia\\Downloads\\xtts-v2\\sample\\de_sample.wav")

            if not os.path.exists(speaker_wav_path):
                raise FileNotFoundError(f"Die Datei {speaker_wav_path} existiert nicht. Bitte überprüfen Sie den Pfad und versuchen Sie es erneut.")

            outputs = xtts_model.synthesize(
                text_output,
                config,
                speaker_wav=speaker_wav_path,
                gpt_cond_len=3,
                language="de",
            )

            output_file = f"output_{current_time}_xtts.wav"
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
