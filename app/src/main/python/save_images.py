import pandas as pd
from PIL import Image
import requests
import pickle
import os
dir_path = os.path.dirname(os.path.realpath(__file__))
scraped_csv = pd.read_csv(os.path.join(dir_path, "allrecipe-data.csv"))
scraped_csv.drop("Unnamed: 0", axis=1, inplace=True)
scraped_csv = scraped_csv.sample(frac=0.2, random_state=42)
with open(os.path.join(dir_path, "maincat2id.pkl"), "rb") as f:
    maincat2id = pickle.load(f)
with open(os.path.join(dir_path, "id2subcat2id.pkl"), "rb") as f:
    id2subcat2id = pickle.load(f)

image_dir = "dataset/images"
os.makedirs(image_dir, exist_ok=True)

for index, row in scraped_csv.iterrows():
    img_url =  row["Image URL"]
    response = requests.get(img_url)
    image_bytes = response.content
    with open(os.path.join(image_dir, f'{index}.png'), "wb") as f:
        f.write(image_bytes)

ntotal = len(scraped_csv)
ntrain = int(0.7*ntotal)
valstart = ntrain
nval = int(2/3*(ntotal-ntrain))
teststart = valstart+nval
ntest = ntotal-teststart
print(ntrain, nval, ntest)

for split in ["train", "val", "test"]:
    csv_path = os.path.join("dataset", f"{split}.csv")
    with open(csv_path, "w") as f:
        f.write("id,filename,maincat,subcat\n")
        for i, (index, r) in enumerate(scraped_csv.iterrows()):  # the index is not the same as i; index is the random sample df
            if split == "train":
                if i==valstart:
                    break
            elif split =="val":
                if i<valstart:
                    continue
                elif i==teststart:
                    break
            elif split == "test":
                if i<teststart:
                    continue
            maincatid = maincat2id[r['Main Category']]
            subcatid = id2subcat2id[maincatid][r["Subcategory"]]
            imgpath = os.path.join(image_dir, f'{index}.png')
            try:
                img = Image.open(imgpath)
            except FileNotFoundError:
                print(imgpath, "not found")
                continue
            f.write(f"{index},{imgpath},{maincatid},{subcatid}\n")