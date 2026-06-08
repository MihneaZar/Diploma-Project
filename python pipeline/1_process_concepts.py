print("Importing...")

from threading import Thread
from tqdm import tqdm
import pandas as pd
import spacy
# import needed for spacy textrank pipeline
import pytextrank
from langdetect import detect
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from string import digits
import calendar
import re
import os

os.chdir("..")

nltk.download('stopwords')

print("Imports finished. Reading data...")

csv_file = next((file for file in os.listdir() if file[-3:] == "csv"))
data = pd.read_csv(csv_file)[["abstract", "year"]].dropna()
print(len(data))

print("Data read. Building NLP...")

nlp = spacy.load("en_core_web_sm")
nlp.add_pipe("textrank")

print("NLP built.\n")

tqdm.pandas()

lemmatizer = WordNetLemmatizer()
stopwords = stopwords.words('english') + ["however"]
general_words = list(map(lambda s: s.lower(), calendar.month_name[1:])) + ["study", "introduction", "conclusion", \
                "correlation", "analysis", "efficacy", "result", "research", "people", "f-measure", "decrease", \
                "increase", "version", "clinical", "respect", ]

def text_clean_up(text: str):
    # ignoring text with digits
    if any(digit in text for digit in digits):
        return ""
    
    # treating text in lowercase
    text = text.lower()
    
    # removing non-letters
    text = re.sub('[^a-z]+', ' ', text)
    
    # removing extra spaces
    text = " ".join(text.split())

    spaces = text.count(" ")
    # single words are too general
    # and more than five words is too specific
    if not (1 <= spaces and spaces <= 4):
        return ""
    
    # lemmatizing words in text
    text = [lemmatizer.lemmatize(word) for word in word_tokenize(text)]

    # ignoring text if any stopword appears
    if any(word in text for word in stopwords):
        return ""
    
    # ignoring text if any general word appears
    if any(word in text for word in general_words):
        return ""

    text = " ".join(text)
    return text

def transform_abstract(abstract: list[str]):
    new_list = []
    for concept in abstract:
        new_concept = text_clean_up(concept)
        if new_concept and new_concept not in new_list:
            new_list += [new_concept]

    if new_list:
        return new_list
    else:
        return None

def process_abstract(abs):
    try:
        # obtaining list of concepts
        result = nlp(abs)
        result = [phrase.text for phrase in result._.phrases]
        # processing list
        result = transform_abstract(result)
    except:
        result = None

    return result

detect("test")

def check_language(abs):
    try:
        result = (detect(abs) == 'en')
    except:
        result = False

    return result

def thread_test(no, df):
    print(f"Thread #{no + 1}: {len(df)} abstracts")

    df["en"] = df["abstract"].progress_map(check_language) 
    df = df.loc[df["en"] == True, ["abstract", "year"]]

    print(f"Thread #{no + 1}: {len(df)} abstracts")

    df["abstract"] = df["abstract"].progress_map(process_abstract)

    df = df.dropna()

    #print(df)
    df.to_hdf(f"concepts/data_{no}.h5", key="data")


# make the "concepts" folder
if not os.path.exists("concepts"):
    os.mkdir("concepts")

# RUN_NO is the current run of the program
# THREAD_NO is the number of threads to use
# TOTAL_RUNS is the number of runs to split the data into 
# depending on the system resources, change THREAD_NO and TOTAL_RUNS accordingly
# if running on a cloud system with time limits, dont forget to adjust these values to avoid going over the limit
RUN_NO     = 1
THREAD_NO  = 10
TOTAL_RUNS = 4

# divided by no of threads in run, then no. of runs
chunk_size = len(data) // THREAD_NO // TOTAL_RUNS

threads = []
for i in range(THREAD_NO*(RUN_NO-1), THREAD_NO*RUN_NO):
    thread = Thread(target=thread_test, args=((i, data[chunk_size * i:chunk_size * (i + 1)])))
    thread.start()
    threads.append(thread)

for i in range(len(threads)):
    threads[i].join()

print("\nFinished.")



