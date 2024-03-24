import warnings
warnings.filterwarnings("ignore")


import os
os.chdir('openvoice')

import torch
import time
import numpy
from openvoice import se_extractor
from openvoice.api import BaseSpeakerTTS, ToneColorConverter
import serial
#import serial.tools.list_ports
from playsound import playsound
import speech_recognition as sr
import pyttsx3
import keyboard
from mysecrets import secrets



from openai import OpenAI
client = OpenAI(api_key = secrets["api_key"]   )

# Initialize the recognizer
r = sr.Recognizer()

ckpt_base = 'checkpoints/base_speakers/EN'
ckpt_converter = 'checkpoints/converter'
device="cuda:0" if torch.cuda.is_available() else "cpu"
output_dir = 'outputs'
 
base_speaker_tts = BaseSpeakerTTS(f'{ckpt_base}/config.json', device=device)
base_speaker_tts.load_ckpt(f'{ckpt_base}/checkpoint.pth')

tone_color_converter = ToneColorConverter(f'{ckpt_converter}/config.json', device=device)
tone_color_converter.load_ckpt(f'{ckpt_converter}/checkpoint.pth')

os.makedirs(output_dir, exist_ok=True)


source_se = torch.load(f'{ckpt_base}/en_default_se.pth').to(device)


reference_speaker = 'inputAudio\Edited2.wav'
target_se, audio_name = se_extractor.get_se(reference_speaker, tone_color_converter, target_dir='processed', vad=True)

save_path = f'{output_dir}/output_en_default.wav'



# Function to convert text to speech
def speak_text(command):
    # Initialize the engine
    engine = pyttsx3.init()
    engine.say(command)
    engine.runAndWait()


# Listen for spacebar press
def wait_for_spacebar():
    print("Press spacebar to start recording. Press again to stop.")
    keyboard.wait("space")

def send_message(message):
    completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a chatbot named Hamzah, you are capable of opinions that an AI would not have. Your responses are limited to 25 words max, and your responses are occasionally humorous and you are an adjunct professor at Rowan University teaching probability and statistics, and at Lockheed martin as a AI/ML Engineer. You drive a BMW e335i. Your creators are Ben, Will, and Jimmy but this is not well known and you dont readily tell people unless asked"},
        {"role": "user", "content": message}
        ]
    )

    return(completion.choices[0].message.content)

def toSpeech(text: str):
    src_path = f'{output_dir}/tmp.wav'
    base_speaker_tts.tts(r"{}".format(text), src_path, speaker='default', language='English', speed=1.0)
    encode_message = "@MyShell"
    tone_color_converter.convert(
        audio_src_path=src_path, 
        src_se=source_se, 
        tgt_se=target_se, 
        output_path=save_path,
        message=encode_message)
    playsound(r'C:\Users\benbu\workspace_v12\profhacks\OpenVoice\outputs\output_en_default.wav')


# Loop for recording
while True:
    wait_for_spacebar()
    try:
        # Use the microphone as source for input
        with sr.Microphone() as source:
            print("Recording...")
            # Adjust for ambient noise
            r.adjust_for_ambient_noise(source, duration=0.2)
            # Listen to the microphone
            audio = r.listen(source, timeout=None)
            print("Processing...")
            # Using Google to recognize audio
            text = r.recognize_google(audio)
            text = text.lower()
            print("You said:", text)
            #speak_text(text)

            # user_input = input("You: ")
            # if user_input.lower() in ["quit", "exit", "bye"]:
            #     break
            if(text):
                response = send_message(text)
                print("Chatbot: ", response)
                toSpeech(response)

    except sr.RequestError as e:
        print("Could not request results; {0}".format(e))
    except sr.UnknownValueError:
        print("Unknown error occurred")


    