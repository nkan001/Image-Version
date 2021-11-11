import torch
import pretrainedmodels
from pretrainedmodels import utils
import argparse
import os
import pickle
from pretrainedmodels_pytorch.examples.config import parser
from PIL import Image
import numpy as np
import pickle
import random
import io
import json
import base64
from types import SimpleNamespace
random.seed(42)
torch.manual_seed(42)

dir_path = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(dir_path, "maincat2id.pkl"), "rb") as f:
    maincat2id = pickle.load(f)
with open(os.path.join(dir_path, "id2subcat2id.pkl"), "rb") as f:
    id2subcat2id = pickle.load(f)

model_names = sorted(name for name in pretrainedmodels.__dict__
    if not name.startswith("__")
    and name.islower()
    and callable(pretrainedmodels.__dict__[name]))

def predict(args):
    print("INSIDE PREDICT", os.getcwd(), dir_path)
    if type(args)!=argparse.Namespace:
        try: # string
            args = json.loads(args, object_hook = lambda d: SimpleNamespace(**d))
        except Exception as e:
            print(e)

    # Pipeline part 1: CNN
    model = pretrainedmodels.__dict__[args.arch](num_classes = args.num_classes)
    if os.path.exists(args.resume):
        print("Loading weights...")
        checkpoint = torch.load(args.resume, map_location="cpu")
        model_dict = model.state_dict()
        pretrained_dict = {k: v for k, v in checkpoint['state_dict'].items() if (k in model_dict and checkpoint['state_dict'][k].shape == model_dict[k].shape)}
        # overwrite entries in the existing state dict
        model_dict.update(pretrained_dict)
        # Get the input of the last linear layer (i.e. get the extracted features BEFORE they are passed in to the last layer, rather than the final predicted classes)
        temp = model.last_linear
    model.eval()

    # Pipeline part 2: kNN
    knns = pickle.load(open(args.knn_path, 'rb'))

    for inp in args.inputs:
        model.last_linear = temp
        if isinstance(inp, (bytes, bytearray)):
            print("inp is not a PIL.Image, but a", type(inp))
            input_data = Image.open(io.BytesIO(inp))
        elif isinstance(inp, str): # path
            # Load and Transform one input image
            load_img = utils.LoadImage()
            input_data = load_img(inp) 
        elif isinstance(inp, Image):
            input_data = inp 
        else:
            print("Running the else block, inp is a", type(inp))
            try:
                input_data = Image.open(io.BytesIO(inp))
                print("Success")
            except Exception as e:
                print(e)

        tf_img = utils.TransformImage(model)
        # print("step 1 shape", type(input_data))
        input_data = tf_img(input_data)  
        # print("step 2 shape", type(input_data), input_data.size()) # [3, 224, 224]
        input_data = input_data.unsqueeze(0) # new axis for batch size
        # print("step 3 shape", type(input_data), input_data.size()) # [1, 3, 224, 224]
        input = torch.autograd.Variable(input_data)
        # print("step 4 shape", type(input), input_data.size()) # [1, 3, 224, 224]

        with torch.no_grad():
            output = model(input)
            # print("OUTPUT SIZE", output.size()) # [1, 6]
            output = model(input)
            print(output.data.squeeze())
            maxval, argmax = output.data.squeeze().max(0)
            print(maxval, argmax)
            maincat_id = argmax.item()
            maincat_name = list(maincat2id.keys())[maincat_id]
            model.last_linear = utils.Identity()#pretrainedmodels.utils.Identity()   
            hidden = model(input)
            print(hidden.size())
        subcat_id = knns[maincat_id].predict(hidden).item() # p array
        proba = knns[maincat_id].predict_proba(hidden)
        print(subcat_id, proba)
        subcat_name = list(id2subcat2id[maincat_id].keys())[subcat_id]
        print("Predicted subcat:", subcat_name, "is a", maincat_name)
        return maincat_id, maincat_name, subcat_id, subcat_name
if __name__ == "__main__":
    args = vars(parser.parse_args())
    img = Image.open("dataset/images/2167.png")
    output = io.BytesIO()
    img.save(output, format = "png")
    imgString = output.getvalue()
    args_custom = {
        # "inputs": ["dataset/images/2167.png"],
        "inputs": [imgString],
        "resume": r"/Users/phoebezhouhuixin/Desktop/i2r_results/epochs100_lr0.001_20211029062326/model_best.pth",
        "num_classes": 6,
        "knn_path": r"logs/knn/20211108055850/knns.pkl"
    }
    args.update(args_custom)
    args = argparse.Namespace(**args)
    predict(args)