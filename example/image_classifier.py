from fitchain import Runtime

# initialize the runtime
runtime = Runtime()

# Load the dataset from the project
data = runtime.resolve("cats_and_dogs")
print('Found %d files in this collection' % len(data.files))
# files = data.files
# print(files[:10])

# Prepare data
train_dog_files = []    # paths of all dogs images to train from
train_cat_files = []    # paths of all cats images to train from
valid_dog_files = []    # paths of all dogs images to validate
valid_cat_files = []    # paths of all cats images to validate

for f in data.files:
    path = f.split('/')
    if path[0] == 'train':
        if path[1] == 'dogs':
            train_dog_files.append(f)
        if path[1] == 'cats':
            train_cat_files.append(f)
    if path[0] == 'valid':
        if path[1] == 'dogs':
            valid_dog_files.append(f)
        if path[1] == 'cats':
            valid_cat_files.append(f)

# Create your model and give it a unique identifier
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D
from keras.layers import Activation, Dropout, Flatten, Dense
from keras import backend as K
from PIL import Image
import numpy as np

# dimensions of our images
img_width, img_height = 150, 150
nb_validation_samples = 800
epochs = 1
batch_size = 32
# number of channels
if K.image_data_format() == 'channels_first':
    input_shape = (3, img_width, img_height)
else:
    input_shape = (img_width, img_height, 3)

# take the min number of dogs and cats files to build a balanced training dataset
num_dog_files = len(train_dog_files)
num_cat_files = len(train_cat_files)
num_files = min(num_dog_files, num_cat_files)
nb_train_samples = num_files * 2

# prepare images with the correct label
all_images = []
all_labels = []
for i in range(num_files):
    imgFile = data.resolve(train_dog_files[i])
    img = Image.open(imgFile)

    #img = data.load_file(train_dog_files[i])
    img = img.resize((img_width, img_height), Image.ANTIALIAS)   # resize with PIL
    img_data = np.array(img)  # convert to array
    all_images.append(img_data)
    all_labels.append(0)

    imgFile = data.resolve(train_cat_files[i])
    img = Image.open(imgFile)
    # img = data.load_file(train_cat_files[i])
    img = img.resize((img_width, img_height), Image.ANTIALIAS)   # resize with PIL
    img_data = np.array(img)  # convert to array
    all_images.append(img_data)
    all_labels.append(1)

# convert to numpy array (for keras)
all_images = np.asarray(all_images)
all_labels = np.asarray(all_labels)

def generator(X_data, y_data, batch_size):
    """ This just feeds the current batch """
    samples_per_epoch = X_data.shape[0]
    number_of_batches = samples_per_epoch/batch_size
    counter = 0
    while 1:
        X_batch = np.array(X_data[batch_size*counter:batch_size*(counter+1)]).astype('float32')
        y_batch = np.array(y_data[batch_size*counter:batch_size*(counter+1)]).astype('float32')
        counter += 1
        yield X_batch, y_batch
        # restart counter to yeild data in the next epoch as well
        if counter <= number_of_batches:
            counter = 0


# classifier
model = Sequential()
model.add(Conv2D(32, (3, 3), input_shape=input_shape))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Conv2D(32, (3, 3)))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Conv2D(64, (3, 3)))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Flatten())
model.add(Dense(64))
model.add(Activation('relu'))
model.add(Dropout(0.5))
model.add(Dense(1))
model.add(Activation('sigmoid'))
model.compile(loss='binary_crossentropy',
              optimizer='rmsprop',
              metrics=['accuracy'])

# For keras you need to perform the following steps:
from fitchain import keras as ker
model_id = 'catsanddogsmodel'
ker.store_train_params(model_id, x=all_images, y=all_labels)
ker.store_validate_params(model_id, x=all_images, y=all_labels)

# Fit model with entire data batch (can be prohibitive with many images)
ker.fit(model_id, model, x_train=all_images, y_train=all_labels, epochs=epochs)







# Fit model with batches and generator (scalable with millions of images)
#ker.fit_generator(model_id, model, all_images, all_labels, batch_size, generator,
#                  epochs=epochs, steps_per_epoch=nb_train_samples // batch_size)

# happens in runtime
# model.save('./model_file.h5')
#eval_loss, eval_acc = model.evaluate(all_images, all_labels, verbose=1)
#metric = "LOSS=%s ACC=%s"%(eval_loss, eval_acc)
#print(metric)
