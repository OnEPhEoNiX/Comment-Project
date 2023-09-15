import random
import smtplib
import getpass
import firebase_admin
import pyttsx3
import speech_recognition as sr
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

def talk(text):
    engine.say(text)
    engine.runAndWait()
    

def open_py_file(email):
    script_path = "C://Users//Mohak//Desktop//Big_Project//run.py"
    print(f"Calling script at: {script_path} with email: {email}")
    call(["python", script_path, email])

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_email(email, otp):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587  
    sender_email = "darkworldanalysis@gmail.com"  
    sender_password = "ipvv pbnq pqqs hhdl"  

    subject = "Dark World Of Analysis OTP Verification"
    message = f"Hello {email},\nThank you for using our service. To complete your login or registration, we've sent you a one-time password (OTP). Please enter this OTP in the provided field on our website or app.OTP: {otp}.\nPlease note that this OTP is valid for a limited time and should not be shared with anyone. If you didn't request this OTP, please ignore this email.\nIf you have any questions or need assistance, please feel free to contact our support team at {sender_email}.\nThank you for choosing Dark World Analysis."

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, email, f"Subject: {subject}\n\n{message}")
        server.quit()
        return True
    except Exception as e:
        print(f"Error sending OTP: {str(e)}")
        return False
    
def create_account(email, password):
    if keys_data and email in keys_data:
        talk("Email already exists. Please log in.")
        print("Email already exists. Please log in.")
        return
    
    otp = generate_otp()

    if send_otp_email(email, otp):
        while True:
            talk("Enter the OTP sent to your email.")
            user_otp = input("Enter the OTP sent to your email: ")
            if user_otp == otp:
                user_data = {
                    'email': email,
                    'password': password,
                    'otp': otp,
                    'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                ref_data.child(email.replace(".", "_")).set(user_data)
                talk("Account created successfully.")
                print("Account created successfully.")
                break
            else:
                talk("OTP verification failed. Please try again.")
                print("OTP verification failed. Please try again.")
    else:
        talk("Failed to create an account. Please try again.")
        print("Failed to create an account. Please try again.")

def login():
    talk("Welcome to the Dark World Of Analysis.")
    print("Welcome to the Dark World Of Analysis")
    talk("First is Login to the World of Dark Analysis.")
    print("1. Login to the World of Dark Analysis")
    talk("Second is Create Account to be a part of Dark World.")
    print("2. Create Account to be a part of Dark World")
    talk("Third is Logout from the Dark World.")
    print("3. Logout from the Dark World")
    talk("Enter your choice.")
    choice = input("Enter your choice (1, 2, or 3): ")

    if choice == '1':
        talk("Enter your Dark World email account.")
        email = input("Enter your Dark World email account: ")
        email_key = email.replace(".", "_")
        user_data = ref_data.child(email_key).get()
        
        if user_data:
            talk("Enter your Dark World account password.")
            password = getpass.getpass("Enter your Dark World account password: ")
            if password == user_data['password']:
                otp = generate_otp()
                ref_data.child(email.replace(".", "_")).update({'otp': otp})
                if send_otp_email(email, otp):
                    while True:
                        talk("First is Logout")
                        print("1. Logout")
                        talk("Second is to Explore The Dark World Of Analysis")
                        print("2. Explore The Dark World Of Analysis")
                        talk("Enter your choice.")
                        user_choice = input("Enter your choice (1 or 2): ")
                        user_data = ref_data.child(email_key).get()
                        if user_choice == '1':
                            talk("Logout successful! You have left the Dark World.")
                            print("Logout successful! You have left the Dark World.")
                            break
                        elif user_choice == '2':
                            talk("Enter the OTP sent to your email.")
                            user_otp = input("Enter the OTP sent to your email: ")
                            if user_otp == user_data['otp']:
                                talk("OTP verified. Login successful!")
                                print("OTP verified. Login successful!")
                                talk("Welcome to the Dark World.")
                                print("Welcome to the Dark World.")
                                open_py_file(email_key) 
                            else:
                                talk("OTP verification failed. Please try again.")
                                print("OTP verification failed. Please try again.")
                        else:
                            talk("Invalid choice.")
                            print("Invalid choice. Please select 1 or 2.")
            else:
                talk("Password incorrect. Login failed.")
                print("Password incorrect. Login failed.")
        else:
            talk("Email not found. Please create a Dark World account.")
            print("Email not found. Please create a Dark World account.")
            talk("Do you want to create account in Dark World of Analysis?")
            acc_create = input("Do you want to create account in Dark World of Analysis , Yes/No : ")
            if acc_create.upper() == 'YES' or acc_create.upper() == 'Y':
                create_account(email, password)
            else:
                talk("Thank you for visiting Dark World of Analysis.")
                print("Thank you for visiting Dark World of Analysis.")
    elif choice == '2':
        talk("Enter your email for entering the Dark World of Analysis.")
        email = input("Enter your email for entering the Dark World of Analysis: ")
        talk("Create a password for your Dark World account.")
        password = getpass.getpass("Create a password for your Dark World account: ")
        create_account(email, password)
    elif choice == '3':
        talk("Logout successful! You have left the Dark World.")
        print("Logout successful! You have left the Dark World.")
    else:
        talk("Invalid choice.")
        print("Invalid choice. Please select 1, 2, or 3.")

if __name__ == "__main__":
    login()