import os
from dotenv import load_dotenv
import azure.cognitiveservices.speech as speechsdk
from pkg.shared.core.stage_logger import stage_log

# Load environment variables
load_dotenv()

speech_key = os.getenv("SPEECH_KEY")
speech_region = os.getenv("SPEECH_REGION")

if not speech_key or not speech_region:
    raise ValueError("Environment variables SPEECH_KEY and SPEECH_REGION are not set correctly.")

# Azure Speech SDK Configurations
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
speech_config.speech_recognition_language = "en-US"
speech_config.speech_synthesis_voice_name = 'en-US-AvaMultilingualNeural'
audio_output = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_output)

@stage_log(stage=2)
def text_to_speech(text):
    speech_synthesis_result = speech_synthesizer.speak_text_async(text).get()
    if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print(f"Speech synthesized for text: {text}")
    elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_synthesis_result.cancellation_details
        print(f"Speech synthesis canceled: {cancellation_details.reason}")

@stage_log(stage=2)
def speech_to_text():
    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
    print("Speak into your microphone...")
    speech_recognition_result = speech_recognizer.recognize_once_async().get()
    if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
        return speech_recognition_result.text
    elif speech_recognition_result.reason in [speechsdk.ResultReason.NoMatch, speechsdk.ResultReason.Canceled]:
        return None