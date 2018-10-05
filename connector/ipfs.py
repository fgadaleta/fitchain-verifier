import json
import os
import sys
import ipfsapi
import _pickle
import logging

log = logging.getLogger(__name__)


class IPFS:
    """ IPFS interface to read/write assets from the fitchain network """
    def __init__(self, ipfs_config):
        self.ipfs_config = ipfs_config
        print('Connecting to IPFS node... at %s:%s'%(self.ipfs_config['server'], self.ipfs_config['port']))
        try:
            self.ipfs_conn = ipfsapi.connect(self.ipfs_config['server'], self.ipfs_config['port'])
        except:
            print('IPFS Daemon does not seem to run (check ipfs config)')
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

    """
    Get object from IPFS as a stream of bytes and write to outfile
    @param meta <dict>    - metadata of stuff saved to ipfs
    @param outfile <str>  - filename to save to (optional)
    @param load <bool>    - load into memory and return
    @param storedas <str> - file stored as joblib|pickle|plain

    Return: filename storing stuff
    """
    """
    def get_remote_obj(self, meta, outfile=None, load=False):
        ipfs_addr = meta['ipfs_address'].decode() # FIXME is this always bytes (??)
        if 'stored_as' in meta:
            stored_as = meta['stored_as']
        else:
            stored_as = storedAs.joblib

        print('stored_as=', stored_as)

        # stuff is stored as file or unknown (store to file by default)
        if stored_as == storedAs.pickle or stored_as == storedAs.joblib:
            # if not provided use this obj hash
            if outfile is None:
                outfile = str(ipfs_addr)
            filepath = os.path.join(self.ipfs_config['data_path'], outfile)
            try:
                with open(filepath, 'wb') as f:
                    f.write(self.ipfs_conn.cat(ipfs_addr))
                    print('Remote object correctly saved at %s'%filepath)
            except:
                return False

            # load into memory and return
            if load:
                if stored_as == storedAs.joblib:
                    return joblib.load(filepath)
                if stored_as == storedAs.pickle:
                    with open(filepath, "rb") as input_file:
                        return _pickle.load(input_file)
            else:
                return outfile

        if stored_as == storedAs.unknown:
            pass
        if stored_as == storedAs.object:
            pass
        return None
    """
