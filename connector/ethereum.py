import json
import os
import sys
from web3 import Web3
import ipfsapi
import _pickle
import logging

log = logging.getLogger(__name__)


class Contract:
    def __init__(self, eth_config, abi_file):
        self.eth_config = eth_config
        url = self.eth_config['server']+':'+str(self.eth_config['port'])
        self.web3 = Web3(Web3.HTTPProvider(url, request_kwargs={'timeout': 60}))
        self.eth_account = None
        log.info('Loading ABIs...')
        self.contract_abi = self.__read_abi(abi_file)
        log.info('ABIs loaded successfully')
        # getting registry contract
        self.contract_address = self.eth_config['contract_addr']  # addresses must have a checksum EIP-55
        self.contract_address = Web3.toChecksumAddress(self.contract_address)
        self.contract = self.web3.eth.contract(abi=self.contract_abi,
                                               address=self.contract_address)
        log.info('Smart contract instantiated successfully')

    def to_bytes(self, string, encoding="utf-8"):
        return bytes(string, encoding)

    def check_type(self, variable, type):
        if not isinstance(variable, type):
            variable = self.to_bytes(variable)
        return variable

    @property
    def account(self):
        return self.eth_account

    @account.setter
    def account(self, account):
        self.eth_account = account

    def __read_abi(self, file: str) -> str:
        abifile = "%s.json" % file
        with open(os.path.join(self.eth_config['abi'], abifile), encoding='utf-8') as f:
            artifact = json.load(f)
        return artifact['abi']

    def __new_block_callback(block_hash):
        sys.stdout.write("New Block: {0}".format(block_hash))


class VpcContract(Contract):
    """
    VPC contract interface
    """
    def __init__(self, eth_config, abi_file):
        Contract.__init__(self, eth_config, abi_file)
        print('[Contract VPC]\t\tConnecting to Ethereum node on %s:%d...' %
              (self.eth_config['server'], self.eth_config['port']))

    @property
    def channels(self):
        return self.contract.call().getNumberOfChannels()

    def init_channel(self, model_id, k: int):
        model_id = self.check_type(model_id, bytes)
        transact_params = {
            'from': self.eth_account,
        }
        try:
            tx = self.contract.transact(transact_params).initChannel(model_id, int(k))
        except:
            return None
        return tx

    @property
    def verifiers(self):
        return self.contract.call().getRegistrants()

    @property
    def nverifiers(self):
        return self.contract.call().getNumberRegistrants()

    def deposit(self, mindeposit=12000000000000000000):
        if not self.eth_account:
            return "Set account first"

        transact_params = {
            'from': self.eth_account,
            'value': mindeposit,
        }

        tx = self.contract.transact(transact_params).deposit()
        return tx

    def is_channel(self, channel_id):
        channel_id = self.check_type(channel_id, bytes)
        tx = self.contract.call().isChannel(channel_id)
        return tx

    def get_channel(self, channel_id):
        channel_id = self.check_type(channel_id, bytes)
        model_id, k = self.contract.call().getChannel(channel_id)
        return model_id, k

    def submit_proof(self, model_id: bytes, merkleroot: bytes, sigs: list):
        model_id = self.check_type(model_id, bytes)
        merkleroot = self.check_type(merkleroot, bytes)
        sigs = [self.to_bytes(s) for s in sigs]
        transact_params = {
            'from': self.eth_account,
        }
        tx = self.contract.transact(transact_params).submitProof(model_id, merkleroot, sigs)
        return tx

    def nproofs(self, model_id):
        """ Return number of proofs submitted for model_id """
        model_id = self.check_type(model_id, bytes)
        # this is faster (but we don't pay gas for this)
        # return self.contract.call().getProofCount(model_id)
        return len(self.get_proofs(model_id))

    def get_proofs(self, model_id):
        """ Return: dict {proof_key} -> (sender, merkleroot, sigs) for model_id """
        model_id = self.check_type(model_id, bytes)
        proof_keys = self.contract.call().getProofsList(model_id)
        proofs = {}
        for pk in proof_keys:
            proofs[pk] = {}
            proofs[pk]['sender'], proofs[pk]['merkleroot'], proofs[pk]["sigs"] = \
                self.contract.call().getProof(model_id, pk)
        return proofs

    def is_model_valid(self, model_id):
        model_id = self.check_type(model_id, bytes)
        is_valid = self.contract.call().isPotValid(model_id)
        return is_valid


