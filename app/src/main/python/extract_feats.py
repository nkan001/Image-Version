import torch
import torchvision.datasets as datasets
import pretrainedmodels
from pretrainedmodels import utils
from recipedataset import RecipeDataset
import argparse
import os
import pickle
from pretrainedmodels_pytorch.examples.config import parser
import shutil
import random
random.seed(42)
torch.manual_seed(42)
model_names = sorted(name for name in pretrainedmodels.__dict__
        if not name.startswith("__")
        and name.islower()
        and callable(pretrainedmodels.__dict__[name]))

def main(args):    
    model = pretrainedmodels.__dict__[args.arch](num_classes = args.num_classes)
    assert os.path.exists(args.resume)
    print("Loading weights...")
    checkpoint = torch.load(args.resume, map_location="cpu")
    model_dict = model.state_dict()
    pretrained_dict = {k: v for k, v in checkpoint['state_dict'].items() if (k in model_dict and checkpoint['state_dict'][k].shape == model_dict[k].shape)}
    # overwrite entries in the existing state dict
    model_dict.update(pretrained_dict)
    # Get the input of the last linear layer (i.e. get the extracted features BEFORE they are passed in to the last layer, rather than the final predicted classes)
    model.last_linear = utils.Identity()#pretrainedmodels.utils.Identity()
    model.eval()

    extracted_path = os.path.join(args.data, "extracted")
    if os.path.exists(extracted_path):
        shutil.rmtree(extracted_path)
    os.makedirs(extracted_path, exist_ok=False)
    
    with torch.no_grad():
        for split in ["train", "val", "test"]:
            dataset = RecipeDataset(image_size=args.image_size,  data_dir = args.data, name=split)
            loader = torch.utils.data.DataLoader(dataset=dataset, batch_size=1, shuffle=False, num_workers=0)
            for i, (img, label, _id) in enumerate(loader):
                print("Input", type(img), img.size(), type(label), label.size(), type(_id), _id.size())
                feats = model(img)
                print("Output", type(feats), feats.size())
                # feats = feats.byte() # TODO not sure what format to store this in 
                # query = {"_id": _id}
                # newvalues = {"$set":{"extracted": feats}}
                # scraped_collection.update_one(query, newvalues)
                with open(os.path.join(extracted_path, f"{_id.item()}.pkl"), "wb") as f:
                    pickle.dump(feats, f)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--arch', '-a', metavar='ARCH', default='nasnetamobile', choices=model_names, help='model architecture: ' +' | '.join(model_names) +' (default: nasnetamobile)')
    parser.add_argument('-n', '--num_classes', default=1000, type=int, help='number of classes to predict')
    parser.add_argument('--image_size', default=224, type=int, help='model input size (default for nasnet mobile: 224)')
    parser.add_argument("--resume", type=str, help="path to model weights that will be used without the last layer to extract the features")
    parser.add_argument('--data', metavar='DIR', help='path to dataset')
    # WEIGHTS_PATH = r"/Users/phoebezhouhuixin/Desktop/i2r_results/epochs100_lr0.001_20211029062326/model_best.pth"
    args = vars(parser.parse_args())
    args_custom = {
        "data":"dataset",
        "resume": "/weights/model_best.pth",#WEIGHTS_PATH,
        "num_classes": 6,
    }
    args.update(args_custom)
    args = argparse.Namespace(**args)
    main(args)
