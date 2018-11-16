# What is this?

This is a sample machine learning model training workflow.

## Step 1 
Data Provider owns the csv file `train.csv` where the original data is

## Step 2
Model Provider owns the algorithm in `train_model.py` 

## Step 3
Compute provider (== Data Provider) performs model training by launching `$ python train_model.py`

After model is trained, it is exported to local filesystem as `model_params.h5`

Compute provider stores trained model to IPFS executing `$ ipfs add model_params.h5`

## Step 4
A model verifier who is in possession of testing data as `test.csv`, can fetch the model from IPFS 
and perform off-chain verification launching `$ python verify_model.py`

Verification output can be written to fitchain smart contract together with verifier signature and address.
