from ConsoleListInterface import MenuInterface, waitForEnter
import matplotlib.pyplot as plt
from readchar import key
from tqdm import tqdm
import pandas as pd
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
    pattern = re.compile(regex)
    regex_list = [concept for concept in tqdm(concept_list, f"Creating list of concepts") if pattern.match(concept)]

    if not regex_list:
        print("No concepts found.\nPress enter to continue.")
        waitForEnter()
        return

    print(f"\n{len(regex_list)} concepts found.\n")

    try:
        df = pd.read_hdf("other_data/years.h5", key="concept")
    except:
        df = None

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
            years[year]  = 1

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

    # applying title() to concept names
    top = {concept.title(): top[concept] for concept in top}

    # first, ordering by years (for equal counts)
    top = dict(sorted(top.items(), key=lambda item: item[1][1]))
    # then ordering by count
    top = dict(sorted(top.items(), key=lambda item: item[1][0], reverse=True))

    with open(f"querries/{filename}/{filename}.yaml", 'w', encoding='utf-8') as file:
        yaml.safe_dump(top, file, indent=4, sort_keys=False)

    print(f"\nTop concepts saved to 'querries/{filename}/{filename}.yaml'.")

    if df is not None:
        # not enough data in these years
        for year in [1951, 1952]:
            if year in years:
                del year[years]

        for year in years:
            try:
                # * 100 => this value is in percentage points
                years[year] = years[year] * 100 / df['count'].loc[year]
            except:
                del years[year]

    fig, ax = plt.subplots()

    fig.set_figwidth(16)
    fig.set_figheight(8)
    plt.margins(x=0.02, y=0.5)

    plt.scatter(years.keys(), years.values())

    plt.xlabel("Year")
    plt.tick_params(axis='x', which='both', rotation=90)#, pad=20)
    plt.tight_layout()

    if df is None:
        plt.ylabel("Count")
        for xy in zip(years.keys(), years.values()):
            plt.annotate(f'{xy[0]}, {xy[1]}', xy=xy, rotation=90)
        # setting bottom y at y frequency over four for better visibility 
        ax.set_ylim(bottom=-y_freq/4) 
        
    else:
        plt.ylabel("log-10 % of total new concepts")
        for xy in zip(years.keys(), years.values()):
            plt.annotate(f'{xy[0]}, {math.log(xy[1], 10):.2f}', xy=xy, rotation=90)
        ax.set_yscale('log', base=10)

    y_ticks = ax.get_yticks()
    y_freq  = y_ticks[1] - y_ticks[0]
    # setting xticks for all years
    ax.set_xticks(np.arange(math.floor(ax.get_xlim()[0]), math.ceil(ax.get_xlim()[1]), 1))

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
            concepts = menu.separateInteraction(function=lambda: input("Type concepts, separated by comma (add ':{number}' to limit co-occurences): ").lower(), showCursor=True)
            if not concepts or concepts.isspace():
                continue
            concepts = [concept.strip() for concept in concepts.split(",")]
            print_text = "\n"
            for concept in concepts:
                limit   = int(concept[concept.find(':') + 1:].strip()) if (':' in concept and concept[concept.find(':') + 1:].strip().isdigit()) else None
                concept = concept[:concept.find(':')].strip() if ':' in concept else concept
                letter = concept[0]
                if letter not in data:
                    # concepts that don't start with a letter (hopefully fixed)
                    try:
                        data[letter] = pickle.load(open(f"split_concepts/{letter}.pkl", 'rb'))
                    except:
                        pass

                if letter in data and concept in data[letter]:
                    concept_data = data[letter][concept]

                    print_text += f"{concept.title()}:\n"
                    print_text += f"\tYear: {concept_data['year']}\n"
                    print_text += f"\tCount: {concept_data['count']}\n"
                    print_text += f"\tCo-occurences:\n"

                    if not limit:
                        limit = len(concept_data['cooc'])
                    
                    # copying them manually to avoid changing origin
                    cooc = {c: concept_data['cooc'][c] for c in concept_data['cooc']}
                    cooc = dict(sorted(cooc.items(), key=lambda item: item[1], reverse=True))
                    for other_concept in cooc:
                        # the first {number} co-occurences have been added
                        if limit == 0:
                            break
                        limit -= 1
                        print_text += f"\t\t{other_concept.title()}: {concept_data['cooc'][other_concept]}\n"

                else:
                    print_text += f"{concept.title()} not found.\n"

            menu.separateInteraction(print_text, startAtTop=True)

        # trace merged concept based on regex
        if path.startswith("Trace"):
            regex = menu.separateInteraction(function=lambda: input("Regex of concept to trace: ").lower(), showCursor=True)
            if not regex or regex.isspace():
                continue
            try:
                pattern = re.compile(regex)
            except Exception as e:
                menu.separateInteraction(str(e).capitalize() + '\n')
                continue
            
            stop = False
            filename = menu.separateInteraction(function=lambda: input("Output folder name: "), showCursor=True)
            while True:
                # empty folder name cancels
                if not filename or filename.isspace():
                    stop = True
                    break

                # folder with that name already exists
                if filename in os.listdir("querries"):
                    filename = menu.separateInteraction(function=lambda: input("Name already used, try again: "), showCursor=True)
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
