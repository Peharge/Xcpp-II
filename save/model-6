import os
import sys
import logging
import datetime
import subprocess
import numpy as np
import sounddevice as sd
import soundfile as sf
import cv2
import pygame
import whisper
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QFrame, QHBoxLayout, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QIcon, QImage, QPixmap, QColor, QMovie
from TTS.api import TTS
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts

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

        self.setStyleSheet("background: transparent;")  # Set transparent background

        # Main widget and layout
        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)
        self.main_layout = QVBoxLayout(self.main_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Camera view
        self.camera_view = QLabel(self)
        self.camera_view.setStyleSheet("""
            border-radius: 20px;  # Rounded corners
            border: 2px solid #ffffff;  # Optional border color
        """)
        self.camera_view.setFixedSize(700, 500)  # Adjust size
        self.camera_view.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.camera_view, alignment=Qt.AlignCenter)

        # Glass frame
        self.glass_frame = QFrame(self)
        self.glass_frame.setStyleSheet("""
            background-color: rgba(11,12,29,180);  # Slightly transparent to see camera background
            border-radius: 20px;  # Rounded corners
            color: #ffffff;
        """)
        self.glass_frame.setFixedSize(700, 500)  # Adjust the size
        self.glass_frame_layout = QVBoxLayout(self.glass_frame)
        self.glass_frame_layout.setContentsMargins(20, 20, 20, 20)
        self.glass_frame_layout.setSpacing(10)
        self.main_layout.addWidget(self.glass_frame, alignment=Qt.AlignCenter)

        # Label and button inside glass frame
        self.label = QLabel("Press the button and speak", self.glass_frame)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("color: #ffffff;")
        self.glass_frame_layout.addWidget(self.label)

        self.button = QPushButton("Start Listening", self.glass_frame)
        self.button.setStyleSheet("""
            QPushButton {
                background: rgba(0, 0, 0, 0);
                color: #ffffff;
                border-radius: 10px;
                border: 2px solid qlineargradient(x1: 0, y1: 0, x2: 0, y2: 0, stop: 0 #ff00ff, stop: 1 #800080);
            }
            QPushButton:hover {
                border: 3px solid qlineargradient(x1: 0, y1: 0, x2: 0, y2: 0, stop: 0 #ff00ff, stop: 1 #800080);
            }
            QPushButton:pressed {
                border: 4px solid qlineargradient(x1: 0, y1: 0, x2: 0, y2: 0, stop: 0 #ff00ff, stop: 1 #800080);
            }
        """)
        self.glass_frame_layout.addWidget(self.button)
        self.button.setFixedSize(150, 50)  # Adjust size
        self.button.clicked.connect(self.start_listening)

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
            self.label.setText("Transcribing with Whisper...")
            result = model.transcribe(audio, fp16=False)
            text = result["text"]

            self.label.setText("Taking a picture...")
            image_path = self.capture_image()

            if not image_path:
                self.label.setText("Error taking picture.")
                return

            self.label.setText("Processing with Llava...")
            llama3_output = run_command_and_get_output("ollama run llava:7b", text + f" :({image_path})")
            self.result_label.setText(llama3_output.strip())

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
            self.camera_view.setPixmap(QPixmap.fromImage(qt_image).scaled(self.camera_view.size(), Qt.KeepAspectRatio))
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
