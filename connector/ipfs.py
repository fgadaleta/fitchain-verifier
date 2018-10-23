# import json
import os
# import sys
import ipfsapi
# import _pickle
import logging

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class IPFS:
    """ IPFS interface to read/write assets from the fitchain network """
    def __init__(self, ipfs_config):
        self.ipfs_config = ipfs_config
        log.info('Connecting to IPFS node... at %s:%s', self.ipfs_config['server'], self.ipfs_config['port'])
        try:
            self.ipfs_conn = ipfsapi.connect(self.ipfs_config['server'], self.ipfs_config['port'])
        except Exception:
            log.info('IPFS Daemon does not seem to be running (Hint: launch ipfs daemon)')
            exit(1)
        # Create IPFS local storage for models
        if not os.path.exists(self.ipfs_config['data_path']):
            log.info("Local storage path does not exist... creating")
            os.makedirs(self.ipfs_config['data_path'])

    def to_bytes(self, string, encoding="utf-8"):
        return bytes(string, encoding)

    def check_type(self, variable, type):
        if not isinstance(variable, type):
            variable = self.to_bytes(variable)
        return variable

    def store_file(self, filename):
        """
        Store filename to IPFS
        Return hash ipfs address
        """
        return self.ipfs_conn.add(filename)

    def store_object(self, obj):
        """
        Store string and bytes to IPFS and return hash address
        @param isfile - pickle|joblib

        Return hash of stored object (as bytes) or false if obj is something else
        """

        if os.path.isfile(obj):
            res = self.store_file(obj)
            return self.check_type(res['Hash'], bytes)

        if isinstance(obj, str):
            obj_hash = self.check_type(self.ipfs_conn.add_str(obj), bytes)
            return obj_hash

        if isinstance(obj, bytes):
            obj_hash = self.check_type(self.ipfs_conn.add_bytes(obj), bytes)
            return obj_hash

        if isinstance(obj, object):
            obj_hash = self.check_type(self.ipfs_conn.add_pyobj(obj), bytes)
            return obj_hash

        return False

    def get_obj(self, ipfs_address):
        return self.ipfs_conn.cat(ipfs_address)
