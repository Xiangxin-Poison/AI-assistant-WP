from datetime import datetime
import speech_recognition as sr
import pyttsx3
import webbrowser
import wikipedia
import wolframalpha
import pywhatkit
import random
import lyricsgenius
import time

# Speech engine initialization
engine = pyttsx3.init()
voices = engine.getProperty('voices')

# Set the voice to a professional female voice
for voice in voices:
    if "female" in voice.name.lower() and "professional" in voice.name.lower():
        engine.setProperty('voice', voice.id)
        break

# Adjust the pitch and rate for a professional sound
engine.setProperty('pitch', 0.9)  # Increase or decrease the value to adjust the pitch
engine.setProperty('rate', 180)   # Adjust the value to control the speech rate

# Configure browser
brave_path = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
webbrowser.register('brave', None, webbrowser.BackgroundBrowser(brave_path))

# Wolfram Alpha client
appId = 'X26573-49TRG8JJ4P'
wolframClient = wolframalpha.Client(appId)

# Predefined responses
greetings = ['Hello!', 'Hi there!', 'Greetings!', 'How can I assist you today?']
farewells = ['Goodbye!', 'Farewell!', 'Have a great day!', 'Until next time!']
jokes = ['Why don’t scientists trust atoms? Because they make up everything!', 'I’m reading a book about anti-gravity. It’s impossible to put down!',
         'Why did the scarecrow win an award? Because he was outstanding in his field!', 'Why did the bicycle fall over? Because it was two-tired!']

# Personality-based responses
def get_personality_response(query):
    if 'how are you' in query:
        return 'I am an AI, so I don\'t experience emotions, but thank you for asking!'
    elif 'joke' in query:
        return random.choice(jokes)
    elif 'thank you' in query:
        return 'You\'re welcome!'
    elif 'your name' in query:
        return 'I am Shadow, your helpful AI assistant.'
    else:
        return None

# Create a Genius API client
genius = lyricsgenius.Genius('YOUR_ACCESS_TOKEN')

def sing_song(song_title):
    try:
        # Search for the lyrics of the song
        song = genius.search_song(song_title)
        if song:
            lyrics = song.lyrics
            speak("I will now sing a song for you. Here it goes!")
            speak(lyrics)
        else:
            speak("I couldn't find the lyrics for that song.")
    except Exception as e:
        print(f"An error occurred while singing the song: {str(e)}")
        speak("Sorry, I encountered an error while singing the song.")

def speak(text, rate=120):
    engine.setProperty('rate', rate)
    engine.say(text)
    engine.runAndWait()


def parseCommand():
    listener = sr.Recognizer()
    print('Listening for a command')

    with sr.Microphone() as source:
        listener.pause_threshold = 2
        input_speech = listener.listen(source)

    try:
        print('Recognizing speech...')
        query = listener.recognize_google(input_speech, language='en_gb')
        print(f'The input speech was: {query}')
    except sr.UnknownValueError:
        print('I did not quite catch that')
        speak('I did not quite catch that')
        return 'None'
    except sr.RequestError:
        print('Sorry, my speech service is unavailable')
        speak('Sorry, my speech service is unavailable')
        return 'None'

    return query


def search_wikipedia(query=''):
    try:
        searchResults = wikipedia.search(query)
        if not searchResults:
            print('No Wikipedia result')
            return 'No result received'

        wikiPage = wikipedia.page(searchResults[0])
        print(wikiPage.title)
        wikiSummary = str(wikiPage.summary)

        # Write summary to file
        now = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        with open(f'wikipedia_summary_{now}.txt', 'w') as summary_file:
            summary_file.write(wikiSummary)

        return wikiSummary
    except wikipedia.exceptions.WikipediaException:
        print('An error occurred while searching Wikipedia')
        return 'An error occurred while searching Wikipedia'


def listOrDict(var):
    if isinstance(var, list):
        return var[0]['plaintext']
    else:
        return var['plaintext']


def search_wolframAlpha(query=''):
    try:
        response = wolframClient.query(query)

        if response['@success'] == 'false':
            return 'Could not compute'

        result = ''
        pod0 = response['pod'][0]
        pod1 = response['pod'][1]

        if 'result' in pod1['@title'].lower() or pod1.get('@primary', 'false') == 'true' or 'definition' in pod1['@title'].lower():
            result = listOrDict(pod1['subpod'])
            return result.split('(')[0]
        else:
            question = listOrDict(pod0['subpod'])
            return question.split('(')[0]
    except wolframalpha.WolframAlphaException:
        print('An error occurred while searching Wolfram Alpha')
        return 'An error occurred while searching Wolfram Alpha'


def update_conversations(user_query, ai_response):
    with open('conversations.txt', 'a') as file:
        file.write(f'{user_query}\n{ai_response}\n')


def self_learn():
    try:
        with open('conversations.txt', 'r') as file:
            lines = file.readlines()

        conversations = [line.strip() for line in lines]
        user_queries = conversations[::2]
        ai_responses = conversations[1::2]

        if len(user_queries) > 0 and len(ai_responses) > 0:
            # Select a random conversation
            index = random.randint(0, len(user_queries) - 1)
            user_query = user_queries[index]
            ai_response = ai_responses[index]

            print('AI is learning from user feedback...')
            speak('How can I improve? Please provide feedback on my response.')
            user_feedback = parseCommand().lower()

            if 'good' in user_feedback or 'great' in user_feedback:
                print('User is satisfied with the response. Learning complete.')
            else:
                print('User is not satisfied with the response. Learning from feedback...')
                with open('conversations.txt', 'a') as file:
                    file.write(f'{user_query}\n{user_feedback}\n')

                print('Learning complete.')

    except FileNotFoundError:
        print('No conversation data found. Start interacting to generate data.')


if __name__ == '__main__':
    speak(random.choice(greetings))

    while True:
        query = parseCommand().lower().split()

        response = get_personality_response(' '.join(query))
        if response:
            speak(response)
            update_conversations(' '.join(query), response)
            continue

        if query[0] == 'say':
            if 'hello' in query:
                speak('Greetings, all.')
            else:
                query.pop(0)  # Remove "say"
                speech = ' '.join(query)
                speak(speech)

        elif query[0] == 'go' and query[1] == 'to':
            speak('Opening...')
            query = ' '.join(query[2:])
            webbrowser.get('brave').open_new(query)

        elif query[0] == 'search':
            query = ' '.join(query[2:])
            speak('Querying Wikipedia for ' + query)
            summary = search_wikipedia(query)
            speak(summary)
            update_conversations(' '.join(query), summary)

        elif query[0] == 'computer' or query[0] == 'shadow':
            query = ' '.join(query[1:])
            speak('Computing')
            result = search_wolframAlpha(query)
            speak(result)
            update_conversations(' '.join(query), result)

        elif 'take note' in query:
            speak('Ready to record your note')
            newNote = parseCommand().lower()
            now = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
            with open(f'note_{now}.txt', 'w') as newFile:
                newFile.write(newNote)
            speak('Note written')
            update_conversations(' '.join(query), 'Note written')

        elif query[0] == 'play':
            query = ' '.join(query[1:])
            speak('Playing ' + query)
            pywhatkit.playonyt(query)
            
        elif query[0] == 'sing':
            query = ' '.join(query[1:])
            sing_song(query)

        elif 'time' in query:
            time = datetime.now().strftime('%H:%M')
            speak('The time is ' + time)

        elif query[0] == 'goodbye':
            speak(random.choice(farewells))
            break

        self_learn()
