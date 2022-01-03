# Common imports
import numpy as np
from PIL import Image

# TensorFlow 
import tensorflow as tf
from tensorflow import keras

# OpenCV
import cv2

# Flask
from flask import request
from flask_restful import Resource, Api
from app import db
from sqlalchemy import text

from model.user import UserModel

class Predict(Resource):
    def post(self):
        # opencv object that will detect faces for us
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

        # Load model to face classification
        model_name = 'face_classifier.h5'

        # face_classifier = keras.models.load_model(f'../ml_models/{model_name}')
        face_classifier = keras.models.load_model(f'./ml_models/{model_name}')
        # class_names = ['abizar', 'bintang', 'muchdor']
        def get_class_name_from_db():
            try:
                sql = text('SELECT * FROM users')
                result = db.engine.execute(sql)
                class_names = []
                for row in result:
                    class_names.append(row[1])
                return class_names
            except Exception as e:
                print(e)
                return None  
        class_names = get_class_name_from_db()

        def get_extended_image(img, x, y, w, h, k=0.1):
            if x - k*w > 0:
                start_x = int(x - k*w)
            else:
                start_x = x
            if y - k*h > 0:
                start_y = int(y - k*h)
            else:
                start_y = y

            end_x = int(x + (1 + k)*w)
            end_y = int(y + (1 + k)*h)

            face_image = img[start_y:end_y,
                            start_x:end_x]
            face_image = tf.image.resize(face_image, [250, 250])
            # shape from (250, 250, 3) to (1, 250, 250, 3)
            face_image = np.expand_dims(face_image, axis=0)
            return face_image

        image = Image.open(request.files['image'])
        npimg = np.array(image)
        gray = cv2.cvtColor(npimg, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.3,
            minNeighbors=5,
            minSize=(100, 100),
            flags=cv2.CASCADE_SCALE_IMAGE
        )

        for (x, y, w, h) in faces:
            face_image = get_extended_image(npimg, x, y, w, h, 0.5)
            result = face_classifier.predict(face_image)
            prediction = class_names[np.array(
                result[0]).argmax(axis=0)]  # predicted class
            confidence = np.array(result[0]).max(axis=0)  # degree of confidence

        # display the resulting frame
        return {'prediction': prediction}

