import pandas as pd
from tqdm import tqdm
import os
import pickle
from random import sample

os.chdir("..")

folder = "concepts"

data = {}

def process_row(row):
    already_done = []
    for abs in row["abstract"]:
        if abs in already_done:
            continue
        already_done += [abs]
        if abs not in data:
            data[abs] = {}
            data[abs]["year"] = row["year"]
            data[abs]["count"] = 1
            data[abs]["cooc"] = {}
        else:
            data[abs]["year"] = min(data[abs]["year"], row["year"])
            data[abs]["count"] += 1

        for othabs in [a for a in row["abstract"] if a != abs]:
            if othabs in data[abs]["cooc"]:
                data[abs]["cooc"][othabs] += 1
            else:
                data[abs]["cooc"][othabs] = 1


tqdm.pandas()
print([file for file in os.listdir(folder) if file.startswith("data")])
for file in tqdm([file for file in os.listdir(folder) if file.startswith("data")]):
    df = pd.read_hdf(f"{folder}/{file}", key="data")
    df.progress_apply(process_row, axis=1)

with open("concept_data.pkl", 'wb') as file:
    pickle.dump(data, file)

for concept in sample(list(data), 20):
    print(concept + ":")
    print(data[concept])

print(f'No. of concepts: {len(data)}')
