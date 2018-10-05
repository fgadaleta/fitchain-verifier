import pytest
import os
import inspect
import sys
from web3 import Web3
from connector.ethereum import VpcContract, RegistryContract
from connector.config.vpc_config import VPC_CONFIG
from connector.config.registry_config import REG_CONFIG

# currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
# parentdir = os.path.dirname(currentdir)
# sys.path.insert(0, parentdir)

# Instantiate contracts to test in the single tests
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
    print("There are %s registered models" %registry.models)
    # Get model info given model_id
    model_info = registry.get_model('0x0001cd34fdsefg')
    print("model_info:", model_info)

def test_submit_proof():
    model_id = '0x0001cd34fdsefg'
    merkleroot = '000merkleroot000'
    sigs = ['sig1', 'sig2', 'sig3']
    sp_tx = vpc.submit_proof(model_id=model_id, merkleroot=merkleroot, sigs=sigs)
    print("Submit proof tx=", sp_tx)

    nproofs = vpc.nproofs(model_id)
    print("There are %s proofs for model %s " %(nproofs, model_id))
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
    print("there are %s active channels"% vpc.channels)

    model_id, k = vpc.get_channel('0x0001cd34fdsefg')
    print('Channel info model_id=%s k=%s'%(model_id, k))
