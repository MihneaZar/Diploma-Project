from timeit import default_timer as timer
from threading import Thread
from time import sleep
from tqdm import tqdm
import pickle
import string
import os

os.chdir("..")

def time_counter(start, stop, message):
    while True:
        if stop():
            return

        print(f'{message}: {int(timer()) - start:{"0"}>2}s', end='\r')
        sleep(1)


def main():
    start = int(timer())

    stop = False
    t = Thread(target=lambda: time_counter(start, lambda: stop, "Loading data"))
    t.start()
    data = pickle.load(open("concept_data.pkl", 'rb'))
    stop = True
    t.join()

    print("\nData loaded.\n")

    stop = False
    t = Thread(target=lambda: time_counter(start, lambda: stop, "Saving concept list"))
    t.start()
    with open("split_concepts/concept_list.pkl", 'wb') as file:
        pickle.dump(list(data.keys()), file)
    stop = True
    t.join()

    for letter in tqdm(string.ascii_lowercase, "Saving concepts by letter"):
        letter_data = {k: v for k, v in data.items() if k.startswith(letter)}
        with open(f"split_concepts/{letter}.pkl", 'wb') as file:
            pickle.dump(letter_data, file)


if __name__=="__main__":
    main()
