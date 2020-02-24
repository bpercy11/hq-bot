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
#importlib.reload(sys)
#sys.setdefaultencoding('utf8')

# class for printing purposes
class output:
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

class searchStats:
    def __init__(self, count, num_results, answer, isHighestRankedAnswer):
        self.count = count
        self.num_results = num_results
        self.answer = answer
        self.isHighestRankedAnswer = isHighestRankedAnswer

# sends image to google vision API to read text from
# an image
#
# returns an array of text, broken by each newline (text_list)
def googleVisionResponse(image, path):
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
def queryWeb(question):
    service = build("customsearch", "v1", developerKey="AIzaSyBIOYJV-5hVpe8CibQoAsEDfGoz7uk_T5k")
    res = service.cse().list( q=question,  cx="009405847973959423901:pbdp0cbhche", ).execute()
    return res 


# scrape the response from google to see how many times
# an answer is mentioned/cited/referenced
def scrapeQueryResults(result, answer):
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

    num_results = result[u'searchInformation'][u'totalResults']
    searchObj = searchStats(count, num_results, answer, False)
    return searchObj
    #percent = (int(count) * int(num_results) / 10000)
    #print('{:4}  |  {:8}  |  {:20s}'.format(count, num_results , answer))


# sets question to all lowercase and then removes
# unnecessary words from question using regex \b
# operator (word boundary)
# 
# returns more concise question
def makeQuestionSuccint(question):
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

def printResults(searchObjects):
    for i in range(1,4):
        if searchObjects[i-1].isHighestRankedAnswer:
            print('{:4}  |  {:8}  |  {:20s} <--'.format(searchObjects[i-1].count, searchObjects[i-1].num_results , answer_list[i]))
        else:
            print('{:4}  |  {:8}  |  {:20s}'.format(searchObjects[i-1].count, searchObjects[i-1].num_results , answer_list[i]))


# main method, entry point of program
if __name__ == "__main__":
    img = ImageGrab.grab(bbox=(0,150,490,650)) # X1,Y1,X2,Y2
    img.save('/Users/Brett/Development/python-sandbox/testimage.png')
    
    image_text_list = googleVisionResponse(img, 'testimage.png')

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

    question = makeQuestionSuccint(question)
    print("=====================================================================")
    print(f"Question: {question}")
    print("=====================================================================")
    print(output.BOLD + output.UNDERLINE + 'COUNT |  NUM_RES   |  ANSWER            ' + output.END)

    searchObjects = []

    highest_ranked_answer = -1
    for i in range(1,4):
        #if question.find('not') > -1:
        #    questionWithAnswer = question + " -" + answer_list[i]
        #else:
        #    questionWithAnswer = question + " " + answer_list[i]
        questionWithAnswer = question + " " + answer_list[i]

        result = queryWeb(questionWithAnswer)

        searchObjects.append(scrapeQueryResults(result, answer_list[i]))
        
        # set 
        #if searchObjects[i-1].count > highest_ranked_answer:
            #searchObjects[i-1].isHighestRankedAnswer = True

    printResults(searchObjects)       
