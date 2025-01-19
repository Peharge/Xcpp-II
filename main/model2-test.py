import os
import datetime
import logging
import pygame
import soundfile as sf
from TTS.api import TTS
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts

# Definiere die Eingabevariablen
input_text = "Ich bin hier, um alle deine Fragen zu Weuzeck zu beantworten. Ob du was zum Drama, den Charakteren oder einzelnen Szenen wissen willst. Ich hab die Antworten, oder zumindest eine ziemlich gute Ausrede."
language = "de"  # oder "en" für Englisch, je nach Modell

class YourClassName:
    def process_with_professional_tool(self, text_output, language="de"):
        try:
            # TTS-Modell und Sample-WAV-Pfad basierend auf der Sprache konfigurieren
            if language == "en":
                tts_model_name = "tts_models/en/ljspeech/vits"  # Ein gültiges Modell für Englisch
                speaker_wav_path = os.path.join("C:/Users/julia/PycharmProjects/Xcpp/xtts-v2/sample/de_sample.wav")
            elif language == "de":
                tts_model_name = "tts_models/de/thorsten/tacotron2-DCA"
                speaker_wav_path = os.path.join("C:/Users/julia/PycharmProjects/Xcpp/xtts-v2/sample/de_sample.wav")
            else:
                raise ValueError("Unsupported language")

            #"C:/Users/julia/PycharmProjects/Xcpp/xtts-v2"

            # TTS-Modell initialisieren und Text in eine WAV-Datei konvertieren
            tts = TTS(model_name=tts_model_name, progress_bar=False, gpu=False)
            current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            tts_output_filename = f"tts_output_{current_time}.wav"
            tts.tts_to_file(text=text_output, file_path=tts_output_filename)

            # XTTS-Konfiguration und Modell laden
            config = XttsConfig()
            config.load_json(os.path.join("C:/Users/julia/PycharmProjects/Xcpp/xtts-v2", "config.json"))
            xtts_model = Xtts(config)
            xtts_model.load_checkpoint(config, checkpoint_dir="C:/Users/julia/PycharmProjects/Xcpp/xtts-v2", eval=True)

            # Überprüfen, ob die Beispiel-WAV-Datei existiert
            if not os.path.exists(speaker_wav_path):
                raise FileNotFoundError(f"Die Datei {speaker_wav_path} existiert nicht. Bitte überprüfen Sie den Pfad und versuchen Sie es erneut.")

            # XTTS-Synthese durchführen
            outputs = xtts_model.synthesize(
                text_output,                # Der Text wird hier übergeben
                config,
                speaker_wav=speaker_wav_path,
                gpt_cond_len=3,
                language=language,          # Die Sprache wird hier übergeben
            )

            xtts_output_file = f"C:/Users/julia/PycharmProjects/Xcpp/output_{current_time}_xtts.wav"
            if "wav" in outputs.keys():
                sample_rate = config.audio['sample_rate']
                with sf.SoundFile(xtts_output_file, "w", samplerate=sample_rate, channels=1) as file:
                    file.write(outputs["wav"])
                logging.info(f"Die Audiodatei wurde erfolgreich gespeichert unter: {xtts_output_file}")

                # Audiodatei abspielen
                pygame.mixer.init()
                pygame.mixer.music.load(xtts_output_file)
                pygame.mixer.music.play()

                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)

            else:
                raise KeyError("Output dictionary does not contain 'wav'")

            # Temporäre Dateien löschen
            if os.path.exists(tts_output_filename):
                os.remove(tts_output_filename)

            if os.path.exists(xtts_output_file):
                os.remove(xtts_output_file)

        except FileNotFoundError as e:
            logging.error(f"FileNotFoundError: {e}")
        except KeyError as e:
            logging.error(f"KeyError: {e}")
        except ValueError as e:
            logging.error(f"ValueError: {e}")
        except Exception as e:
            logging.error(f"Error in process_with_professional_tool: {e}")

# Instanziiere die Klasse und rufe die Methode auf
if __name__ == "__main__":
    my_instance = YourClassName()  # Ersetze YourClassName durch den tatsächlichen Klassennamen
    my_instance.process_with_professional_tool(text_output=input_text, language=language)
