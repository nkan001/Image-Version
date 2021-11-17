import os
import sys
sys.path.insert(1, os.getcwd())
import argparse
from flask import Flask, jsonify, request
from pretrainedmodels_pytorch.examples.config import parser
from predict import predict
import requests
from PIL import Image
import io
import json
app = Flask(__name__)


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
        args = vars(parser.parse_args())
        args_custom = {
            "resume": r"/Users/phoebezhouhuixin/Desktop/i2r_results/epochs100_lr0.001_20211029062326/model_best.pth",
            "num_classes": 6,
            "knn_path": r"./logs/knn/20211108055850/knns.pkl"
        }
        args.update(args_custom)
        args = argparse.Namespace(**args)
        maincat_id, maincat_name, subcat_id, subcat_name = predict(img_bytes, args = args)
        return jsonify({
            'maincat_id': maincat_id, 'maincat_name': maincat_name,
            'subcat_id': subcat_id, 'subcat_name': subcat_name,
        })
@app.route('/', methods = ["GET"])
def send_request():
    img = Image.open("dataset/images/2167.png")
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

