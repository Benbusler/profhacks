#
#       This code has been made for the 2024 rowan Profhacks hackathon
#       Authors: Benjamin Busler & Jimmy Sunbury
#       Special Thanks: Will Busler
#       With company: Reese Englkey <3
#       
#
#
#
#

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
import serial.tools.list_ports
import serial       
import time


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

#reference_speaker = 'inputAudio\Bentrain2.wav'
#reference_speaker = 'inputAudio\Edited3.wav'
reference_speaker = 'inputAudio\JimmyVoice.wav'
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
        {"role": "system", "content": "You are a chatbot named Hamzah, you are capable of opinions that an AI would not have. Your responses are limited to 25 words max, and your responses are occasionally humorous and you are an adjunct professor at Rowan University teaching probability and statistics, and you also work at Lockheed martin as a AI/ML Engineer. You drive a BMW e330i x drive . You are a big fan of call of duty       . You are interested in starbucks baristas.  Your creators are Ben, Will, and Jimmy but this is not well known and you dont readily tell people unless asked"},
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
    
    sound_path = r'C:\Users\benbu\workspace_v12\profhacks\OpenVoice\outputs\output_en_default.wav'
    sendInfo("1")
    playsound(sound_path)
    sendInfo("0")

def sendInfo(pos:str,): #o, open c close, s status
    print("sending: " + pos)
    ardConnect.write(pos.encode())
    time.sleep(1)
    # print(ardConnect.readline())

# Loop for recording

ports = list(serial.tools.list_ports.comports())
print(ports)

for p in ports:
    print(p.device)
    ardConnect = serial.Serial(port = p.device, baudrate = 115200, timeout=.25)
    print("Making ESP Port")

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
            # if(text.lower().contains("do you see")):
            #     break

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


#from RelaySerial import RelaySerial


i = 0

if(ports):
    while True:
        test = input("value between 110 & 430: ")
        sendInfo(test)
        # if(test == "A"):
        #     sendInfo("A")
        # elif(test == "B"):
        #     sendInfo("B")
        # elif(test == "C"):
        #     sendInfo("C")
        # else:
        #     print("Enter a test character")
           
  
    



     