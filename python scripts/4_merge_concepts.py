from threading import Thread
from tqdm import tqdm
from time import time
import pickle
import yaml
import re
import os

os.chdir("..")

def thread_merge(pos, data, names, regex_lists, new_data):
    start = time()
    concepts = regex_lists[pos]

    new_concept = {"year": 3000, "count": 0, "cooc": {}}
    new_data[names[pos]] = new_concept

    # loading concepts from files
    # keeping lowest year value
    # adding counts
    # adding cooc -> only counting merged concepts, under the new name
    for concept in tqdm(concepts, f"Merging '{names[pos]}'"):
        # more than eleven hours have passed -> break to avoid running out of time
        if (time() - start) // 3600 == 11:
            print(f"'{names[pos]}' thread quitting early...")
            break

        letter = concept[0]
        # concepts that don't start with a letter (hopefully fixed)
        try:
            data[letter] = pickle.load(open(f"split_concepts/{letter}.pkl", 'rb'))
        except:
            pass

        # ignoring if it doesn't start with a letter
        if letter not in data:
            continue

        concept = data[letter][concept]
        new_concept["year"]   = min(new_concept["year"], concept["year"])
        new_concept["count"] += concept["count"]
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


def merge_concepts(data, concept_list):
    merge_info = yaml.safe_load(open("merge.yaml"))

    print(merge_info)

    names = list(merge_info["merges"].keys())
    regexes = list(merge_info["merges"].values())

    # each sublist represents a concept to be merged
    regex_lists = []
    for pos in tqdm(range(len(regexes)), "Creating merge lists"):
        # only adding the concepts that match the regex, and that aren't in previous merge list
        regex_list = [concept for concept in tqdm(concept_list, f"Creating list for '{names[pos]}'") if re.compile(regexes[pos]).match(concept) and not any(concept in regex_list for regex_list in regex_lists)]

        # limting merge lists
        if "limit" in merge_info:
            regex_list = regex_list[:merge_info["limit"]]

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
    if filename not in os.listdir("merged_concepts"):
        # if the filename is bad, resort to the fir`st name of first concept
        try:
            open(f"merged_concepts/{filename}", 'w')
        except:
            filename = regex_lists[0][0]

    else:
        filename_no = 0
        while filename in os.listdir("merged_concepts"):
            filename = f'{filename_base}_{filename_no}.yaml'
            filename_no += 1

    print("Merging concepts:")
    new_data = {}
    threads = []
    for pos in range(len(regex_lists)):
        t = Thread(target=lambda: thread_merge(pos, data, names, regex_lists, new_data))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    with open(f"merged_concepts/{filename}", 'w', encoding='utf-8') as file:
        yaml.safe_dump(new_data, file, indent=4, sort_keys=False)

    print(f"\n\nConcept merge saved to merged_concepts/{filename}.")


def main():
    concept_list = pickle.load(open(f"split_concepts/concept_list.pkl", 'rb'))

    data = {}
    merge_concepts(data, concept_list)


if __name__=="__main__":
    main()
