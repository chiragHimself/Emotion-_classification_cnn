# -*- coding: utf-8 -*-
"""img_classificaton_cnn.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ryJQJtqLLDDqu0ORhNffkIvcft_5XBgM
"""

import cv2
import imghdr
import os
import tensorflow as tf

data_dir = '/content/drive/MyDrive/Datasets/cnn_happy_sad' # address to the directory of your saved image data.

image_exts = ['jpeg','jpg', 'bmp', 'png'] # allowed formats of images.

# code to remove any sort of images in our datasets that are not of our suitable datatypes.
for image_class in os.listdir(data_dir):
    for image in os.listdir(os.path.join(data_dir, image_class)):
        image_path = os.path.join(data_dir, image_class, image)
        try:
            img = cv2.imread(image_path)
            tip = imghdr.what(image_path)
            if tip not in image_exts:
                print('Image not in ext list {}'.format(image_path))
                os.remove(image_path)
        except Exception as e:
            print('Issue with image {}'.format(image_path))
            # os.remove(image_path)

"""**LOADING DATA**"""

import numpy as np
from matplotlib import pyplot as plt

data = tf.keras.utils.image_dataset_from_directory('/content/drive/MyDrive/Datasets/cnn_happy_sad')

data_iterator = data.as_numpy_iterator()
batch = data_iterator.next()

batch[1][:12]

#visulising our labels.
fig, ax = plt.subplots(ncols=4, figsize=(20,20))
for idx, img in enumerate(batch[0][0:4]):
    ax[idx].imshow(img.astype(int))
    ax[idx].title.set_text(batch[1][idx])

#=> 1 = happy
#=> 0 = confused
#=> 2 = sad

"""**SCALING**"""

data = data.map(lambda x,y: (x/255, y)) #returns normalized tuple. map is a funciton of dataset API.

data.as_numpy_iterator().next()

len(data) # around 12X32 images

'''from sklearn.model_selection import train_test_split
images, labels = zip(*data) # converting tupled data to lists.'''

'''# Initial train-test split to get training and test sets
train_images, test_images, train_labels, test_labels = train_test_split(images, labels, test_size=0.3, random_state=42)

# Further split the test set into test and cross-validation sets
test_images, cv_images, test_labels, cv_labels = train_test_split(test_images, test_labels, test_size=1/3, random_state=42)

# Now 'train_images', 'train_labels' contain the training data (70%)
# 'cv_images', 'cv_labels' contain the cross-validation data (20%)
# 'test_images', 'test_labels' contain the testing data (10%)'''# one method of doing splitting.

train_size = int(len(data)*.7)
val_size = int(len(data)*.2)+1
test_size = int(len(data)*.1)+1

train = data.take(train_size)
val = data.skip(train_size).take(val_size)
test = data.skip(train_size+val_size).take(test_size)

train

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Dense, Flatten, Dropout

#building layers of cnn
model = Sequential()
model.add(Conv2D(16, (3,3), 1, activation='relu', input_shape=(256,256,3)))
model.add(MaxPooling2D())
model.add(Conv2D(32, (3,3), 1, activation='relu'))
model.add(MaxPooling2D())
model.add(Conv2D(16, (3,3), 1, activation='relu'))
model.add(MaxPooling2D())
model.add(Flatten())
model.add(Dense(256, activation='relu'))
model.add(Dense(3, activation='softmax'))

model.compile('adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

model.summary()

logdir='/content/drive/MyDrive/Datasets/logs'
tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir=logdir)
hist = model.fit(train, epochs=20, validation_data=val, callbacks=[tensorboard_callback])

#plotting losses of training vs cross validation set using tensorboard
fig = plt.figure()
plt.plot(hist.history['loss'], color='teal', label='loss')
plt.plot(hist.history['val_loss'], color='orange', label='val_loss')
fig.suptitle('Loss', fontsize=20)
plt.legend(loc="upper left")
plt.show()
#reduction in loss of both sets is almost similar hense we can observe no overfitting.

#plotting accuracy scores of both the sets.
fig = plt.figure()
plt.plot(hist.history['accuracy'], color='teal', label='accuracy')
plt.plot(hist.history['val_accuracy'], color='orange', label='val_accuracy')
fig.suptitle('Accuracy', fontsize=20)
plt.legend(loc="upper left")
plt.show()

"""**NO PIRTICULAR OVERFITTING OF DATA IS OBSERVED.**

**Testing on random examples**
"""

import cv2
img = cv2.imread('/content/drive/MyDrive/Datasets/test images/images.jpg')# RANDOM SAD IMAGE.
plt.imshow(img)
plt.show()

resize = tf.image.resize(img, (256,256))
plt.imshow(resize.numpy().astype(int))
plt.show()

yhat = model.predict(np.expand_dims(resize/255, 0))
yhat

pred = np.argmax(yhat)
classes = ['confused','happy','sad']
predicted_class = classes[pred]
print(f'Predicted class is: {predicted_class}')

"""SAVING TRAINED MODEL"""

from tensorflow.keras.models import load_model
model.save("/content/drive/MyDrive/Datasets/Models/emotion_classification_cnn.h5")#address to model save folder.

# Load the saved model
loaded_model = tf.keras.models.load_model("/content/drive/MyDrive/Datasets/Models/emotion_classification_cnn.h5")