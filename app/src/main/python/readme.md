STEPS
* scrape.ipynb: get all recipes in csv
* save_images.py: creates the dataset by saving (a subset) of images, main cat labels and sub cat labels from abovementioned csv to local directory
* recipedataset.py: torch.utils.data.Dataset to load the data for the NasNet model
* main.py: train NasNet to classify main cat labels (train, val and test dataset are on local directory, due to save_images.py)
* extract_feats.py: use trained NasNet to extract features and store in the same directory as the respective image
* knn.py: train and test 6 different KNNs, to classify sub cats of each of the 6 main cats
* predict.py: image inference pipeline combining CNN and kNN
* put the pipeline in flutter: IN PROGRESS