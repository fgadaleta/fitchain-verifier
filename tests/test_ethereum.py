import pytest
import os
import inspect
import sys
import logging
from web3 import Web3
from connector.ethereum import VpcContract, RegistryContract
from connector.config.vpc_config import VPC_CONFIG
from connector.config.registry_config import REG_CONFIG

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


# Instantiate contracts to call from each single test
w3 = Web3(Web3.HTTPProvider("http://localhost:8545", request_kwargs={'timeout': 60}))

vpc = VpcContract(eth_config=VPC_CONFIG['LOCAL'], abi_file='Vpc')
vpc.account = w3.eth.accounts[3]
vpc.deposit()

registry = RegistryContract(eth_config=REG_CONFIG['LOCAL'], abi_file="Registry")
registry.account = w3.eth.accounts[0]


def test_create_model():
    # Create a model and add to registry
    # model_id is a user-defined name, ipfs_addr is the unique id of the model (hash)
    cm_tx = registry.create_model(model_id="my_model_name", ipfs_addr="0x0001cd34fdsefg", stored_as=1,
                                  bounty=100, current_error=1, target_error=0)
    print("Created model tx=", cm_tx)
    print("There are %s registered models" % registry.models)
    # Get model info given model_id
    model_info = registry.get_model('0x0001cd34fdsefg')
    print("model_info:", model_info)


def test_submit_proof():
    model_id = '0x0001cd34fdsefg'
    merkleroot = '000merkleroot001'
    sigs = ['sig1', 'sig2', 'sig3']
    sp_tx = vpc.submit_proof(model_id=model_id, merkleroot=merkleroot, sigs=sigs)
    print("Submit proof tx=", sp_tx)

    nproofs = vpc.nproofs(model_id)
    print("There are %s proofs for model %s " % (nproofs, model_id))
    proofs = vpc.get_proofs(model_id)
    print("Proofs = ", proofs)
    # assert 0


def test_create_challenges():
    # Create a number of challenges to the same model
    cc_tx = registry.create_challenge('0x0001cd34fdsefg', '0x98978797897879')
    print("Created challenge tx = ", cc_tx)
    cc_tx = registry.create_challenge('0x0001cd34fdsefg', '0x767676767676767')
    print("Created challenge tx = ", cc_tx)
    cc_tx = registry.create_challenge('0x0001cd34fdsefg', '0x212121212121212')
    print("Created challenge tx = ", cc_tx)
    # Get all challenges of a model
    gc_tx = registry.get_model_challenges('0x0001cd34fdsefg')
    print("Model challenges tx = ", gc_tx)


def test_init_channel():
    # Initiate a channel for the proof-of-training of a model
    ic_tx = vpc.init_channel('0x0001cd34fdsefg', 2)
    print("Init channel tx=", ic_tx)
    print("there are %s active channels" % vpc.channels)

    model_id, k = vpc.get_channel('0x0001cd34fdsefg')
    print('Channel info model_id=%s k=%s' % (model_id, k))


def test_use_case_1():
    """
        Deposit 12ETH to VPC and become validator from accounts[2], accounts[3], accounts[4]
        Create 1 model and initiate channel (from accounts[1])
        Submit 3 proofs from accounts[2], accounts[3], accounts[4]
        Check validation
    """

    # Deposit 12ETH to VPC and become validator from accounts[2], accounts[3], accounts[4]
    for i in [2, 3, 4]:
        vpc.account = w3.eth.accounts[i]
        vpc.deposit()

    # Create 1 model and initiate channel (from accounts[1])
    registry.account = w3.eth.accounts[1]
    cm_tx = registry.create_model(model_id="my_decentralized_model",
                                  ipfs_addr="0x023401cd34453d123e98",
                                  stored_as=1, bounty=100,
                                  current_error=1, target_error=0)
    log.info("Created model tx=%s", cm_tx)
    log.info("There are %s registered models", registry.models)
    ic_tx = vpc.init_channel('0x023401cd34453d123e98', 3)
    log.info("Init channel tx=%s", ic_tx)
    model_id, k = vpc.get_channel('0x0001cd34fdsefg')
    log.info('Channel info model_id=%s k=%s', model_id, k)

    # Submit 3 proofs from accounts[2], accounts[3], accounts[4]
    model_id = '0x023401cd34453d123e98'
    merkleroot = '000merkleroot000'
    sigs = ['sig1', 'sig2', 'sig3']
    for i in [2, 3, 4]:
        vpc.account = w3.eth.accounts[i]
        sp_tx = vpc.submit_proof(model_id=model_id, merkleroot=merkleroot, sigs=sigs)
        log.info("Submit proof tx=%s", sp_tx)

    assert 0



def test_use_case_2():
    """ Create 1 model from accounts[1]
        Initiate a channel for such model (from accounts[1])
        Submit 3 proofs from accounts[2], accounts[3], accounts[4]
        Check validation
        Create 3 model challenges from accounts[2], accounts[3], accounts[4]
    """
    pass
