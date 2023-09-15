import pyttsx3
import speech_recognition as sr
import firebase_admin
import sys
from subprocess import call
from firebase_admin import credentials, db
from datetime import datetime
from subprocess import call

# Initialize Firebase
cred = credentials.Certificate("C://Users//Mohak//Desktop//Big_Project//cred.json")

firebase_admin.initialize_app(cred, {
    'databaseURL': "https://link-bd2ea-default-rtdb.firebaseio.com/"
})

root = db.reference()
ref_data = db.reference('User-Data')
keys_data = ref_data.get()

listener = sr.Recognizer()
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

dynamic_email = None

def talk(text):
    engine.say(text)
    engine.runAndWait()

def open_py_file():
    talk("Here is the list of Features you can perform")
    print("The list of Features you can perform")
    talk("First is Add the data of Youtube Video")
    talk("Second is Analysis of Youtube Video")
    talk("Enter your choice")
    choice = int(input("1.Add the data of Youtube Video \n2.Analysis of Youtube Video \nEnter your choice : "))
    if choice == 1:
        script_path = "C://Users//Mohak//Desktop//Big_Project//adddata.py"
        print(f"Calling script at: {script_path}")
        call(["python", script_path])
    elif choice == 2:
        script_path = "C://Users//Mohak//Desktop//Big_Project//youtubecomment.py"
        call(["python", script_path])
    else:
        talk("Invalid Choice")
        print("Invalid Choice")

# Retrieve the dynamic email from command-line arguments
if len(sys.argv) > 1:
    dynamic_email = sys.argv[1]
    # print("Dynamic Email received:", dynamic_email)
else:
    print("Dynamic Email not provided.")

talk("Want to Explore Dark World of Analysis?")
choice = input("Want to Explore Dark World of Analysis , Press 'Y' to run code or Press 'N' for exit : ")
while True:
    if choice.upper() == 'Y':
        dynamic_email = str(dynamic_email)
        print(type(dynamic_email))
        user_data = ref_data.child(dynamic_email).get()
        talk("Enter the last time OTP sent to your email.")
        otp = input("Enter the Last time OTP sent to your email: ")
        if otp == user_data['otp']:
            open_py_file()
            talk("Want to Explore Dark World of Analysis Again?")
            choice = input("Want to Explore Dark World of Analysis Again , Press 'Y' to run code or Press 'N' for exit : ")
    elif choice.upper() == 'N':
        break
    else:
        talk("Invalid Choice.")
        print("Invalid Choice")
        talk("Want to Explore Dark World of Analysis Again?")
        choice = input("Want to Explore Dark World of Analysis Again , Press 'Y' to run code or Press 'N' for exit : ")
