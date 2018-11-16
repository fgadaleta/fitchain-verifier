import numpy as np
import pandas as pd
import keras
from keras.models import load_model
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Embedding, LSTM
from keras.preprocessing.text import Tokenizer
from sklearn.model_selection import train_test_split

max_words = 2000

# Testing model
print('Loading testing data...')
df = pd.read_csv('./test.csv')
data = np.asarray(df.iloc[:, : -1], dtype=np.int32)
y_test = np.asarray(df.iloc[:, -1], dtype=np.int32)

num_classes = 46  # np.max(labels) + 1
x_data_test = []
for i, row in enumerate(data):
    x_data_test.append(list(row))

print('Vectorizing sequence data...')
tokenizer = Tokenizer(num_words=max_words)
x_test = tokenizer.sequences_to_matrix(x_data_test, mode='binary')
print('Convert class vector to binary class matrix '
      '(for use with categorical_crossentropy)')
y_test = keras.utils.to_categorical(y_test, num_classes)
print('x_train shape:', x_test.shape)
print('y_train shape:', y_test.shape)


model = load_model('./model_params.h5')
score = model.evaluate(x_test, y_test)
print('Test score:', score[0])
print('Test accuracy:', score[1])
