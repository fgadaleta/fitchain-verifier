from config import eth, ipfs
from web3 import Web3
from ethereum import VpcContract, RegistryContract
from config.vpc_config import VPC_CONFIG
from config.registry_config import REG_CONFIG

w3 = Web3(Web3.HTTPProvider("http://localhost:8545", request_kwargs={'timeout': 60}))

# Instantiate VPC contract
vpc = VpcContract(eth_config=VPC_CONFIG['LOCAL'], abi_file='Vpc')
vpc.account = w3.eth.accounts[0]
vpc.deposit()

# Instantiate Registry contract
registry = RegistryContract(eth_config=REG_CONFIG['LOCAL'], abi_file="Registry")
registry.account = w3.eth.accounts[0]

# Set verifier accounts (if not already)
naccounts = len(w3.eth.accounts)
for i in range(naccounts):
    vpc.account = w3.eth.accounts[i]
    vpc.deposit()



v = vpc.verifiers
print("verifiers=", v)

nv = vpc.nverifiers
print('num_verifiers=', nv)
