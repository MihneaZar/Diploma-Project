import pandas as pd
from tqdm import tqdm
import os
import pickle
from random import sample

os.chdir("..")

# using the actual concepts folder, not the demo one
# for more data
folder = "../../concepts"

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
            data[abs]["recent"] = 1 if 2013 <= row["year"] else 0
            data[abs]["cooc"] = {}
        else:
            data[abs]["year"] = min(data[abs]["year"], row["year"])
            data[abs]["count"] += 1
            data[abs]["recent"] += 1 if 2013 <= row["year"] else 0

        for othabs in [a for a in row["abstract"] if a != abs]:
            if othabs in data[abs]["cooc"]:
                data[abs]["cooc"][othabs] += 1
            else:
                data[abs]["cooc"][othabs] = 1


tqdm.pandas()
# print([file for file in os.listdir(folder) if file.startswith("data")])
for file in tqdm([file for file in os.listdir(folder) if file.startswith("data")][:8], desc="Processing HDF files"):
    df = pd.read_hdf(f"{folder}/{file}", key="data")
    df.progress_apply(process_row, axis=1)

with open("concept_data.pkl", 'wb') as file:
    pickle.dump(data, file)

print()
print("machine learning:")
ml_data = data["machine learning"]
print(f"\tyear: {ml_data['year']}")
print(f"\tcount: {ml_data['count']}")
print(f"\tco-occurence:")
for conc in ml_data['cooc']:
    if 10 <= ml_data['cooc'][conc]:
        print(f"\t\t{conc}: {ml_data['cooc'][conc]}")
print()

print(f'No. of concepts: {len(data)}')
