from ConsoleListInterface import MenuInterface, waitForEnter
from threading import Thread
from readchar import key
from tqdm import tqdm
import pickle
import cursor
import yaml
import re
import os

os.chdir("..")

def main():
    concept_list = pickle.load(open(f"split_concepts/concept_list.pkl", 'rb'))

    menu = MenuInterface(yaml.safe_load(open("menu.yaml")))

    data = {}
    while True:
        path = menu.interactWithMenu()

        # ignoring backspace to main menu
        if not path:
            continue

        path = path[0]

        # find concepts based on regex
        if path.startswith("Search"):
            regex = menu.separateInteraction(function=lambda: input("Regex to search for: ").lower(), showCursor=True)
            if not regex:
                continue
            try:
                pattern = re.compile(regex)
            except Exception as e:
                menu.separateInteraction(str(e).capitalize() + '\n')
                continue
            regex_list = [concept for concept in concept_list if pattern.match(concept)]
            no_of_concepts = len(regex_list)
            if no_of_concepts == 0:
                menu.separateInteraction("No concepts found.\n")
                continue
            regex_list = "\n".join(regex_list)
            menu.separateInteraction(f"Concepts ({no_of_concepts}):\n\n{regex_list}\n", startAtTop=True)

        # get concept entries based on complete name
        if path.startswith("Get"):
            concepts = menu.separateInteraction(function=lambda: input("Type concepts, separated by comma: ").lower(), showCursor=True)
            if not concepts or concepts.isspace():
                continue
            concepts = [concept.strip() for concept in concepts.split(",")]
            print_text = "\n"
            for concept in concepts:
                letter = concept[0]
                if letter not in data:
                    # concepts that don't start with a letter (hopefully fixed)
                    try:
                        data[letter] = pickle.load(open(f"split_concepts/{letter}.pkl", 'rb'))
                    except:
                        pass

                if letter in data and concept in data[letter]:
                    print_text += f"{concept.capitalize()}:\n"
                    print_text += str(data[letter][concept]) + '\n'

                else:
                    print_text += f"{concept.capitalize()} not found.\n"

            menu.separateInteraction(print_text, startAtTop=True)


        if path in ["Exit", key.ESC, key.BACKSPACE]:
            menu.exitInterface()
            return
        

if __name__=="__main__":
    main()
