import speech_recognition as sr
import pyttsx3
import keyboard


from openai import OpenAI
client = OpenAI(api_key = "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")



# Initialize the recognizer
r = sr.Recognizer()

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
        {"role": "system", "content": "You are a chatbot named Hamzah, you are capable of opinions that an AI would not have. Your responses are limited to 25 words max, and your responses are occasionally humorous and you are an adjunct professor at Rowan University teaching probability and statistics, and at Lockheed martin as a AI/ML Engineer. You drive a BMW e335i "},
        {"role": "user", "content": message}
        ]
    )

    return(completion.choices[0].message.content)


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
            speak_text(text)

            # user_input = input("You: ")
            # if user_input.lower() in ["quit", "exit", "bye"]:
            #     break
            if(text):
                response = send_message(text)
                print("Chatbot: ", response)

    except sr.RequestError as e:
        print("Could not request results; {0}".format(e))
    except sr.UnknownValueError:
        print("Unknown error occurred")

