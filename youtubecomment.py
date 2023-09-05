from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from datetime import datetime
import pandas as pd
from langdetect import detect
from textblob import TextBlob
import re
import sys
from pytube import YouTube
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import matplotlib.pyplot as plt
from wordcloud import WordCloud
# from nltk.corpus import nrc_emotion_lexicon
import spacy

# Load the spaCy English language model
nlp = spacy.load("en_core_web_sm")

def generate_response(input_text):
    # Function to generate a response based on user input
    doc = nlp(input_text)
    # You can add custom logic here to generate responses based on user input
    response = doc
    return response

# import nltk
# nltk.download('nrc_emotion_lexicon')


cred = credentials.Certificate("C://Users//Mohak//Desktop//Big_Project//cred.json")

firebase_admin.initialize_app(cred, {
    'databaseURL' : "https://link-bd2ea-default-rtdb.firebaseio.com/"
})

root = db.reference()
ref = db.reference('Youtube-Videos')
data_ref = root.child('Youtube-Videos')
keys = data_ref.get(shallow=True)
ref_data = db.reference('Youtube-Videos-data')
data_ref_data = root.child('Youtube-Videos-data')
keys_data = data_ref_data.get(shallow=True)




def ScrapeComment(key , url_2):
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

    if keys_data is not None and key in keys_data:
        video_data = ref_data.child(key).get()
        if isinstance(video_data, dict):
            print("\nTitle : {}".format(video_data.get('title')))
            print("\nSubscribers : {}".format(video_data.get('subscribers')))
            print("\nViews : {}".format(video_data.get('views')))
            print("\nUpload-Date : {}".format(video_data.get('upload-date')))
        else:
            print("\nData Not Found")
    else:
        print("\nData Not Found")


    comments = []
    nested_comments_list = []
    likes_list = []
    author_list = []
    
    comment_sections = soup.find_all('yt-formatted-string', {'class': 'style-scope ytd-comment-renderer'})

    for comment_section in comment_sections:
        
        comment_text = comment_section.text.strip()
        comments.append(comment_text)

        nested_comments = []
        nested_comment_elements = comment_section.find_all('yt-formatted-string', {'class': 'style-scope ytd-comment-renderer'})
        for nested_comment in nested_comment_elements:
            nested_comment_text = nested_comment.text.strip()
            nested_comments.append(nested_comment_text)
        nested_comments_list.append(nested_comments)

        
        like_dislike_section = comment_section.find_next('span', {'id': 'vote-count-left'})
        if like_dislike_section:
            likes_dislikes = like_dislike_section.text.split()
            likes = likes_dislikes[0] if len(likes_dislikes) > 0 else None
            dislikes = likes_dislikes[2] if len(likes_dislikes) > 2 else None
            likes_list.append(likes)
        else:
            likes_list.append(None)

        
        author_name = comment_section.find_previous('a', {'id': 'author-text'}).text.strip()
        author_list.append(author_name)

    
    data = {
        'Comment': comments,
        'Likes': likes_list, 
        'Author' : author_list
    }
    df = pd.DataFrame(data)
    
    print(df)

    sentiment_analysis_using_textblob(comments)
    sentiment_analysis_using_vader(comments)
    # emotion_ana = input("\n Do you want to do emotions analysis , Yes/No : ")
    # if emotion_ana.upper() == "YES" or emotion_ana.upper() == "Y":
    #     emotions_list = emotion_analysis(comments)
    #     for i, emotions in enumerate(emotions_list, start=1):
    #         print(f"Emotions for Comment {i}:")
    #         for emotion, is_present in emotions.items():
    #             if is_present:
    #                 print(f"{emotion.capitalize()}: {is_present}")


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

