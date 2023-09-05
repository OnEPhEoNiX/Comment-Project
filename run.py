from subprocess import call

def open_py_file():
    print("\nWhat you want to do")
    choice = int(input("\n1.Add the data of Youtube Video \n2.Analysis of Youtube Video \nEnter your choice : "))
    if choice == 1:
        script_path = "C://Users//Mohak//Desktop//Big_Project//adddata.py"
        print(f"Calling script at: {script_path}")
        call(["python", script_path])
    elif choice == 2:
        script_path = "C://Users//Mohak//Desktop//Big_Project//youtubecomment.py"
        call(["python", script_path])
    else:
        print("Invalid Choice")

choice = input("\nWant to Run this code , Press 'Y' to run code or Press 'N' for exit : ")
while True:
    if choice.upper() == 'Y':
        open_py_file()
        choice = input("\nWant to Run this code , Press 'Y' to run code or Press 'N' for exit : ")
    elif choice.upper() == 'N':
        break
    else:
        print("Invalid Choice")
        choice = input("\nWant to Run this code , Press 'Y' to run code or Press 'N' for exit : ")
