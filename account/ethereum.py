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
Return value of this transaction after verification or
False if verification fails
"""
"""
def verify_transaction_v1(key: str, transaction: Transaction, sign=True):
    #log.debug('verifying transaction with key %s', key)
    #log.debug('transaction content %s', transaction.as_dict())
    #print('DEBUG from verify_transaction_v1 ', transaction.as_dict())
    tx_hash = transaction.hash.hex()
    #print('DEBUG from verify_transaction_v1 tx_hash=', tx_hash)
    # if digest of this transaction is not key, return
    if tx_hash != key:
        print('uh oh! Hash is not the same')
        return False

    sender_pk  = transaction['sender_pk']
    nonce = transaction['nonce']
    validators = transaction['validators']
    #print('DEBUG from verify_transaction_v1 sender_pk=', sender_pk, type(sender_pk))
    #print('DEBUG validators=', validators)
    # verify sender signature
    signatures = transaction['signatures']

    sender_signature = signatures[0]
    sender_pk = transaction['sender_pk']
    valid_sender = verify_signature(transaction.body, sender_signature, sender_pk)
    if not valid_sender:
        print('Cannot verify sender, aborting.')
        return False

    # sign this transaction and append to signatures
    if sign:
        print('Signing and appending my signature')
        signa = Globals.account.sign(transaction.body, to_bytes=False)
        #print('signa=', signa, type(signa))
        signatures = signatures + (signa.encode(), )

    # TODO verify all signatures
    # when state channel is opened, list of required validators is attached
    # to tx['validators']. Here we check if they have signed
    collected_signatures = 0
    for validator_signature, validator_pubkey in zip(signatures, validators):
        recovered_pk = verify_signature(transaction.body, validator_signature)
        # print('DEBUG from verify_transaction_v1 Recovered pk=', recovered_pk)
        if recovered_pk in validators:
            collected_signatures += 1

    if collected_signatures < constants.MIN_NUM_SIGNATURES:
        print('DEBUG from verify_transaction_v1 Insufficient number of signatures collected. This transaction is not yet final.')

    # all is text before returning Transaction object
    signatures = [s.decode() for s in signatures]
    validators = [v.decode() for v in validators]

    return Transaction(sender_pk,
                       nonce,
                       transaction['data'],
                       transaction['timestamp'],
                       signatures,
                       validators)

"""

"""
fields = [
    ('private_key', binary),
    ('public_key', binary),
    ('address', binary),
]
"""

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

    def sign(self, message, to_bytes=True):
        # Return (str) signature of message signed with private key (hex)
        # @param message str or bytes

        if not isinstance(message, bytes):
            message = message.encode()
        signature = self.private_key.sign_msg(message)

        if to_bytes:
            return signature.to_bytes()

        return signature.to_bytes().hex()

    def encrypt(self, message, public_key=None):
        # Return message encrypted with public key
        # @param message bytes
        # @param public_key bytes

        if isinstance(message, str):
            message = message.encode()

        if public_key is None:
            public_key = self.public_key
        else:
            public_key = KeyAPI.PublicKey(public_key)
        return ecies.encrypt(message, public_key)

    def decrypt(self, encrypted_message):
        # Return decrypted message with private key
        # @param encrypted_message bytes
        return ecies.decrypt(encrypted_message, self.private_key)

    def create_transaction(self, data):
        # Create transaction from this account and return tx dictionary
        # print('DEBUG from create_transaction data=', data, type(data))
        now = str(int(datetime.datetime.utcnow().timestamp()))
        # this should be set from smart contract
        validators = ['0x3d4a8e640bdcf0c640ea42e5c25877afc572101c',
                      '0x40210576d9262a214aac7494e85718ec3a12ec54',
                      '0xde0B295669a9FD93d5F28D9Ec85E40f4cb697BAe',
                      '0x95d4ca7b9c8cc4f00871d95378f94ca24197ee2e']

        # body = rlp.encode(self.public_key.to_hex(), sedes=text) + rlp.encode(self.nonce) + rlp.encode(data, sedes=text) + rlp.encode(now, sedes=text)
        body = self.public_key.to_hex() + str(self.nonce) + data + now + ''.join(validators)
        signatures = [self.sign(body).hex()]
        # print('DEBUG from create_transaction signatures=', signatures)

        # data contains all the fitchain-specific fields (decode and convert to dict)
        print('DEBUG from create_transaction data=', data, type(data))
        tx = Transaction(sender_pk=self.public_key.to_hex(),
                         nonce=str(self.nonce),
                         data=data,
                         timestamp=now,
                         signatures=signatures,
                         validators=validators)

        #print('DEBUG from create_transaction', rlp.encode(tx))
        self.nonce += 1
        return tx


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
