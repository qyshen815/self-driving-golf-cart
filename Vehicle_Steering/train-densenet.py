import pandas as pd
import os, sys
import cv2
import numpy as np
import matplotlib.pyplot as plt
import densenet

from keras.models import Model, Sequential
from keras.layers.core import Dense, Dropout, Activation, Flatten
from keras.layers.convolutional import Conv2D, Conv2DTranspose, UpSampling2D
from keras.layers.pooling import AveragePooling2D, MaxPooling2D
from keras.layers.pooling import GlobalAveragePooling2D
from keras.layers import Input
from keras.layers.normalization import BatchNormalization
from keras.regularizers import l2
from keras.utils import plot_model
from keras.optimizers import Adam
from keras.models import load_model
import keras as K

steering_labels = None

def rotate(img):
    row, col, channel = img.shape
    angle = np.random.uniform(-15, 15)
    rotation_point = (row / 2, col / 2)
    rotation_matrix = cv2.getRotationMatrix2D(rotation_point, angle, 1)
    rotated_img = cv2.warpAffine(img, rotation_matrix, (col, row))
    return rotated_img


def gamma(img):
    gamma = np.random.uniform(0.5, 1.2)
    invGamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** invGamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
    new_img = cv2.LUT(img, table)
    return new_img


def blur(img):
    r_int = np.random.randint(0, 2)
    odd_size = 2 * r_int + 1
    return cv2.GaussianBlur(img, (odd_size, odd_size), 0)

def random_transform(img):
    # There are total of 3 transformation
    # I will create an boolean array of 3 elements [ 0 or 1]
    a = np.random.randint(0, 2, [1, 3]).astype('bool')[0]
    if a[0] == 1:
        img = rotate(img)
    if a[1] == 1:
        img = blur(img)
    if a[2] == 1:
        img = gamma(img)
    return img

def generate_train_batch(data, batch_size = 16):

    img_rows = 480
    img_cols = 640
    
    batch_images = np.zeros((batch_size, img_rows, img_cols, 3))
    angles = np.zeros((batch_size, 1))
    while 1:
        for i_batch in range(batch_size):
            i_line = np.random.randint(2000)
            i_line = i_line+len(data)-2000
            
            file_name = steering_labels.iloc[i_line]["filename"]
            img_bgr = cv2.imread("/home/ubuntu/dataset/udacity-driving/" + file_name)
            
            b,g,r = cv2.split(img_bgr)       # get b,g,r
            rgb_img = cv2.merge([r,g,b])     # switch it to rgb
            
            f =  float(steering_labels.iloc[i_line]["angle"]) #* 57.2958 #float(* 180.00 / 3.14159265359 )
    
            i = np.random.randint(3)
            if i == 0:
                rgb_img = cv2.flip(rgb_img, 1)
                f = f * -1.0
            if i == 1:
                rgb_img = random_transform(rgb_img)
    
            batch_images[i_batch] = rgb_img
            angles[i_batch] = f
            
        yield batch_images, angles
    
if __name__ == "__main__":

    steering_labels = pd.read_csv("/home/ubuntu/dataset/udacity-driving/interpolated.csv")
    print(steering_labels.shape)
    steering_labels.head()
    
    depth = 13
    growth_rate = 12
    nb_filters = 24 # (2 * growth_rate)
    model = densenet.DenseNet(nb_classes=1, 
                              img_dim=(480, 640, 3), 
                              depth = depth, 
                              nb_dense_block = 3, 
                              growth_rate = growth_rate, 
                              nb_filter = nb_filters, 
                              dropout_rate=0.1)
    model.compile(optimizer=Adam(lr=1e-4), loss="mse")
    model.summary()
    # model start here
    generator = generate_train_batch(steering_labels, 1)
    history = model.fit_generator(generator, steps_per_epoch=10000, epochs=5, verbose=1)

    model.save('trained-v9.h5')

