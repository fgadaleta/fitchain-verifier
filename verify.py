from argparse import ArgumentParser
from eth_keyfile import (extract_key_from_keyfile, create_keyfile_json)
import os
import tempfile
import getpass
import json
import numpy as np
import pandas as pd
import datetime
import logging
from web3 import Web3
from account.ethereum import Account
from connector.ethereum import VpcContract, RegistryContract
from connector.config.vpc_config import VPC_CONFIG
from connector.config.registry_config import REG_CONFIG
from connector.ipfs import IPFS


log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


def load_data(filepath):
    from keras.preprocessing.text import Tokenizer
    import keras
    max_words = 2000
    num_classes = 46

    print('Loading testing data...')
    df = pd.read_csv(filepath)
    data = np.asarray(df.iloc[:, : -1], dtype=np.int32)
    y_test = np.asarray(df.iloc[:, -1], dtype=np.int32)
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
    return x_test, y_test


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-m", "--model", dest="model_schema",
                        help="Schema of the model to verify", metavar="FILE", required=True)
    parser.add_argument("-d", "--data", dest="data_schema",
                        help="Schema of the testing data to verify model with", metavar="FILE", required=True)

    args = parser.parse_args()
    model_schema = args.model_schema
    data_schema = args.data_schema

    if not os.path.exists(model_schema):
        parser.error("The file %s does not exist!" % model_schema)
    if not os.path.exists(data_schema):
        parser.error("The file %s does not exist!" % data_schema)

    with open(model_schema) as json_file:
        model_info = json.load(json_file)
    with open(data_schema) as json_file:
        data_info = json.load(json_file)

    # check signatures (model and data are compatible)
    assert (model_info["input_signature"] == data_info["input_signature"])
    assert (model_info["type"] == "keras")
    assert (model_info["format"] == "h5")

    if model_info["location"]["provider"] == "ipfs":
        # load model from IPFS and save to local filesystem
        model_endpoint = model_info["location"]["endpoint"]
        from connector.config.ipfs_config import IPFS_CONFIG
        ipfs_conn = IPFS(ipfs_config=IPFS_CONFIG['LOCAL'])
        model_bytes = ipfs_conn.get_obj(model_endpoint)
        # save model to file
        modelfile = tempfile.NamedTemporaryFile()
        modelfile.write(model_bytes)
        print('Model saved at %s' % modelfile.name)
    else:
        raise NotImplementedError

    if data_info["location"]["provider"] == "ipfs":
        data_endpoint = data_info["location"]["endpoint"]
        data_bytes = ipfs_conn.get_obj(data_endpoint)
        # save data to file
        datafile = tempfile.NamedTemporaryFile()
        datafile.write(data_bytes)
        print('Testing data saved at %s' % datafile.name)
    else:
        raise NotImplementedError

    from keras.models import load_model
    model = load_model(modelfile.name)
    print('Model loaded')
    print(model.summary())
    print('Data loaded')
    x, y = load_data(datafile.name)
    y_hat = model.predict(x)
    print('positive hits=', np.sum(abs(y_hat - y)/y < 0.1))
    score = model.evaluate(x, y)
    print('Test score:', score[0])
    print('Test accuracy:', score[1])
