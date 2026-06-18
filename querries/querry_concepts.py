from ConsoleListInterface import MenuInterface, waitForEnter
import matplotlib.pyplot as plt
from readchar import key
from tqdm import tqdm
import numpy as np
import matplotlib
import pickle
import yaml
import math
import re
import os

os.chdir("..")

font = {'size': 15}

matplotlib.rc('font', **font)


def trace_concept(regex, filename, concept_list):
    regex_list = [concept for concept in tqdm(concept_list, f"Creating list of concepts") if re.compile(regex).match(concept)]

    if not regex_list:
        print("No concepts found.\nPress enter to continue.")
        waitForEnter()
        return

    print(f"\n{len(regex_list)} concepts found.\n")

    data  = {}
    years = {}
    top   = {} # {concept: (count, year)} for top ten concepts (with highest counts) 
            
    last_concept = None # concept from top with least counts
    last_count   = None # count of concept from top with least counts
    last_year    = None # year of concept from top with least counts (for equal counts)
    for concept in tqdm(regex_list, "Processing concepts"):
        letter = concept[0]
        if letter not in data:
            data[letter] = pickle.load(open(f"split_concepts/{letter}.pkl", 'rb'))

        year = data[letter][concept]["year"]
        if year in years:
            years[year] += 1
        else:
            years[year] = 1

        count = data[letter][concept]["count"]
        # for the first ten concept processed
        if len(top) < 10:
            top[concept] = (count, year)
        else:
            # the concept after the first ten
            if not last_concept:
                min_concept  = min(top, key=top.get)
                last_concept = min_concept
                last_count = top[min_concept][0]
                last_year  = top[min_concept][1] 

            # the count of the current concept is either bigger than the lowest from top
            # or it's equal, but it appeared earlier
            if last_count < count or (last_count == count and last_year < year):
                # adding current concept
                top[concept] = (count, year)

                # removing lowest previous concept
                del top[last_concept]

                # recalculating lowest concept
                min_concept  = min(top, key=top.get)
                last_concept = min_concept
                last_count = top[min_concept][0]
                last_year  = top[min_concept][1] 

    # first, ordering by years (for equal counts)
    top = dict(sorted(top.items(), key=lambda item: item[1][1]))
    # then ordering by count
    top = dict(sorted(top.items(), key=lambda item: item[1][0], reverse=True))

    with open(f"querries/{filename}/{filename}.yaml", 'w', encoding='utf-8') as file:
        yaml.safe_dump(top, file, indent=4, sort_keys=False)

    print(f"\nTop concepts saved to 'querries/{filename}/{filename}.yaml'.")

    fig, ax = plt.subplots()

    fig.set_figwidth(16)
    fig.set_figheight(8)
    plt.margins(x=0.02, y=0.4)

    plt.scatter(years.keys(), years.values())

    plt.xlabel("Year")
    plt.ylabel("Count")
    plt.tick_params(axis='x', which='both', rotation=90)#, pad=20)
    plt.tight_layout()
    for xy in zip(years.keys(), years.values()):
        plt.annotate(f'{xy[0]}, {xy[1]}', xy=xy, rotation=90)

    y_ticks = ax.get_yticks()
    y_freq  = y_ticks[1] - y_ticks[0]
    # setting xticks for all years
    ax.set_xticks(np.arange(math.floor(ax.get_xlim()[0]), math.ceil(ax.get_xlim()[1]), 1))
    # setting bottom y at y frequency over four for better visibility 
    ax.set_ylim(bottom=-y_freq/4) 

    plt.savefig(f"querries/{filename}/{filename}.png")

    print(f"Year counts saved to 'querries/{filename}/{filename}.png'.\n\nPress enter to continue.")
    waitForEnter()


def main():
    concept_list = pickle.load(open(f"split_concepts/concept_list.pkl", 'rb'))

    menu = MenuInterface(yaml.safe_load(open("querries/menu.yaml")))

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
            if not regex or regex.isspace():
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

        # trace merged concept based on regex
        if path.startswith("Trace"):
            regex = menu.separateInteraction(function=lambda: input("Regex to search for: ").lower(), showCursor=True)
            if not regex or regex.isspace():
                continue
            try:
                pattern = re.compile(regex)
            except Exception as e:
                menu.separateInteraction(str(e).capitalize() + '\n')
                continue
            
            stop = False
            filename = menu.separateInteraction(function=lambda: input("Output folder name: ").lower(), showCursor=True)
            while True:
                # empty folder name cancels
                if not filename or filename.isspace():
                    stop = True
                    break

                # folder with that name already exists
                if filename in os.listdir("querries"):
                    filename = menu.separateInteraction(function=lambda: input("Name already used, try again: ").lower(), showCursor=True)
                    continue

                # checking that folder name is valid
                try:
                    os.mkdir("querries/" + filename)
                    break
                except:
                    filename = menu.separateInteraction(function=lambda: input("Invalid character in name, try again: ").lower(), showCursor=True)

            if stop:
                continue

            menu.separateInteraction(function=lambda: trace_concept(regex, filename, concept_list))


        if path in ["Exit", key.ESC, key.BACKSPACE]:
            menu.exitInterface()
            return
        

if __name__=="__main__":
    main()
