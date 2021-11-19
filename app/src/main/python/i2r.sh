sudo apt-get update
# sudo apt-get install -y libsm6 libxext6 libxrender-dev libglib2.0-0
# sudo pip install opencv-contrib-python-headless
sudo docker run --gpus device=1 --ipc=host -it \
-v /home/phoebezhou/ImageToRecipeV2:/ImageToRecipeV2 \
-v /home/phoebezhou/i2r:/dataset \
-v /home/phoebezhou/ImageToRecipeV2/logs/train/epochs100_lr0.001_20211029062326:/weights \
phoebezhouhuixin/i2r
# cd ImageToRecipeV2/pretrainedmodels_pytorch
# pip install -e . (install in editable mode)
# python ImageToRecipeV2/save_images.py
# python ImageToRecipeV2/main.py


