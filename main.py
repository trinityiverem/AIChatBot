import aiml
import nltk
import pandas as pd
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import wordnet
import csv
import spacy
from nltk.sem import Expression
from nltk.inference import ResolutionProver
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import requests
import json

# Create a Kernel object. No string encoding (all I/O is unicode)
kern = aiml.Kernel()
kern.setTextEncoding(None)
# Create the kernel and learn AIML files
kern.learn("std-startup.xml")

# Use the Kernel's bootstrap() method to initialize the Kernel. The
# optional learnFiles argument is a file (or list of files) to load.
# The optional commands argument is a command (or list of commands)
# to run after the files are loaded.
# The optional brainFile argument specifies a brain file to load.

kern.learn("/Users/trinity/PycharmProjects/chatbot1/chat.xml")
kern.respond("load aiml b")
df = pd.read_csv('/Users/trinity/Documents/questions.csv', header=None)

kb = []
read_expr = Expression.fromstring
data = pd.read_csv('kb.csv', header=None)
[kb.append(read_expr(row)) for row in data[0]]
if not kb:
    print('Error with kb.csv \nPLease Check')

str_kb = []
[str_kb.append(row) for row in data[0]]

#######################################################
# Welcome user
#######################################################
print("Welcome to this chat bot. Please feel free to ask questions from me!")
#######################################################
# Main loop
#######################################################
while True:
    # get user input
    try:
        userInput = input("You > ")
    except (KeyboardInterrupt, EOFError) as e:
        print("Bye!")
        break
    # pre-process user input and determine response agent (if needed)
    responseAgent = 'aiml'
    # activate selected response agent
    if responseAgent == 'aiml':
        answer = kern.respond(userInput)
    # post-process the answer for commands
    if userInput[0] == '#':
        params = userInput[1:].split('$')
        cmd = int(params[0])
        words = params[1]
        if cmd == 0:
            print(params[1])
            break

        elif cmd == 2:
            planet_name = input("Chatbot > Enter the name of the planet: ")

            api_url = 'https://planets-by-api-ninjas.p.rapidapi.com/v1/planets'
            querystring = {"name": planet_name}

            headers = {
                "X-RapidAPI-Key": "14cd95106fmshbb8be2ae40fead0p15abe4jsn72233175ed86",  # Replace with your actual RapidAPI key
                "X-RapidAPI-Host": "planets-by-api-ninjas.p.rapidapi.com"
            }

            print("Querystring:", querystring)

            response = requests.get(api_url, headers=headers, params=querystring)



            response = requests.get(api_url, headers=headers, params=querystring)

            if response.status_code == 200:
                print("Response Content:", response.content)
                  # Print the planet information here
            else:
                print("Sorry, I could not check the planet information you gave me.")

        elif cmd == 99:
            notInQuestionsCsv = False

            vectorizer = TfidfVectorizer()
            tfidf = vectorizer.fit_transform(df[0])
            user_tfidf = vectorizer.transform([words])
            similarity_scores = cosine_similarity(user_tfidf, tfidf)
            most_similar_score = similarity_scores.max()
            if most_similar_score >= 0.92:
                most_similar_index = similarity_scores.argmax()
                response = df.loc[most_similar_index, 1]

                print("Chatbot > " + response)
                notInQuestionsCsv = True
            if not notInQuestionsCsv:
                print("I did not get that, please try again.")

                # Here are the processing of the new logical component:
        elif cmd == 31:  # if input pattern is "I know that * is *"
            object, subject = params[1].split(' is ')
            expr = read_expr(subject + '(' + object + ')')
            str_expr = str(expr)

            Ratio = process.extractOne(str_expr, str_kb, scorer=fuzz.WRatio)
            answer = ResolutionProver().prove(expr, kb, verbose=True)
            if (Ratio[1] >= 100) or answer:

                print("Correct")

            elif subject.lower() == 'planet' or subject.lower() == 'moon':
                kb.append(expr)
                print('OK, I will remember that', object, 'is a', subject)
            # >>> ADD SOME CODES HERE to make sure expr does not contradict
            # with the KB before appending, otherwise show an error message.
            else:
                print('Could you please enter a valid Statement ')


        elif cmd == 33:
            object, subject = params[1].split(' is a ')
            expr = read_expr(subject + '(' + object + ')')
            answer = ResolutionProver().prove(expr, kb, verbose=True)
            if answer:
                print('Chatbot > Correct.')
            else:
                print('Chatbot > It may not be true.')

    else:
        print("Chatbot > " + answer)
