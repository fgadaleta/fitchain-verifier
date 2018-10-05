from ecies import encrypt, decrypt
from eth_keys import keys, KeyAPI
from ethereum import Account


if __name__ == "__main__":
    pk_from_disk = b'\xb3\x07\xae\x02&\x00g \xa8\xf5w*O.|\x8a\xae\xb1\xf3\xf6\xf7op\x90>\xad\xdfo\x1e:\xd0\x16'
    verifier = Account(pk_from_disk)
    message = b"hello world!"
    print('Verifier ', verifier)

    sig = verifier.sign(message)
    print('Signature ', sig)

    enc_msg = verifier.encrypt(message)
    print('Encrypted msg ', enc_msg)

    dec_msg = verifier.decrypt(enc_msg)
    print('Decrypted msg ', dec_msg)
