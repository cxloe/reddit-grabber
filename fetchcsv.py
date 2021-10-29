
import pandas as pd
import requests #Pushshift accesses Reddit via an url so this is needed
import json #JSON manipulation
import csv #To Convert final table into a csv file to save to your machine
import time
import datetime
import docopt

__doc__ = '''
Usage: prog AF QU SU FI
'''

args = docopt.docopt(__doc__, more_magic = True)
print(args)

#Adapted from this https://gist.github.com/dylankilkenny/3dbf6123527260165f8c5c3bc3ee331b
#This function builds an Pushshift URL, accesses the webpage and stores JSON data in a nested list
def getPushshiftData(qu, af, before, su):
    #Build URL
    url = 'https://api.pushshift.io/reddit/search/submission/?title='+str(args.QU)+'&size=1000&after='+str(args.AF)+'&before='+str(before)+'&subreddit='+str(args.SU)
    #Print URL to show user
    print(url)
    #Request URL
    r = requests.get(url)
    #Load JSON data from webpage into data variable
    data = json.loads(r.text)
    #return the data element which contains all the submissions data
    return data['data']

#This function will be used to extract the key data points from each JSON result
def collectSubData(subm):
    #subData was created at the start to hold all the data which is then added to our global subStats dictionary.
    subData = list() #list to store data points
    title = subm['title']
    url = subm['url']
    #flairs are not always present so we wrap in try/except
    try:
        flair = subm['link_flair_text']
    except KeyError:
        flair = "NaN"
    author = subm['author']
    sub_id = subm['id']
    score = subm['score']
    created = datetime.datetime.fromtimestamp(subm['created_utc']) #1520561700.0
    numComms = subm['num_comments']
    permalink = subm['permalink']

    #Put all data points into a tuple and append to subData
    subData.append((sub_id,title,url,author,score,created,numComms,permalink,flair))
    #Create a dictionary entry of current submission data and store all data related to it
    subStats[sub_id] = subData


#Create your timestamps and queries for your search URL
#https://www.unixtimestamp.com/index.php > Use this to create your timestamps

#turn these into a function?
#bElement = datetime.datetime.strptime(af,"%d/%m/%Y")
#bTuple = bElement.timetuple()
#bTimestamp = int(time.mktime(bTuple))
before = int(time.time())


element = datetime.datetime.strptime(args.AF,"%d/%m/%Y")
tuple = element.timetuple()
timestamp = int(time.mktime(tuple))
after = timestamp


query = args.QU #Keyword(s) to look for in submissions
sub = args.SU #Which Subreddit to search in

#subCount tracks the no. of total submissions we collect
subCount = 0
#subStats is the dictionary where we will store our data.
subStats = {}

# We need to run this function outside the loop first to get the updated after variable
data = getPushshiftData(query, after, before, sub)
# Will run until all posts have been gathered i.e. When the length of data variable = 0
# from the 'after' date up until before date
while len(
        data) > 0:  # The length of data is the number submissions (data[0], data[1] etc), once it hits zero (after and before vars are the same) end
    for submission in data:
        collectSubData(submission)
        subCount += 1
    # Calls getPushshiftData() with the created date of the last submission
    print(len(data))
    print(str(datetime.datetime.fromtimestamp(data[-1]['created_utc'])))
    # update after variable to last created date of submission
    after = data[-1]['created_utc']
    # data has changed due to the new after variable provided by above code
    data = getPushshiftData(query, after, before, sub)

print(len(data))


def updateSubs_file():
    upload_count = 0
    # location = "\\Reddit Data\\" >> If you're running this outside of a notebook you'll need this to direct to a specific location
    filename = FI  # This asks the user what to name the file
    file = filename
    with open(file, 'w', newline='', encoding='utf-8') as file:
        a = csv.writer(file, delimiter=',')
        headers = ["Post ID", "Title", "Url", "Author", "Score", "Publish Date", "Total No. of Comments", "Permalink",
                   "Flair"]
        a.writerow(headers)
        for sub in subStats:
            a.writerow(subStats[sub][0])
            upload_count += 1

        print(str(upload_count) + " submissions have been uploaded")


updateSubs_file()
