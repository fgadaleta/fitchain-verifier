import pytest
import os
import inspect
import sys

from account.ethereum import Account


def test_sign_verify():
    # load private key from disk to account
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

    assert dec_msg == message

    pub_key = verifier.extract_pubkey_from_signature(message, sig.to_bytes())
    print('Recovered pub_key ', pub_key)
    is_valid = verifier.verify_sig_msg(message, sig.to_bytes(), pub_key.to_bytes())
    assert is_valid == True