def sentiment_analysis_using_textblob(comments_1):
    english_comments = {}

    english = []
    hindi_comments = {}
    hindi = []
    text_list = []
    sentiment_list_tb = []
    sentiment_score_list_tb = []
    custom_sentiments = []
    
    for i in range(len(comments_1)):
        comment_text = comments_1[i]
        try:
            detected_language = detect(comment_text)
        except:
            detected_language = 'unknown'
        
        if detected_language == 'en':
            english_comments[i] = comment_text
        elif detected_language == 'hi':
            hindi_comments[i] = comment_text

    for i, comment_text in english_comments.items():
        comment_text = comment_text.replace("\n", "")
        english.append(comment_text)

    for i, comment_text in hindi_comments.items():
        comment_text = comment_text.replace("\n", "")
        hindi.append(comment_text)
    
    for text in english:
        analysis = TextBlob(text)
        
        # You can use the sentiment property directly without calling correct()
        polarity = analysis.sentiment.polarity
        
        if polarity > 0:
            sentiment = "Positive"
        elif polarity < 0:
            sentiment = "Negative"
        else:
            sentiment = "Neutral"
        
        text_list.append(text)
        sentiment_list_tb.append(sentiment)
        sentiment_score_list_tb.append(polarity)


    df_1 = pd.DataFrame({'Text': text_list, 'Sentiment-Score': sentiment_score_list_tb, 'Sentiment': sentiment_list_tb})

    print(df_1)

    overall_sentiment_textblob = calculate_overall_sentiment(sentiment_score_list_tb)

    print("Overall Sentiment (TextBlob):", overall_sentiment_textblob)

    advance_analysis = input("\nDo you want to do advance analysis , Yes/No : ")
    if advance_analysis.upper() == "YES" or advance_analysis.upper() == "Y":
        strong_positive_threshold = 0.6
        slightly_positive_threshold = 0.2
        strong_negative_threshold = -0.6
        slightly_negative_threshold = -0.2

        for sentiment_score in sentiment_score_list_tb:
            if sentiment_score >= strong_positive_threshold:
                custom_sentiments.append("Strongly Positive")
            elif sentiment_score >= slightly_positive_threshold:
                custom_sentiments.append("Slightly Positive")
            elif sentiment_score <= strong_negative_threshold:
                custom_sentiments.append("Strongly Negative")
            elif sentiment_score <= slightly_negative_threshold:
                custom_sentiments.append("Slightly Negative")
            else:
                custom_sentiments.append("Neutral")

        sentiment_distribution = {
            "Strongly Positive": custom_sentiments.count("Strongly Positive"),
            "Slightly Positive": custom_sentiments.count("Slightly Positive"),
            "Neutral": custom_sentiments.count("Neutral"),
            "Slightly Negative": custom_sentiments.count("Slightly Negative"),
            "Strongly Negative": custom_sentiments.count("Strongly Negative"),
        }

        print("Sentiment Distribution:", sentiment_distribution)
    else:
        pass
    
    print("\nVisualizing Sentiment Analysis(TextBlob)")
    sentiment_analysis_using_textblob_visuals(text_list,sentiment_list_tb,sentiment_score_list_tb)

def sentiment_analysis_using_textblob_visuals(comments , sentiment , sentiment_scores):
    sentiment_counts = {
    "Positive": sentiment.count("Positive"),
    "Negative": sentiment.count("Negative"),
    "Neutral": sentiment.count("Neutral")
    }

    # Create a bar chart to visualize sentiment distribution
    plt.figure(figsize=(8, 6))
    plt.bar(sentiment_counts.keys(), sentiment_counts.values(), color=['green', 'red', 'gray'])
    plt.title('Sentiment Distribution in Comments')
    plt.xlabel('Sentiment Category')
    plt.ylabel('Number of Comments')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.show()

    # Create a pie chart to visualize sentiment distribution
    labels = sentiment_counts.keys()
    sizes = sentiment_counts.values()

    plt.figure(figsize=(6, 6))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.title('Sentiment Distribution in Comments')
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.show()

    # Create a word cloud to visualize the most frequent keywords in comments
    text = " ".join(comments)

    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)

    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title('Word Cloud of Keywords in Comments')
    plt.show()

    #Histogram of Sentiment Scores
    plt.figure(figsize=(8, 6))
    plt.hist(sentiment_scores, bins=10, color='blue', alpha=0.7)
    plt.xlabel('Sentiment Score')
    plt.ylabel('Frequency')
    plt.title('Distribution of Sentiment Scores')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.show()

    #Box Plot for Sentiment Scores:
    plt.figure(figsize=(8, 6))
    plt.boxplot(sentiment_scores, vert=False)
    plt.xlabel('Sentiment Score')
    plt.title('Box Plot of Sentiment Scores')
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    plt.show()

