import pytest
# import os
# import inspect
# import sys

from account.ethereum import Account


def test_sign_verify():
    # load private key from disk to account
    pk_from_disk = bytes.fromhex('4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d')
    verifier = Account(pk_from_disk)
    message = b"hello world!"
    print('Verifier ', verifier)

    sig = verifier.sign(message)
    print('Signature ', sig)

    enc_msg = verifier.encrypt(message)
    print('Encrypted msg ', enc_msg)

    dec_msg = verifier.decrypt(enc_msg)
    print('Decrypted msg ', dec_msg)

    assert dec_msg == message

    pub_key = verifier.extract_pubkey_from_signature(message, sig.to_bytes())
    print('Recovered pub_key ', pub_key)
    is_valid = verifier.verify_sig_msg(message, sig.to_bytes(), pub_key.to_bytes())
    # assert 0
    assert is_valid == True
