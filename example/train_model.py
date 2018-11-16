'''
Load csv file and trains and evaluate a simple MLP
'''

import numpy as np
import pandas as pd
import keras
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Embedding, LSTM
from keras.preprocessing.text import Tokenizer
from sklearn.model_selection import train_test_split

# diabetes = runtime.load('diabetes')
max_words = 2000
batch_size = 32
epochs = 20

df = pd.read_csv('./train.csv')
data = np.asarray(df.iloc[:, : -1], dtype=np.int32)
y_train = np.asarray(df.iloc[:, -1], dtype=np.int32)

num_classes = 46  # np.max(labels) + 1
x_data_train = []
for i, row in enumerate(data):
    x_data_train.append(list(row))

print('Vectorizing sequence data...')
tokenizer = Tokenizer(num_words=max_words)
x_train = tokenizer.sequences_to_matrix(x_data_train, mode='binary')
print('Convert class vector to binary class matrix '
      '(for use with categorical_crossentropy)')
y_train = keras.utils.to_categorical(y_train, num_classes)

print('x_train shape:', x_train.shape)
print('y_train shape:', y_train.shape)

print('Building model...')
model = Sequential()
model.add(Dense(128, input_shape=(max_words,)))
model.add(Activation('relu'))
model.add(Dropout(0.05))

model.add(Dense(64))
model.add(Activation('relu'))
model.add(Dropout(0.2))

model.add(Dense(32))
model.add(Activation('relu'))
model.add(Dropout(0.2))

model.add(Dense(num_classes))
model.add(Activation('softmax'))
model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

# Fit and store the model
model_id = "my-private-model"
model.fit(x_train, y_train,
          # validation_data=(x_test, y_test),
          epochs=epochs)

score = model.evaluate(x_train, y_train, batch_size=batch_size, verbose=1)
print('Test score:', score[0])
print('Test accuracy:', score[1])

print('Saving model')
model.save('./model_params.h5')
