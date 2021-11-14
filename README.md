# Set Up
1. Download [xception.tflite](https://drive.google.com/file/d/1J45qS-IOX2E5kV8l5wDYbdYDWsi1nnwf/view?usp=sharing) and [cnn_knn_model_small.tflite](https://drive.google.com/file/d/1w0YvuaSxTNRZW2IpwMKNFFBJsdRWYEjg/view?usp=sharing) add to [app/src/main/ml](app/src/main/ml)
2. Download [all_recipes.json](https://drive.google.com/file/d/1KGTEYq98SGFnKu_3lyW8RaXezxind0BW/view?usp=sharing) and [labels.txt](https://drive.google.com/file/d/15AZ73I8yAIQ01qTu3GEH48CC6utGOBSC/view?usp=sharing) add to [app/src/main/assets](app/src/main/assets)

# ML Models
1. Recipe data is scraped from [allrecipes](https://www.allrecipes.com/) with this [code](https://drive.google.com/file/d/1uKGrzM9YC1z3qHdIOVu0ejPggSrbR0Yq/view?usp=sharing)
2. Xception model is fine-tuned on the images scraped from allrecipes using this [code](https://drive.google.com/file/d/1M3igoYXI39zpPA8Ekj4wrwfNEPoTe9kf/view?usp=sharing)
3. This [code](https://www.kaggle.com/carlosmiao/cz4125) uses features from trained Xception model to conduct KNN to find similar images to uploaded image and saves as a tflite model
