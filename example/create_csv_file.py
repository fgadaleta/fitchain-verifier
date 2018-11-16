# Data owner posts data onto a CSV file
# We just convert from keras to a csv file for demonstration purpose only

import numpy as np
import pandas
from keras.datasets import reuters

MAX_WORDS = 1000
MAX_ROWS = 1000

(x_train, y_train), (x_test, y_test) = reuters.load_data(num_words=MAX_WORDS, test_split=0)
x_train = x_train[:MAX_ROWS]
y_train = y_train[:MAX_ROWS]
x_test = x_test[:MAX_ROWS]
y_test = y_test[:MAX_ROWS]


lens = []
for e in x_train:
    lens.append(len(e))
maxlen = max(lens)

# create numpy array where the first columns are features
# last column is label
x_data = np.zeros([x_train.shape[0], maxlen + 1])

for i, j in enumerate(x_train):
    x_data[i][:len(j)] = j
for i, j in enumerate(y_train):
    x_data[i][-1] = j

print('Converting to csv file and storing')
df = pandas.DataFrame(x_data)
df.to_csv('data.csv', sep=',', index=False, index_label=False)
