import datetime as dt
import pyscreenshot as ImageGrab
import io
import json
import os
import pprint
import re
import sys
import search_google.api
import time
from google.cloud              import vision
from google.cloud.vision       import types
from googleapiclient.discovery import build
from PIL                       import Image


# class for printing purposes
class Output:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

class SearchStats:
    def __init__(self, count, number_of_results, answer, is_highest_ranked_answer):
        self.count = count
        self.number_of_results = number_of_results
        self.answer = answer
        self.is_highest_ranked_answer = is_highest_ranked_answer

# sends image to google vision API to read text from
# an image
#
# returns an array of text, broken by each newline (text_list)
def google_vision_response(image, path):
    # Load credentials for using google vision
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="/Users/Brett/Development/python-sandbox/key-file.json"

    # Instantiates a google vision client
    client = vision.ImageAnnotatorClient()
    
    # The name of the image file to annotate
    file_name = os.path.join(os.path.dirname(__file__), 'testimage.png')
    
    # Loads the image into memory
    with io.open(file_name, 'rb') as image_file:
        content = image_file.read()

    image = types.Image(content=content)

    # Performs label detection on the image file
    response = client.text_detection(image=image)
    labels = response.text_annotations
    all_text = labels[0].description
    text_list = all_text.split('\n')

    return text_list

# send question to google custom search engine that searches
# google, wikipedia, ask, among other sites
#
# returns results (res)
def query_web(question):
    service = build("customsearch", "v1", developerKey="AIzaSyBIOYJV-5hVpe8CibQoAsEDfGoz7uk_T5k")
    res = service.cse().list( q=question,  cx="009405847973959423901:pbdp0cbhche", ).execute()
    return res 


# scrape the response from google to see how many times
# an answer is mentioned/cited/referenced
def scrape_query_results(result, answer):
    count = 0
    #print("SCRAPEQUERYRESULTS: " + answer)
    for items in result[u'items']:
        url = items[u'link']
        title = items[u'title']
        snippet = items[u'snippet']

        if answer_list[i] in url:
            count += 2
        if answer_list[i] in title:
            count += 3
        if answer_list[i] in snippet:
            count += 1

    number_of_results = result[u'searchInformation'][u'totalResults']
    search_object = SearchStats(count, number_of_results, answer, False)
    return search_object
    #percent = (int(count) * int(number_of_results) / 10000)
    #print('{:4}  |  {:8}  |  {:20s}'.format(count, number_of_results , answer))


# sets question to all lowercase and then removes
# unnecessary words from question using regex \b
# operator (word boundary)
# 
# returns more concise question
def make_question_succint(question):
    question = question.lower()
    question = question.replace('?', '')
    question = re.sub(r'\bwhat\b', '', question)
    question = re.sub(r'\bwhich\b', '', question)
    question = re.sub(r'\bhow\b', '', question)
    question = re.sub(r'\bwho\b', '', question)
    question = re.sub(r'\bwhere\b', '', question)
    question = re.sub(r'\bwhy\b', '', question)
    question = re.sub(r'\bthe\b', '', question)
    question = re.sub(r'\ba\b', '', question)
    question = re.sub(r'\bin\b', '', question)
    question = re.sub(r'\bis\b', '', question)
    question = re.sub(r'\bfor\b', '', question)
    question = re.sub('\s\s+', ' ', question)
    return question

def print_results(search_objects_array, highest_ranked_answer):
    for i in range(1,4):
        if search_objects_array[i-1].count == highest_ranked_answer:
            print(Output.GREEN + '{:4}  |  {:8}  |  {:20s}'
                    .format(search_objects_array[i-1].count, 
                      search_objects_array[i-1].number_of_results,
                        answer_list[i]) + Output.END)
        else:
            print('{:4}  |  {:8}  |  {:20s}'
                   .format(search_objects_array[i-1].count,
                     search_objects_array[i-1].number_of_results,
                       answer_list[i]))


# main method, entry point of program
if __name__ == "__main__":
    img = ImageGrab.grab(bbox=(0,150,490,650)) # X1,Y1,X2,Y2
    img.save('/Users/Brett/Development/python-sandbox/testimage.png')
    
    image_text_list = google_vision_response(img, 'testimage.png')

    # assign question and answer_list
    i = 0
    answer_list = []
    question = ""
    for str in reversed(image_text_list):
        if i < 4:
            answer_list.append(str)
            i = i + 1
            image_text_list.remove(str)

    question = ' '.join(image_text_list)

    question = make_question_succint(question)

    print("=====================================================================")
    print(f"Question: {question}")
    print("=====================================================================")
    print(Output.BOLD + Output.UNDERLINE + 
          'COUNT |  NUM_RES   |  ANSWER            '
          + Output.END)

    search_objects_array = []

    highest_ranked_answer = -1
    for i in range(1,4):
        #if question.find('not') > -1:
        #    questionWithAnswer = question + " -" + answer_list[i]
        #else:
        #    questionWithAnswer = question + " " + answer_list[i]
        questionWithAnswer = question + " " + answer_list[i]

        result = query_web(questionWithAnswer)

        search_objects_array.append(scrape_query_results(result, answer_list[i]))
        
        # set the highest_ranked_answer to colorize the output
        if search_objects_array[i-1].count > highest_ranked_answer:
            highest_ranked_answer = search_objects_array[i-1].count

    print_results(search_objects_array, highest_ranked_answer)       