def calculate_overall_sentiment(sentiment_scores):

    mean_sentiment_score = sum(sentiment_scores) / len(sentiment_scores)

    if mean_sentiment_score > 0:
        overall_sentiment = "Positive"
    elif mean_sentiment_score < 0:
        overall_sentiment = "Negative"
    else:
        overall_sentiment = "Neutral"

    return overall_sentiment

def sentiment_analysis_using_vader(comments_1):
    text_list = []
    sentiment_list_vader = []
    sentiment_score_list_vader = []
    custom_sentiments = []

    sia = SentimentIntensityAnalyzer()
    for comment in comments_1:
        sentiment_scores = sia.polarity_scores(comment)
        
        # Determine sentiment based on compound score
        if sentiment_scores["compound"] >= 0.05:
            sentiment = "Positive"
        elif sentiment_scores["compound"] <= -0.05:
            sentiment = "Negative"
        else:
            sentiment = "Neutral"
        # print("\n{}".format(sentiment_scores))
        text_list.append(comment)
        sentiment_list_vader.append(sentiment)
        sentiment_score_list_vader.append(sentiment_scores["compound"])

    df_1 = pd.DataFrame({'Text': text_list, 'Sentiment-Score': sentiment_score_list_vader, 'Sentiment': sentiment_list_vader})

    print(df_1)

    overall_sentiment_vader = calculate_overall_sentiment_vad(sentiment_score_list_vader)

    print("Overall Sentiment (VADER):", overall_sentiment_vader)

    advance_analysis = input("\nDo you want to do advance analysis , Yes/No : ")
    if advance_analysis.upper() == "YES" or advance_analysis.upper() == "Y":
        strong_positive_threshold = 0.6
        slightly_positive_threshold = 0.2
        strong_negative_threshold = -0.6
        slightly_negative_threshold = -0.2

        for sentiment_score in sentiment_score_list_vader:
            if sentiment_score >= strong_positive_threshold:
                custom_sentiments.append("Strongly Positive")
            elif sentiment_score >= slightly_positive_threshold:
                custom_sentiments.append("Slightly Positive")
            elif sentiment_score <= strong_negative_threshold:
                custom_sentiments.append("Strongly Negative")
            elif sentiment_score <= slightly_negative_threshold:
                custom_sentiments.append("Slightly Negative")
            else:
                custom_sentiments.append("Neutral")

        sentiment_distribution = {
            "Strongly Positive": custom_sentiments.count("Strongly Positive"),
            "Slightly Positive": custom_sentiments.count("Slightly Positive"),
            "Neutral": custom_sentiments.count("Neutral"),
            "Slightly Negative": custom_sentiments.count("Slightly Negative"),
            "Strongly Negative": custom_sentiments.count("Strongly Negative"),
        }

        print("Sentiment Distribution:", sentiment_distribution)
    else:
        pass
    aspect_choice = input("\nDo you want to do Aspect Sentimental Analysis , Yes/No : ")
    if aspect_choice.upper() == "YES" or aspect_choice.upper() == "Y":
        aspect_sentiment_analysis_using_vader(comments_1)
    else:
        pass

    print("\nVisualizing Sentiment Analysis(Vader)")
    sentiment_analysis_using_vader_visuals(text_list , sentiment_list_vader , sentiment_score_list_vader)

def sentiment_analysis_using_vader_visuals(comments , sentiment ,sentiment_scores):
    sentiment_counts = {
    "Positive": sentiment.count("Positive"),
    "Negative": sentiment.count("Negative"),
    "Neutral": sentiment.count("Neutral")
    }

    # Create a bar chart to visualize sentiment distribution
    plt.figure(figsize=(8, 6))
    plt.bar(sentiment_counts.keys(), sentiment_counts.values(), color=['green', 'red', 'gray'])
    plt.title('Sentiment Distribution in Comments')
    plt.xlabel('Sentiment Category')
    plt.ylabel('Number of Comments')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.show()

    # Create a pie chart to visualize sentiment distribution
    labels = sentiment_counts.keys()
    sizes = sentiment_counts.values()

    plt.figure(figsize=(6, 6))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.title('Sentiment Distribution in Comments')
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.show()

    # Create a word cloud to visualize the most frequent keywords in comments
    text = " ".join(comments)

    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)

    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title('Word Cloud of Keywords in Comments')
    plt.show()

    #Histogram of Sentiment Scores
    plt.figure(figsize=(8, 6))
    plt.hist(sentiment_scores, bins=10, color='blue', alpha=0.7)
    plt.xlabel('Sentiment Score')
    plt.ylabel('Frequency')
    plt.title('Distribution of Sentiment Scores')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.show()

    #Box Plot for Sentiment Scores:
    plt.figure(figsize=(8, 6))
    plt.boxplot(sentiment_scores, vert=False)
    plt.xlabel('Sentiment Score')
    plt.title('Box Plot of Sentiment Scores')
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    plt.show()

