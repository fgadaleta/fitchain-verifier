from eth_keys import keys, KeyAPI
from account.ecies import encrypt, decrypt
import logging

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

class Account:

    def __init__(self, private_key: bytes):
        self.privkey = KeyAPI.PrivateKey(private_key)

    def __repr__(self):
        return self.privkey.public_key.to_hex()

    def __str__(self):
         return self.privkey.public_key.to_hex()

    @property
    def public_key(self):
        return self.privkey.public_key.to_bytes()

    def encrypt(self, message, dest_public_key=None):
        """Encrypt with this pubkey or the pubkey of another account

        Args:
            message: The message to encrypt (plaintext)
            dest_public_key: The public key to encrypt the message with

        Returns:
            Bytes of the encrypted message.

        Raises:
            EncryptionError
        """

        if dest_public_key:
            return encrypt(message, dest_public_key)
        return encrypt(message, self.privkey.public_key)

    def decrypt(self, enc_message):
        """Decrypt the encrypted message with the private key of this Account

        Args:
            enc_message: The encrypted message to decrypt (cyphertext)

        Returns:
            Bytes of the plaintext message.

        Raises:
            DecryptionError
        """

        return decrypt(enc_message, self.privkey)

    def sign(self, message: bytes)->bytes:
        return self.privkey.sign_msg(message)

    def verify_sig_msg(self, message: bytes, signature: bytes, pubkey: bytes):
        """ Verifies that message has been signed by pubkey """

        public_key = KeyAPI.PublicKey(pubkey)
        sig = KeyAPI.Signature(signature)
        return sig.verify_msg(message, public_key)

    def extract_pubkey_from_signature(self, message: bytes, signature: bytes):
        """ Recover pubkey that signed message """

        sig = KeyAPI.Signature(signature)
        recovered_pk = sig.recover_public_key_from_msg(message)
        return recovered_pk

    def verify_sig_msg_hash(self, msg_hash: bytes, signature: bytes, pubkey: bytes):
        public_key = KeyAPI.PublicKey(pubkey)
        sig = KeyAPI.Signature(signature)
        return sig.verify_msg_hash(msg_hash, public_key)


















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
