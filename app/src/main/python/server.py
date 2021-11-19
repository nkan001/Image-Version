import os
import sys
sys.path.insert(1, os.getcwd())
sys.path.insert(1, os.path.join(os.getcwd(), "pretrainedmodels_pytorch"))
import argparse
from flask import Flask, jsonify, request
from pretrainedmodels_pytorch.examples.config import parser
from predict import predict
from predict_tensorflowlite import predictTensorflowLite
import requests
from PIL import Image
import io
import json
import pickle
app = Flask(__name__)

dir_path = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(dir_path, "maincat2id.pkl"), "rb") as f:
    maincat2id = pickle.load(f)
with open(os.path.join(dir_path, "id2subcat2id.pkl"), "rb") as f:
    id2subcat2id = pickle.load(f)

@app.route('/predict', methods=['POST'])
def predict_request():
    print("Called predict_request")
    if request.method == 'POST':
        # we will get the file from the request
        print("REQUEST ARGS IS", request.args)
        print("REQUEST FROM IS", request.form)
        print("REQUEST DATA IS", type(request.data))
        print("REQUEST FILES IS", request.files)
        print("REQUEST JSON IS", request.json)
        # https://stackoverflow.com/questions/10434599/get-the-data-received-in-a-flask-request
        img_bytes = request.data

        print("IMG_BYTES", len(img_bytes), type(img_bytes))
        json_path = os.path.join(dir_path, "removed_duplicate_recipes.json")
        with open(json_path, "r") as f:
            allrecipes =json.load(f)
        if len(img_bytes)==0:
            cleanedRecipes = [x for x in allrecipes["recipes"] if type(x["ratings"])!=str]
            sortedrecipes = sorted(cleanedRecipes, key=lambda x: float(x["ratings"])*float(x["rating_counts"]), reverse=True)
            return jsonify({"recipes":sortedrecipes[:100]})
        else:
            recipeURLS = predictTensorflowLite(img_bytes)
            output = []
            for recipeurl in recipeURLS:
                for rec in allrecipes["recipes"]:
                    if recipeurl == rec["url"]:
                        if type(rec["ratings"]) == str:
                            rec["ratings"] = 0
                        output.append(rec)
                        break
            print(output)
            # maincat_id, maincat_name, subcat_id, subcat_name = predict(img_bytes)
            # return jsonify({
            #     'maincat_id': maincat_id, 'maincat_name': maincat_name,
            #     'subcat_id': subcat_id, 'subcat_name': subcat_name,
            # })
            
            # output = [{k:v for k,v in x.items()} for x in allrecipes["recipes"] if x["main_cat"]==maincat_name and x["sub_cat"]==subcat_name]
            return jsonify({"recipes":output})



@app.route('/', methods = ["GET"])
def send_request():
    img = Image.open(os.path.join(dir_path, "dataset/images/2167.png"))
    output = io.BytesIO()
    img.save(output, format = "png")
    imgString = output.getvalue()

    # payload = {"data":imgString}
    resp = requests.post("http://0.0.0.0:5000/predict", data = imgString)# files={"file": open("dataset/images/2167.png", "rb")}
    print(resp.json())
    return resp.json()


# running web app in local machine
if __name__ == '__main__':
    app.run(host = "0.0.0.0", debug=True)

