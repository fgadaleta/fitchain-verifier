from argparse import ArgumentParser
from eth_keyfile import (extract_key_from_keyfile, create_keyfile_json)
import os
import getpass
import json
import datetime 
from account.ethereum import Account

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
    """
    parser = ArgumentParser()
    parser.add_argument("-k", "--keyfile", dest="keyfilePath",
                        help="Ethereum keystore file", metavar="FILE", required=True)

    args = parser.parse_args()
    keyfile = args.keyfilePath
    if not os.path.exists(keyfile):
        parser.error("The file %s does not exist!" % keyfile)
    """
    # password = getpass.getpass()
    # private_key = extract_key_from_keyfile(keyfile, password)

    # TODO
    # get private_key from ethereum keystore file
    # private_key = bytes.fromhex('4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d')
    # verifier = Account(private_key)
    verifiers = list()
    
    for i in range(len(private_keys)):
        verifiers.append(Account(bytes.fromhex(private_keys[i])))

    # One signer
    v = verifiers[0]
    
    # TODO
    # fetch (model, data) and perform off-chain model validation
    
    
    # Create message after model validation
    message = {'eot': True,
               'date': datetime.datetime.now().timestamp(),
               'metrics': {
                   'accuracy': 0.95,
                   'error': 0.07}
    }

    # TODO
    # sig = v.sign(hash(service_id + model_id + message + merkleroot))
    proof = {'service_id' : 'FROM_OCEAN_0x1234',
             'model_id': 'FROM_FITCHAIN_0xabcd',
             'message': message,
             'merkleroot': merkleroot,
             'signature': sig,
             'publickey': v.public_key }
    
    print("\n\nMessage\n", message)
    message = json.dumps(message).encode()
    
    signature = v.sign(message)
    print('signature=', signature, type(signature))
    print('valid=', v.verify_sig_msg(message, signature.to_bytes(), v.public_key))

    signatures = []
    for verifier in verifiers:
        signatures.append( (verifier.sign(message), verifier.public_key.hex()) )
    print("\n\nSignatures \n")
    for sig, account in signatures:
        print(sig, account)

    # encrypt without providing a key, use this account key
    # enc_msg = v.encrypt(message)
    # print('\n\nEncypted message\n', enc_msg.hex())

    # encrypt providing the public key of another account (as bytes)
    # enc_mes = verifier.encrypt(message, """ another_pubkey """)
    # print('encypted=', enc_mes)
    # print('dec_mes=', verifier.decrypt(enc_mes))

    # TODO
    # create json
    eot_msg = {
        'model_id': 0x1234,
        'eot': message,
        'signatures': signatures
    }
    
    
