# Image-Version
## Set Up
Download [removed_duplicate_recipes.json](https://drive.google.com/file/d/1ayFz3DI2KEFhMt7tC7aD9GaoMI-bHKW-/view?usp=sharing), [cnn_knn_model_small_threshold.tflite](https://drive.google.com/file/d/1K8zW266yoBEBenG6GxvdnnyaBwM9GGej/view?usp=sharing) and [labels.txt](https://drive.google.com/file/d/15AZ73I8yAIQ01qTu3GEH48CC6utGOBSC/view?usp=sharing) then place them in [app/src/main/python](app/src/main/python)
## Run
Firstly, run the server on your terminal with

`cd app/src/main/python`

`python server.py`

Next, launch the app in Android Studio by running the MainActivity.kt file
## ML Models
1. Recipe data is scraped from [allrecipes](https://www.allrecipes.com/) with this [code](https://drive.google.com/file/d/1uKGrzM9YC1z3qHdIOVu0ejPggSrbR0Yq/view?usp=sharing)
2. Xception model is fine-tuned on the images scraped from allrecipes using this [code](https://drive.google.com/file/d/1M3igoYXI39zpPA8Ekj4wrwfNEPoTe9kf/view?usp=sharing)
3. This [code](https://www.kaggle.com/carlosmiao/cz4125) uses features from trained Xception model to conduct KNN to find similar images to uploaded image and saves as a tflite model

