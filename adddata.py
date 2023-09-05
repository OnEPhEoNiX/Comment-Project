import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from datetime import datetime
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
from pytube import YouTube

cred = credentials.Certificate("C://Users//Mohak//Desktop//Big_Project//cred.json")


firebase_admin.initialize_app(cred, {
    'databaseURL' : "https://link-bd2ea-default-rtdb.firebaseio.com/"
})


ref = db.reference('Youtube-Videos')
root = db.reference()
ref_data = db.reference('Youtube-Videos-data')
data_ref_data = root.child('Youtube-Videos-data')
keys_data = data_ref_data.get(shallow=True)


def Youtube_Video_data(key , url ,url_2):
    option = webdriver.ChromeOptions()
    option.add_argument("--headless")
    driver = webdriver.Chrome(options = option)
    driver.get(url_2)
    time.sleep(5)
    prev_h = 0
    while True:
        height = driver.execute_script("""
                    function getActualHeight() {
                    return Math.max(
                        Math.max(document.body.scrollHeight, document.documentElement.scrollHeight),
                        Math.max(document.body.offsetHeight, document.documentElement.offsetHeight),
                        Math.max(document.body.clientHeight, document.documentElement.clientHeight)
                    );
                }
                return getActualHeight();                   
                """)
        driver.execute_script(f"window.scrollTo({prev_h},{prev_h + 200})")
        time.sleep(2)
        prev_h += 200
        if prev_h >= height:
            break
    soup = BeautifulSoup(driver.page_source , 'html.parser')




    driver.quit()
    title_text = soup.select_one('#container h1')
    title = title_text and title_text.text

    subscribers_element = soup.find('yt-formatted-string', {'id': 'owner-sub-count'})
    subscribers = subscribers_element.get_text(strip=True) if subscribers_element else 'Subscribers not found'

    try:
        yt = YouTube(url)
        title = yt.title
        upload_date = yt.publish_date
        upload_date = upload_date.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        print(f"Error: {e}")
        return None

    views_element = soup.find('span', {'class': 'view-count'})
    views = views_element.get_text(strip=True) if views_element else 'Views not found'
    current_time = datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
    data = {
        key : {
            'title' : title,
            'subscribers' : subscribers,
            'upload-date' : upload_date,
            'views' : views,
            'url' : url,
            'add-time' : formatted_time
            }
        }
    for key, value in data.items():
        ref_data.child(key).set(value)
        print("Data Added Successfully")


choice = int(input("Press 1 for adding new data \nPress 2 for deleting the specific data \nPress 3 for updating the data \nPress 0 for exit \nEnter your choice = "))

while True:
    if choice == 0:
        break
    elif choice == 1:
        url = input("Enter Youtube Video URL = ")
        comma_index = url.find('=')
        key = url[comma_index + 1:]
        current_time = datetime.now()
        formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
        data = {
            key : {
                'url' : url,
                'add-time' : formatted_time
            }
        }
        for key, value in data.items():
            ref.child(key).set(value)
            print("Data Added Successfully")
    elif choice == 2:
        key = input("Enter Youtube Video ID = ")
        ref.child(key).delete()
        print("Data Deleted Successfully")
    elif choice == 3:
        key = input("Enter Youtube Video ID = ")
        url = input("Enter Youtube Video URL = ")
        current_time = datetime.now()
        formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
        data = {
            key : {
                'url' : url,
                'add-time' : formatted_time
            }
        }
        for key, value in data.items():
            ref.child(key).update(value)
        print("Data Updated Successfully")
    else:
        print("Invalid Input")
    choice = int(input("Press 1 for adding new data \nPress 2 for deleting the specific data \nPress 3 for updating the data \nPress 0 for exit \nEnter your choice = "))

add_choice = input("\nDo you want to add Youtube Video Data , Yes/No : ")
if add_choice.upper() == "YES" or add_choice.upper() == "Y":
    if keys_data is None or key not in keys_data:
        data_ref_val = root.child('Youtube-Videos/{}'.format(key))
        val = data_ref_val.get()
        url_link = val.get('url')
        Youtube_Video_data(key, url ,url_link)
    else:
        print("Data Already Present")
else:
    print("Thank You")
