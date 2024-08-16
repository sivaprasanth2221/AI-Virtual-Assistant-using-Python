import pyttsx3
import speech_recognition as sr
import datetime
import os
from requests import get
import pywhatkit
import wikipedia
import json
import webbrowser
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)


# Load the JSON data
with open('Brain.json') as data:
    brain_data = json.load(data)

# Extract the commands (keys) from the JSON data
commands = list(brain_data.keys())

# Vectorize the commands using TF-IDF
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(commands)


#Funtion to write new words in a json file("Brain")
def write(cmd, ans):
    with open('Brain.json') as jsonfile:
        decoded = json.load(jsonfile)
    decoded[str(cmd)] = str(ans)
    with open('Brain.json', 'w') as jsonfile:
        json.dump(decoded, jsonfile,indent=5)

# Speaking function
def speak(audio):
    engine.say(audio)
    print(audio)
    engine.runAndWait()

# Recognizing Function
def recognize():
    reco = sr.Recognizer()
    with sr.Microphone() as source:
        print('Listening..')
        reco.pause_threshold = 1
        audio = reco.listen(source, timeout=1, phrase_time_limit=3)

    try:
        print('Recognizing...')
        query = reco.recognize_google(audio, language='en-in')
        query = query.lower()
        if 'Das' in query:
            query = query.replace('Das', '')
        print('User said: ', query)
    except Exception as e:
        speak('Can you please repeat..')
        return 'none'
    return query

# Wishing
def wish():
    hour = datetime.datetime.now().hour
    if hour >= 0 and hour < 12:
        speak('Good Morning')
    elif hour >= 12 and hour < 20:
        speak('Good Afternoon')
    else:
        speak('Good Night')

    speak('I am Das, your personal Assistant')
    
    
def find_most_similar_command(query):
    # Transform the query into a TF-IDF vector
    query_tfidf = vectorizer.transform([query])

    # Calculate cosine similarity between the query and commands
    similarities = cosine_similarity(query_tfidf, tfidf_matrix).flatten()

    # Find the index of the most similar command
    most_similar_index = similarities.argmax()

    # Check if the similarity is above a certain threshold
    if similarities[most_similar_index] > 0.7:
        return commands[most_similar_index]
    else:
        return None
    


if __name__ == '__main__':
    wish()
    while True:
        query=recognize()
        if 'bye' or 'goodbye' or 'exit' in query:
            print("Thank You. Have a good day")
            speak('Thank You. Have a good day')
            break
        # To open apps:
        if 'notepad' in query:
            path = 'C:\WINDOWS\system32\\notepad.exe'
            os.startfile(path)

        if 'command' in query:
            #path = 'C:\WINDOWS\system32\\cmd.exe'
            #os.startfile(path)
            os.system('start cmd')

        # playing songs in YouTube
        if 'play' in query:
            query = query.replace('play', '')
            speak('Playing {}'.format(query))
            pywhatkit.playonyt(query)

        # getting ip
        if 'ip address' in query:
            ip = get('https://api.ipify.org').text
            speak('Your IP Address is : {}'.format(ip))

        # time
        if 'time' in query:
            time = datetime.datetime.now().strftime('%I:%M %p')
            speak('The Time is - '+time)      
 # wiki
        if 'tell me about' in query:
            person = query.replace('tell me about', '')
            info = wikipedia.summary(person, 1)
            speak(info)
 #opening browsers
        if 'open instagram' in query:
            webbrowser.open('www.instagram.com')
        if 'open browser' in query:
            speak('What do you want me to search')
            search=recognize()
            speak('Okay')
            webbrowser.open('www.google.com/search?q=' + str(search))
        #To make her learn new phrases and to use them when needed
        else:
            while True:
                #Imma connect the json dict
                with open('words.json') as data:
                    list = json.load(data)
                if query in list:
                    speak(list[query])
                    break
                else:
                    speak('I cant understand...Do you want me to save the phrase?')
                    query = recognize().lower()
                    if 'yes' in query:
                        speak('Repeat the command please')
                        cmd = recognize().lower()
                        speak('What reply should I give')
                        ans = recognize().lower()
                        write(cmd, ans)
                        speak('Thank you for this information')
                        break
                    if 'no' in query:
                        speak('Okay')
                        break
