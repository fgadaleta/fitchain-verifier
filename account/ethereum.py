from eth_keys import keys, KeyAPI
from account.ecies import encrypt, decrypt
import logging
import sha3

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
        return self.privkey.public_key

    @property
    def address(self):
        return self.public_key.to_address()

    def hash(self, message: bytes):
        keccak = sha3.keccak_256()
        keccak.update(message)
        return keccak.hexdigest()

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
