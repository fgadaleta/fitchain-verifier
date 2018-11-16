import pytest
import logging
from web3 import Web3
from connector.ethereum import VpcContract, RegistryContract
from connector.config.vpc_config import VPC_CONFIG
from connector.config.registry_config import REG_CONFIG
from account.ethereum import Account

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


"""

From
$ ganache-cli -d 42 -e 50000 --db /tmp

these public, private keys are generated


Available Accounts
==================
(0) 0x90f8bf6a479f320ead074411a4b0e7944ea8c9c1
(1) 0xffcf8fdee72ac11b5c542428b35eef5769c409f0
(2) 0x22d491bde2303f2f43325b2108d26f1eaba1e32b
(3) 0xe11ba2b4d45eaed5996cd0823791e0c93114882d
(4) 0xd03ea8624c8c5987235048901fb614fdca89b117
(5) 0x95ced938f7991cd0dfcb48f0a06a40fa1af46ebc
(6) 0x3e5e9111ae8eb78fe1cc3bb8915d5d461f3ef9a9
(7) 0x28a8746e75304c0780e011bed21c72cd78cd535e
(8) 0xaca94ef8bd5ffee41947b4585a84bda5a3d3da6e
(9) 0x1df62f291b2e969fb0849d99d9ce41e2f137006e

Private Keys
==================
(0) 4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d
(1) 6cbed15c793ce57650b9877cf6fa156fbef513c4e6134f022a85b1ffdd59b2a1
(2) 6370fd033278c143179d81c5526140625662b8daa446c22ee2d73db3707e620c
(3) 646f1ce2fdad0e6deeeb5c7e8e5543bdde65e86029e2fd9fc169899c440a7913
(4) add53f9a7e588d003326d1cbf9e4a43c061aadd9bc938c843a79e7b4fd2ad743
(5) 395df67f0c2d2d9fe1ad08d1bc8b6627011959b79c53d7dd6a3536a33ab8a4fd
(6) e485d098507f54e7733a205420dfddbe58db035fa577fc294ebd14db90767a52
(7) a453611d9419d0e56f499079478fd72c37b251a94bfde4d19872c44cf65386e3
(8) 829e924fdf021ba3dbbc4225edfece9aca04b929d6e75613329ca6f1d31c0bb4
(9) b0057716d5917badaf911b193b12b910811c1497b5bada8d7711f758981c3773

"""


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
    model_id = b'0x0001cd34fdsefg'
    service_id = b'from_ocean_service_id'
    merkleroot = b'000merkleroot001'
    sigs = [b'sig1', b'sig2', b'sig3']

    # submit_proof(service_id, model_id, merkleroot, tx_eot, sig, sender_addr)
    # bytes32, bytes32, string, string, bytes, address

    for sig in sigs:
        sp_tx = vpc.submit_proof(model_id=model_id, merkleroot=merkleroot, sig)
        # sp_tx = vpc.submit_proof(model_id=model_id, merkleroot=merkleroot, sigs=sigs)
        print("from test_submit_proof tx=", sp_tx.hex())

    nproofs = vpc.nproofs(model_id)
    print("There are %s proofs for model %s " % (nproofs, model_id.hex()))
    proofs = vpc.get_proofs(model_id)
    print("Proofs = ", proofs)
    assert 0


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

"""
Deposit 12ETH to VPC and become validator from accounts[2], accounts[3], accounts[4]
Create 1 model and initiate channel (from accounts[1])
Submit 3 proofs from accounts[2], accounts[3], accounts[4]
Check validation
"""
"""
def test_use_case_1():    
    # Deposit 12ETH to VPC and become validator from accounts[2], accounts[3], accounts[4]
    for i in [2, 3, 4]:
        log.info('Setting VPC eth_account with %s type=%s', w3.eth.accounts[i], type(w3.eth.accounts[i]))
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
    model_id = b'0x023401cd34453d123e98'
    merkleroot = b'000merkleroot000'

    # creating valid signatures from each verifier
    pvt_keys = {}
    pvt_keys[2] = '6370fd033278c143179d81c5526140625662b8daa446c22ee2d73db3707e620c'
    pvt_keys[3] = '646f1ce2fdad0e6deeeb5c7e8e5543bdde65e86029e2fd9fc169899c440a7913'
    pvt_keys[4] = 'add53f9a7e588d003326d1cbf9e4a43c061aadd9bc938c843a79e7b4fd2ad743'

    sigs = []
    for i in [2, 3, 4]:
        verifier = Account(bytes.fromhex(pvt_keys[i]))
        sig = verifier.sign(merkleroot)
        sigs.append(sig.to_bytes())
    print('from test_use_case_1 signatures=%s' % sigs)

    # sigs = ['sig1', 'sig2', 'sig3']
    for i in [2, 3, 4]:
        vpc.account = w3.eth.accounts[i]
        sp_tx = vpc.submit_proof(model_id=model_id, merkleroot=merkleroot, sigs=sigs)
        log.info("Submit proof tx=%s", sp_tx)

    assert 0
"""

def test_use_case_2():
    """ Create 1 model from accounts[1]
        Initiate a channel for such model (from accounts[1])
        Submit 3 proofs from accounts[2], accounts[3], accounts[4]
        Check validation
        Create 3 model challenges from accounts[2], accounts[3], accounts[4]
    """
    pass