def aspect_sentiment_analysis_using_vader(comments_1):
    aspects = {
    "Content Quality": ["content quality", "information", "valuable"],
    "Presentation": ["presentation", "presenter", "style", "boring"],
    }

    sia = SentimentIntensityAnalyzer()

    aspect_sentiments = {aspect: {"comments": [], "sentiment_scores": []} for aspect in aspects}

    for comment in comments_1:
        sentiment_scores = sia.polarity_scores(comment)
        for aspect, keywords in aspects.items():
            if any(keyword in comment.lower() for keyword in keywords):
                aspect_sentiments[aspect]["comments"].append(comment)
                aspect_sentiments[aspect]["sentiment_scores"].append(sentiment_scores["compound"])

    for aspect, data in aspect_sentiments.items():
        sentiment_scores = data["sentiment_scores"]
        if sentiment_scores:
            overall_sentiment_score = sum(sentiment_scores) / len(sentiment_scores)
            if overall_sentiment_score >= 0:
                overall_sentiment = "Positive"
            else:
                overall_sentiment = "Negative"
        else:
            overall_sentiment = "No Comments"

        print(f"Aspect: {aspect}")
        print(f"Overall Sentiment: {overall_sentiment}")
        print(f"Comments:")
        for comment in data["comments"]:
            print(comment)
        print("\n")

def calculate_overall_sentiment_vad(sentiment_scores):
    
    mean_sentiment_score = sum(sentiment_scores) / len(sentiment_scores)

    if mean_sentiment_score > 0.05:
        overall_sentiment = "Positive"
    elif mean_sentiment_score < -0.05:
        overall_sentiment = "Negative"
    else:
        overall_sentiment = "Neutral"

    return overall_sentiment



if __name__ == "__main__":
    choice = int(input("Press 1 For Scrapping data \nPress 0 for exit \nEnter your choice = "))
    if choice == 0:
        exit()
    elif choice == 1:
        url = input("Enter Youtube Video URL = ")
        comma_index = url.find('=')
        key = url[comma_index + 1:]  
        if key not in keys:
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

        choice_1 = input("Do you want to do analysis of Youtube Video , Yes/No : ")
        if choice_1.upper() == "YES" or choice_1.upper() == "Y":
            data_ref_val = root.child('Youtube-Videos/{}'.format(key))
            val = data_ref_val.get()
            url_link = val.get('url')
            ScrapeComment(key , url_link)
        else:
            pass

        while True:
            user_input = input("You: ")
            if user_input.lower() == "exit":
                break
            response = generate_response(user_input)
            print("Bot:", response)
    else:
        print("Invalid Input")







# nrc_lexicon_file = "C://Users//Mohak//Desktop//Big_Project//NRC-Emotion-Lexicon-Wordlevel-v0.92.txt"  # Replace with the actual file path


# def load_nrc_lexicon(file_path):
#     lexicon = {}
#     with open(file_path, 'r') as lexicon_file:
#         for line in lexicon_file:
#             word, emotion, value = line.strip().split('\t')
#             if word not in lexicon:
#                 lexicon[word] = {}
#             lexicon[word][emotion] = int(value)
#     return lexicon

# nrc_emotion_lexicon = load_nrc_lexicon(nrc_lexicon_file)
# print(nrc_emotion_lexicon)




# def emotion_analysis(comment_list):
#     emotions_list = []

#     for comment in comment_list:
#         emotions = {emotion: False for emotion in nrc_emotion_lexicon.keys()}
#         words = comment.split()
        
#         for word in words:
#             for emotion in nrc_emotion_lexicon.keys():
#                 if word in nrc_emotion_lexicon.get(emotion, []):
#                     emotions[emotion] = True

#         emotions_list.append(emotions)

#     return emotions_list
