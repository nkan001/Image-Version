import io
import json
import base64
import numpy as np
from PIL import Image
import tensorflow as tf
from tensorflow.keras.applications.imagenet_utils import preprocess_input

def predictTensorflowLite(inp):
    inp = base64.b64decode(inp)
    inp = Image.open(io.BytesIO(inp))
    inp = inp.resize((299,299))
    input_data = tf.keras.preprocessing.image.img_to_array(inp)
    input_data = preprocess_input(np.expand_dims(input_data, axis=0))
    print(input_data.shape)
    # input_data = tf.image.decode_jpeg(inp, channels=3)
    # Load the TFLite model and allocate tensors.
    interpreter = tf.lite.Interpreter(model_path="cnn_knn_model_small.tflite")
    interpreter.allocate_tensors()

    # Get input and output tensors.
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    print(output_details)

    # Test the model on random input data.
    input_shape = input_details[0]['shape']
    # input_data = x #np.array(np.random.random_sample(input_shape), dtype=np.float32)
    interpreter.set_tensor(input_details[0]['index'], input_data)

    interpreter.invoke()

    # The function `get_tensor()` returns a copy of the tensor data.
    # Use `tensor()` in order to get a pointer to the tensor.
    output_data = interpreter.get_tensor(output_details[0]['index'])
    print("output_data\n", output_data)
    with open("labels.txt") as f:
        recipesURLfull = f.read().splitlines()
        recipesURL = [recipesURLfull[int(i)] for i in output_data]
    print("recipesURL\n", recipesURL)
    return recipesURL