class RegistryContract(Contract):
    def __init__(self, eth_config, abi_file):
        Contract.__init__(self, eth_config, abi_file)
        print('[Contract Registry]\tConnecting to Ethereum node on %s:%d...' %
              (self.eth_config['server'], self.eth_config['port']))

    @property
    def models(self):
        return self.contract.call().getNumberOfModels()

    def challenges(self, model_id):
        model_id = self.check_type(model_id, bytes)
        return self.contract.call().getNumberOfChallenges(model_id)

    def create_model(self, model_id, ipfs_addr, stored_as, bounty, current_error, target_error):
        """
        Add model to blockchain registry
        @param model filename where model is stored (pickle) """

        # FIXME bring this out
        """
        model_id, stored_as = self.__store_object(model, isfile)
        ipfs_addr_first, ipfs_addr_second = IPFSAddress().to_ethereum(model_id)
        print('DEBUG from createModel():', model_id, ipfs_addr_first, ipfs_addr_second)
        """
        model_id = self.check_type(model_id, bytes)
        ipfs_addr = self.check_type(ipfs_addr, bytes)
        stored_as = int(stored_as)
        bounty = int(bounty)
        current_error = int(current_error)
        target_error = int(target_error)
        """
        res = self.contract.call().createModel(model_id,
                                               ipfs_addr,
                                               stored_as,
                                               bounty,
                                               current_error,
                                               target_error)
        print('DEBUG from createModel()', res)
        """
        transact_params = {
            'from': self.account
        }
        tx = self.contract.transact(transact_params).createModel(model_id,
                                                                 ipfs_addr,
                                                                 stored_as,
                                                                 bounty,
                                                                 current_error,
                                                                 target_error)
        print('tx =', tx.hex())
        return {'model_id': model_id, 'stored_as': stored_as, 'tx': tx}

    def get_model(self, model_id):
        """ Retrieve model from model_id and return owner, ipfs_address (merged from array of bytes32)
        and other metadata
        """
        model_id = self.check_type(model_id, bytes)
        owner_address, ipfs_addr, stored_as, bounty, current_error, target_error, is_valid = \
            self.contract.call().getModel(model_id)

        res = {}
        res['owner_address'] = owner_address
        res['ipfs_addr'] = ipfs_addr
        res['stored_as'] = stored_as
        res['bounty'] = bounty
        res['current_error'] = current_error
        res['target_error'] = target_error
        res['is_valid'] = is_valid
        return res

    def create_challenge(self, model_id, validation_data_addr, isfile=False, file_format='pickle', verbose=False):
        """
        Create challenge for model_id
        @params model_id <str> - model unique identifier
        @params validation_data_addr <file> - filename where validset is stored
        @params isfile <boolean> - must be True for files
        @params file_format <string> - pickle | txt | custom schema provided as a dict
        """
        model_id = self.check_type(model_id, bytes)
        validation_data_addr = self.check_type(validation_data_addr, bytes)

        # FIXME out to IPFS
        # validation_data_address, stored_as = self.__store_object(validation_data_addr, isfile)
        # address_first, address_second = IPFSAddress().to_ethereum(validation_data_address)
        # self.fitchain_contract.call().createChallenge(model_id, address_first, address_second)
        # TODO capture event from createChallenge()

        # self.get_transaction(self.account).createChallenge(model_id, address_first, address_second)
        transact_params = {
            'from': self.account,
        }
        tx = self.contract.transact(transact_params).createChallenge(model_id, validation_data_addr)
        return tx

    def __get_challenge(self, challenge_hash):
        """
        @params challenge_hash (bytes32)
        """
        challenge = {}
        res = self.contract.call().getChallenge(challenge_hash)
        challenge['model_id'] = res[0]
        challenge['verifier_address'] = res[1]
        challenge['ipfs_address'] = res[2]
        challenge['error_metric'] = res[3]
        challenge['is_active'] = res[4]
        challenge['validator_addr'] = res[5]
        return challenge

    def get_model_challenges(self, model_id):
        """
        Return all challenges (metadata) of this model_id
        @params model_id (bytes)
        """

        retrieved = []
        model_id = self.check_type(model_id, bytes)
        challenges = self.contract.call().getModelChallenges(model_id)
        for c_hash in challenges:
            retrieved.append(self.__get_challenge(c_hash))

        return retrieved
