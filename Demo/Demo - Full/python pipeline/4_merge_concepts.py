from threading import Thread
from tqdm import tqdm
from time import time
import pickle
import yaml
import re
import os

os.chdir("..")

def thread_merge(pos, names, regex_lists, new_data, max_hours):
    start = time()
    concepts = regex_lists[pos]

    new_concept = {"year": 3000, "count": 0, "recent": 0, "cooc": {}}
    new_data[names[pos]] = new_concept

    data = {}

    # loading concepts from files
    # keeping lowest year value
    # adding counts
    # adding cooc -> only counting merged concepts, under the new name
    for concept in tqdm(concepts, f"Merging '{names[pos]}'"):
        # more than max hours have passed -> break to avoid running out of time
        if max_hours and max_hours <= (time() - start) / 3600:
            print(f"'{names[pos]}' thread quitting early...")
            break

        letter = concept[0]
        
        # file for starting letter hasn't been added to data
        if letter not in data:
            data[letter] = pickle.load(open(f"split_concepts/{letter}.pkl", 'rb'))

        concept = data[letter][concept]
        new_concept["year"]    = min(new_concept["year"], concept["year"])
        new_concept["count"]  += concept["count"]
        new_concept["recent"] += concept["recent"]
        for other_concept in concept["cooc"]:
            concept_key   = None
            concept_value = concept["cooc"][other_concept]

            # searching for the merged concept
            for oth_pos in range(len(regex_lists)):
                if other_concept in regex_lists[oth_pos]:
                    # ignoring same position, aka same concept
                    if oth_pos != pos:
                        concept_key = names[oth_pos]
                    break

            # ignoring non-merged concepts
            if not concept_key:
                continue

            if concept_key in new_concept["cooc"]:
                new_concept["cooc"][concept_key] += concept_value
            else:
                new_concept["cooc"][concept_key] = concept_value


def merge_concepts(concept_list):
    merge_info = yaml.safe_load(open("merge.yaml"))
    
    names = list(merge_info["merges"].keys())
    regexes = list(merge_info["merges"].values())

    # each sublist represents a concept to be merged
    regex_lists = []
    for pos in tqdm(range(len(regexes)), "Creating merge lists"):
        pattern = re.compile(regexes[pos])
        # only adding the concepts that match the regex, and that aren't in previous merge list
        regex_list = [concept for concept in tqdm(concept_list, f"Creating list for '{names[pos]}'") if pattern.match(concept) and not any(concept in regex_list for regex_list in regex_lists)]

        regex_lists.append(regex_list)

    print()

    # ignoring merge if a concept has no found entries
    for pos in range(len(regex_lists)):
        if not regex_lists[pos]:
            print(f"No concepts found for '{regexes[pos]}'.")
            return

    concepts_count = ""
    for pos in range(len(regex_lists)):
        concepts_count += f"{len(regex_lists[pos])} concepts found for '{names[pos]}'.\n"

    print(f"{concepts_count}\n")

    filename_base = merge_info["filename"]
    filename = filename_base + ".yaml"

    if not os.path.exists(f"merged_concepts/{filename_base}"):
        os.mkdir(f"merged_concepts/{filename_base}")

    if filename not in os.listdir(f"merged_concepts/{filename_base}"):
        # if the filename is bad, resort to the first name of first concept
        try:
            open(f"merged_concepts/{filename_base}/{filename}", 'w')
        except:
            filename = regex_lists[0][0]

    else:
        filename_no = 0
        while filename in os.listdir(f"merged_concepts/{filename_base}"):
            filename = f'{filename_base}_{filename_no}.yaml'
            filename_no += 1

    # the maximum number of hours before threads stop merging and save whatever data that has already been collected
    max_hours = merge_info["max_hours"] if "max_hours" in merge_info else None

    print("Merging concepts:")
    new_data = {}
    threads = []
    for pos in range(len(regex_lists)):
        t = Thread(target=lambda: thread_merge(pos, names, regex_lists, new_data, max_hours))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    with open(f"merged_concepts/{filename_base}/{filename}", 'w', encoding='utf-8') as file:
        yaml.safe_dump(new_data, file, indent=4, sort_keys=False)

    print(f"\n\nConcept merge saved to merged_concepts/{filename_base}/{filename}.")


def main():
    if not os.path.exists("merged_concepts"):
        os.mkdir("merged_concepts")

    concept_list = pickle.load(open(f"split_concepts/concept_list.pkl", 'rb'))

    merge_concepts(concept_list)


if __name__=="__main__":
    main()
