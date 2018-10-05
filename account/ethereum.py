from eth_keys import keys, KeyAPI
# from eth_keyfile import extract_key_from_keyfile, create_keyfile_json
from account.ecies import encrypt, decrypt
# import os, getpass
# from argparse import ArgumentParser
# import json
# import datetime
import logging
# import rlp
# from rlp.sedes import big_endian_int, text, Binary
# import constants

log = logging.getLogger(__name__)

class Account:

    def __init__(self, private_key: bytes):
        self.privkey = KeyAPI.PrivateKey(private_key)

    def __repr__(self):
        return self.privkey.public_key.to_hex()

    def __str__(self):
         return self.privkey.public_key.to_hex()

    def encrypt(self, message):
        return encrypt(message, self.privkey.public_key)

    def decrypt(self, enc_message):
        return decrypt(enc_message, self.privkey)

    def sign(self, message: bytes)->bytes:
        return self.privkey.sign_msg(message)

    def verify_sig_msg(self, message: bytes, signature: bytes, pubkey: bytes):
        """ Verifies that message has been signed by pubkey """
        public_key = KeyAPI.PublicKey(pubkey)
        signature = KeyAPI.Signature(signature)
        return signature.verify_msg(message, public_key)

    def extract_pubkey_from_signature(self, message: bytes, signature: bytes):
        """ Recover pubkey that signed message """
        signature = KeyAPI.Signature(signature)
        recovered_pk = signature.recover_public_key_from_msg(message)
        return recovered_pk

    def verify_sig_msg_hash(self, msg_hash: bytes, signature: bytes, pubkey: bytes):
        public_key = KeyAPI.PublicKey(pubkey)
        signature = KeyAPI.Signature(signature)
        return signature.verify_msg_hash(msg_hash, public_key)



"""
class Account: #(rlp.Serializable):
    def __init__(self, keyfile=None, password=None, private_key=None, path='./'):
        if isinstance(password, str):
            password = password.encode()

        # create new account if none given
        if all(p is None for p in [keyfile, private_key]):
            private_key = os.urandom(32)
            if password is None:
                password = os.urandom(10)

            if len(password):
                print('-'*15, 'Save this password somewhere', '-'*15)
                print('<', password.hex(), '>')
                print('-'*58)
            else:
                print('-'*5, '<empty password>', '-'*5)

            keyfile_data = create_keyfile_json(private_key, password)
            #filename = 'keyfile--'+keyfile_data['address']
            filename = os.path.join(path, 'keyfile--'+keyfile_data['address'])
            with open(filename, 'w') as file:
                file.write(json.dumps(keyfile_data))

        # load account from existing keyfile
        else:
            if private_key is None:
                private_key = extract_key_from_keyfile(keyfile, password)

        # init stuff for this account
        self.private_key = KeyAPI.PrivateKey(private_key)
        self.public_key  = keys.PublicKey.from_private(self.private_key)
        self.address = self.public_key.to_address()
        self.nonce = 0
        print('public_key=', self.public_key, type(self.public_key))
        print('address', self.address, type(self.address))
        # convert and keep private_key, public_key, signature in to_bytes()

"""



"""

if __name__ == "__main__":
    parser = ArgumentParser()
    # Add more options if you like
    parser.add_argument("-k", "--keyfile", dest="keyfilePath",
                        help="Ethereum keystore file", metavar="FILE")


    parser.add_argument("-p", "--password",
                        action="store_false", dest="password", default=True,
                        help="Ethereum account password")

    args = parser.parse_args()
    print('Ethereum keyfile', args.keyfilePath)
    if not os.path.exists(args.keyfilePath):
        parser.error("The file %s does not exist!" % args.keyfilePath)

    password = getpass.getpass()
    account = Account(keyfile=args.keyfilePath,
                      password=password,
                      private_key=None)

    signature = account.sign('hello world')
    print('signature=', signature, type(signature))
    print('valid=', verify('hello world', signature,account.public_key.to_bytes()))

    # encrypt without providing a key, use this account key
    enc_mes = account.encrypt('hello dick')
    print('encypted=', enc_mes)

    # encrypt providing the public key of another account (as bytes)
    enc_mes = account.encrypt('hello dick', account.public_key.to_bytes())
    print('encypted=', enc_mes)
    print('dec_mes=', account.decrypt(enc_mes))

    print('pubkey',account.public_key.to_bytes(),len(account.public_key.to_bytes()))
    pk_hex = account.public_key.to_bytes().hex()
    print('is_equal', bytes.fromhex(pk_hex))

    print('signature', signature)
    sig_hex = signature.hex()
    print('is_equal', bytes.fromhex(sig_hex))

    valid = verify('hello world', bytes.fromhex(sig_hex), bytes.fromhex(pk_hex))
    print('transaction valid', valid)


"""
