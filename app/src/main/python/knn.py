import pandas as pd
# from sklearn.model_selection import train_test_split 
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import GridSearchCV
from torchvision import transforms
import time
import pickle
import numpy as np
from PIL import Image
import io
import argparse
import os
import datetime
def main(args):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(dir_path, "maincat2id.pkl"), "rb") as f:
        maincat2id = pickle.load(f)

    if args.train:
        train_df = pd.read_csv(os.path.join(args.data, "train.csv"))
        test_df = pd.read_csv(os.path.join(args.data, "val.csv"))
        test_df = pd.concat([test_df, pd.read_csv(os.path.join(args.data, "test.csv"))], axis = 0) # use both csv for testing since validation 
        
        knns = {}
        for mc in maincat2id.values():
            print("MAIN CAT", mc)
            img_arrays = None
            for i, train_line in train_df[train_df.maincat == mc].iterrows():
                _id = train_line.id
                # print(_id)
                try:
                    with open(os.path.join(args.data, "extracted", f"{_id}.pkl"), "rb") as f:
                        feats = pickle.load(f)
                    # print(type(feats), feats.size()) # torch.Tensor, torch.Size([1,1056])
                    if img_arrays is None:
                        img_arrays = feats.detach().numpy()
                        labels = [int(train_line.subcat)]
                    else:
                        img_arrays = np.concatenate([img_arrays, feats.detach().numpy()], axis = 0)
                        labels.append(int(train_line.subcat))
                except Exception as e:
                    print(e)
        
            print("Training...", len(img_arrays),len(labels))
            # TODO: Apply PCA to reduce features?

            # parameters = {"n_neighbours":[2,3,4,5]}
            knn = KNeighborsClassifier(n_neighbors= min(len(train_df[train_df.maincat == mc].subcat.unique()), 4))
            # clf = GridSearchCV(knn, parameters, refit = True, scoring= "f1", cv = min(len(labels), 5)) #scoring="accuracy"
            knn.fit(img_arrays, labels)
            # results_df = pd.DataFrame(clf.cv_results_)
            # results_df.to_csv(os.path.join(args.logdir, f"knn{mc}.csv"))
            
            img_arrays_test = None
            for i, test_line in test_df[test_df.maincat == mc].iterrows():
                _id = test_line.id
                # print(_id)
                try:
                    with open(os.path.join(args.data, "extracted", f"{_id}.pkl"), "rb") as f:
                        feats = pickle.load(f)
                    if img_arrays_test is None:
                        img_arrays_test = feats.detach().numpy()
                        labels_test = [int(test_line.subcat)]
                    else:
                        img_arrays_test = np.concatenate([img_arrays_test, feats.detach().numpy()], axis = 0)
                        labels_test.append(int(test_line.subcat))
                except Exception as e:
                    print(e)

            print("Testing after training...", len(test_df),  len(img_arrays_test),len(labels_test))
            # based on the training dataset, our model predicts the following for the test set:
            print("Test set score for main cat {} ({}): {:.2f}".format(mc,list(maincat2id.keys())[mc], knn.score(img_arrays_test, labels_test)))
            knns[mc] = knn#clf.best_estimator_
        args.knn_path = os.path.join(args.logdir, "knns.pkl")
        with open(args.knn_path, "wb") as f:
            pickle.dump(knns, f)
        args.train = False

    if not args.train:
        test_df = pd.read_csv(os.path.join(args.data, "val.csv"))
        test_df = pd.concat([test_df, pd.read_csv(os.path.join(args.data, "test.csv"))], axis = 0) # use both csv for testing since validation 
        
        with open(args.knn_path, "rb") as f:
            knns = pickle.load(f)

        scores = {}
        for i, mc in enumerate(maincat2id.values()):
            img_arrays_test = None
            for i, test_line in test_df[test_df.maincat == mc].iterrows():
                _id = test_line.id
                # print(_id)
                try:
                    with open(os.path.join(args.data, "extracted", f"{_id}.pkl"), "rb") as f:
                        feats = pickle.load(f)
                    if img_arrays_test is None:
                        img_arrays_test = feats.detach().numpy()
                        labels_test = [int(test_line.subcat)]
                    else:
                        img_arrays_test = np.concatenate([img_arrays_test, feats.detach().numpy()], axis = 0)
                        labels_test.append(int(test_line.subcat))
                except Exception as e:
                    print(e)

            score = knns[mc].score(img_arrays_test, labels_test)
            print("Test set score for main cat {} ({}): {:.2f}".format(mc,list(maincat2id.keys())[mc], knn.score(img_arrays_test, labels_test)))
            scores[mc] = score
        with open(os.path.join(args.logdir, "scores.pkl"), "wb") as f:
            pickle.dump(scores, f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    args = vars(parser.parse_args())
    args_custom = {
        "data": "dataset",
        "train": True,
        "logdir":  os.path.join(os.path.dirname(os.path.realpath(__file__)), "logs", "knn", datetime.datetime.now().strftime('%Y%m%d%H%M%S')),
        # "resume": r"/Users/phoebezhouhuixin/Desktop/i2r_results/epochs100_lr0.001_20211029062326/model_best.pth",
        "resume":r"/weights/model_best.pt"
    }
    args.update(args_custom)
    args = argparse.Namespace(**args)
    os.makedirs(args.logdir)
    print("LEN", len(os.listdir("dataset/extracted")), len(os.listdir("dataset/images")))
    main(args)