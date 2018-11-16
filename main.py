from argparse import ArgumentParser
from eth_keyfile import (extract_key_from_keyfile, create_keyfile_json)
import os
import getpass
import json
import datetime
import logging
from web3 import Web3
from account.ethereum import Account
from connector.ethereum import VpcContract, RegistryContract
from connector.config.vpc_config import VPC_CONFIG
from connector.config.registry_config import REG_CONFIG

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

private_keys = ['4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d',
                '6cbed15c793ce57650b9877cf6fa156fbef513c4e6134f022a85b1ffdd59b2a1',
                '6370fd033278c143179d81c5526140625662b8daa446c22ee2d73db3707e620c',
                '646f1ce2fdad0e6deeeb5c7e8e5543bdde65e86029e2fd9fc169899c440a7913',
                'add53f9a7e588d003326d1cbf9e4a43c061aadd9bc938c843a79e7b4fd2ad743',
                '395df67f0c2d2d9fe1ad08d1bc8b6627011959b79c53d7dd6a3536a33ab8a4fd',
                'e485d098507f54e7733a205420dfddbe58db035fa577fc294ebd14db90767a52',
                'a453611d9419d0e56f499079478fd72c37b251a94bfde4d19872c44cf65386e3',
                '829e924fdf021ba3dbbc4225edfece9aca04b929d6e75613329ca6f1d31c0bb4',
                'b0057716d5917badaf911b193b12b910811c1497b5bada8d7711f758981c3773']

if __name__ == "__main__":

    parser = ArgumentParser()
    parser.add_argument("-m", "--model", dest="model_schema",
                        help="Schema of the model to verify", metavar="FILE", required=True)
    parser.add_argument("-d", "--data", dest="data_schema",
                        help="Schema of the testing data to verify model with", metavar="FILE", required=True)

    # parser.add_argument("-k", "--keyfile", dest="keyfilePath",
    #                    help="Ethereum keystore file", metavar="FILE", required=True)

    args = parser.parse_args()
    # keyfile = args.keyfilePath
    # if not os.path.exists(keyfile):
    #    parser.error("The file %s does not exist!" % keyfile)

    model_schema = args.model_schema
    data_schema = args.data_schema

    if not os.path.exists(model_schema):
        parser.error("The file %s does not exist!" % model_schema)
    if not os.path.exists(data_schema):
        parser.error("The file %s does not exist!" % data_schema)

    # password = getpass.getpass()
    # private_key = extract_key_from_keyfile(keyfile, password)

    # TODO
    # get private_key from ethereum keystore file
    # private_key = bytes.fromhex('4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d')
    # verifier = Account(private_key)

    # Common fields for this proof
    merkleroot = 'eb7368b657facb55bf7712d49dc72e7f591e682418bb62a6af6c5336cf7a279e'
    service_id = 'FROM_OCEAN_0X1234'
    model_id = 'FROM_FITCHAIN_0xabcd'

    verifiers = list()

    for i in range(len(private_keys)):
        verifiers.append(Account(bytes.fromhex(private_keys[i])))

    # One signer
    v = verifiers[0]

    # Instantiate contracts to call from each single test
    w3 = Web3(Web3.HTTPProvider("http://localhost:8545", request_kwargs={'timeout': 60}))
    vpc = VpcContract(eth_config=VPC_CONFIG['LOCAL'], abi_file='Vpc')
    vpc.account = w3.eth.accounts[3]
    print('Account ', vpc.account)

    registry = RegistryContract(eth_config=REG_CONFIG['LOCAL'], abi_file="Registry")
    registry.account = w3.eth.accounts[0]
    cm_tx = registry.create_model(model_id="my_model_name", ipfs_addr=model_id, stored_as=1,
                                  bounty=100, current_error=1, target_error=0)

    # print("Created model tx=", cm_tx)
    # Get model info given model_id
    model_info = registry.get_model(model_id)
    print('\n\nCreated model', model_info)
    print("There are %s registered models" % registry.models)

    # Deposit 12ETH to VPC and become validator from accounts[2], accounts[3], accounts[4]
    for i in [0, 1, 2, 3, 4, 5, 6, 7, 8]:
        # log.info('Setting VPC eth_account with %s type=%s', w3.eth.accounts[i], type(w3.eth.accounts[i]))
        print('Account %s deposits to VPC' % w3.eth.accounts[i])
        vpc.account = w3.eth.accounts[i]
        vpc.deposit()

    # Initiate a channel for the proof-of-training of this model
    ic_tx = vpc.init_channel(model_id, 4)
    m, k = vpc.get_channel(model_id)
    print('Initiated channel for model model_id=%s min_gossipers=%s' % (m, k))
    print("there are %s active channels" % vpc.channels)

    # TODO
    # fetch (model, data) and perform off-chain model validation

    # Last transaction (End-of-Training)
    tx_eot = {'eot': True,
              'date': datetime.datetime.now().timestamp(),
              'metrics': {
                  'accuracy': 0.95,
                  'error': 0.07
                  }
              }
    # dump to string
    tx_eot = json.dumps(tx_eot)
    print("\n\nMessage\n", tx_eot)

    # Concatenate and sign the hash of it
    msg = (service_id + model_id + tx_eot + merkleroot).encode('utf-8')
    msg_hash = v.hash(msg)
    sig = v.sign(bytes.fromhex(msg_hash))

    # Create proof
    proof = {'service_id': service_id,
             'model_id': model_id,
             'message': tx_eot,
             'merkleroot': merkleroot,
             'signature': sig.to_hex(),
             'sender_addr': v.address
             }

    # dump proof to string
    proof = json.dumps(proof)

    print('\n\nSubmitting proof\n', proof)
    # FIXME
    # vpc.submit_proof(service_id, model_id, tx_eot, sig, v.address)

    # TODO
    # Ahmed working on VPC
    # submit_proof(service_id, model_id, merkleroot, tx_eot, sig, sender_addr)
    # bytes32, bytes32, string, string, bytes, address


    # Simulate other gossipers signing the same proof
    signatures = []
    for verifier in verifiers:
        s = verifier.sign(bytes.fromhex(msg_hash))
        print('signature', s, type(s))
        pk = verifier.address
        signatures.append((s.to_hex(), pk))

    print("\n\nSignatures \n")
    for sig, account in signatures:
        print(sig, account)


    # Now it's the VPC's turn :)






    # encrypt without providing a key, use this account key
    # enc_msg = v.encrypt(message)
    # print('\n\nEncypted message\n', enc_msg.hex())

    # encrypt providing the public key of another account (as bytes)
    # enc_mes = verifier.encrypt(message, """ another_pubkey """)
    # print('encypted=', enc_mes)
    # print('dec_mes=', verifier.decrypt(enc_mes))
