import pytest
from connector.ipfs import IPFS
from connector.config.ipfs_config import IPFS_CONFIG

ipfs = IPFS(ipfs_config=IPFS_CONFIG['LOCAL'])


def test_store_object():
    str_obj = "hello world"
    hash = ipfs.store_object(str_obj)
    print('Stored obj=%s to %s' % (str_obj, hash))
    assert hash == b'Qmf412jQZiuVUtdgnB36FXFX7xg5V6KEbSJ4dpQuhkLyfD'

    byte_obj = b'hello world'
    hash = ipfs.store_object(byte_obj)
    print('Stored obj=%s to %s' % (byte_obj, hash))
    assert hash == b'Qmf412jQZiuVUtdgnB36FXFX7xg5V6KEbSJ4dpQuhkLyfD'


def test_store_file():
    pass
