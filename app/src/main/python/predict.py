import torch
from torch import nn
import pretrainedmodels
from pretrainedmodels import utils
import argparse
import os
from pretrainedmodels_pytorch.examples.config import parser
from PIL import Image
import pickle
import random
import io
import base64
random.seed(42)
torch.manual_seed(42)

dir_path = os.path.dirname(os.path.realpath(__file__))
# dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "src/main/python")

with open(os.path.join(dir_path, "maincat2id.pkl"), "rb") as f:
    maincat2id = pickle.load(f)
print("MAINCAT2ID", maincat2id)
with open(os.path.join(dir_path, "id2subcat2id.pkl"), "rb") as f:
    id2subcat2id = pickle.load(f)

model_names = sorted(name for name in pretrainedmodels.__dict__
    if not name.startswith("__")
    and name.islower()
    and callable(pretrainedmodels.__dict__[name]))


def predict(inputs, **kwargs):
    print(f"INSIDE PREDICT {os.getcwd()}")
    print(f"INSIDE PREDICT 2 {dir_path}")
    print(f"INSIDE PREDICT 3 {kwargs}")
    print(f"INSIDE PREDICT 4 {kwargs.get('args')}")
    if kwargs.get("args"):
        args = kwargs.get("args")
    else: # default
        print("We are in the else block")
        args_custom = {
            "resume": os.path.join(dir_path, "model_best.pt"),
            "num_classes": 6,
            "knn_path": os.path.join(dir_path, "knns.pkl")
        }
        args = vars(parser.parse_args())
        args.update(args_custom)
        args = argparse.Namespace(**args)
    print(f"ARGS IS {args}")
    if not isinstance(inputs,list):
        args.inputs = [inputs]
    else:
        args.inputs = inputs

    # Pipeline part 1: CNN
    model = pretrainedmodels.__dict__[args.arch](num_classes = args.num_classes)
    # model = pretrainedmodels.__dict__[args.arch](num_classes = 1000)
    # new_last_linear = nn.Linear(model.last_linear.in_features, 6)
    # model.last_linear = new_last_linear

    print("Loading weights...")
    checkpoint = torch.load(args.resume, map_location="cpu")
    model_dict = model.state_dict()
    pretrained_dict = {}
    for k, v in checkpoint['state_dict'].items():
        if (k in model_dict and checkpoint['state_dict'][k].shape == model_dict[k].shape):
            pretrained_dict[k]=v
        else:
            print(f"{k} is not loaded")# overwrite entries in the existing state dict
    model_dict.update(pretrained_dict)
    # Get the input of the last linear layer (i.e. get the extracted features BEFORE they are passed in to the last layer, rather than the final predicted classes)
    model.eval()
    temp = model.last_linear

    # Pipeline part 2: kNN
    knns = pickle.load(open(args.knn_path, 'rb'))

    for inp in args.inputs:
        model.last_linear = temp
        if isinstance(inp, (bytes, bytearray)): # TODO no idea whats the diff between bytes and bytearray
            print("inp is not a PIL.Image, but a", type(inp), inp[:20])
            inp = base64.b64decode(inp)
            input_data = Image.open(io.BytesIO(inp))
        elif isinstance(inp, str): # path
            # Load and Transform one input image
            load_img = utils.LoadImage()
            input_data = load_img(inp) 
        elif isinstance(inp, type(Image)):
            input_data = inp 
        else:
            print("TYPE GOTTEN", type(inp))
            raise TypeError("Input to predict() can only be a string (image path) or bytestring (encoded image)")

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
        "resume": r"/Users/phoebezhouhuixin/Desktop/i2r_results/epochs100_lr0.001_20211029062326/model_best.pth",
        "num_classes": 6,
        "knn_path": r"logs/knn/20211108055850/knns.pkl"
    }
    args.update(args_custom)
    args = argparse.Namespace(**args)
    predict(inputs = ["dataset/images/2167.png"], args = args)