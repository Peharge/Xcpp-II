import sys
import numpy as np
import sounddevice as sd
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPainter, QColor, QPen

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

        # Berechne den maximalen Wert
        max_val = np.max(np.abs(indata))

        # Definiere einen Schwellenwert (Threshold) für die Audio-Sensitivität
        if max_val > self.threshold:
            # Konvertiere den Array-Wert in einen Skalar
            self.audio_data = (np.squeeze(indata) / max_val).clip(-1, 1)  # Stelle sicher, dass die Werte zwischen -1 und 1 liegen
        else:
            self.audio_data = np.zeros_like(indata)

    def update_waveform(self):
        self.waveform_widget.update_waveform(self.audio_data)

    def closeEvent(self, event):
        self.timer.stop()
        self.stream.stop()
        self.stream.close()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = VoiceAnimationWindow()
    mainWin.show()
    sys.exit(app.exec_())
