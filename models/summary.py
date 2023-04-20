import tensorflow as tf

model_path = 'model1.h5'


model = tf.keras.models.load_model(model_path)
model.summary()