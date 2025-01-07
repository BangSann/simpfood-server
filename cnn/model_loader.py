from tensorflow.keras.models import load_model
import tensorflow as tf
import os

MODEL_APP = os.path.join(os.path.dirname(__file__), 'model' , 'my_model.keras')

model = load_model(MODEL_APP)