[![banner](https://github.com/fitchain/art/blob/master/fitchain-banner.png)](https://fitchain.io)

# Fitchain Verifier

>    🐳  [Description of repo](https://www.elastic.co/) component for (Python).
>    [fitchain.io](https://fitchain.io)

TODO Change this to match the repo name and testing environments

[![Travis (.com)](https://img.shields.io/travis/com/oceanprotocol/oceandb-elasticsearch-driver.svg)](https://travis-ci.com/oceanprotocol/oceandb-elasticsearch-driver)
[![Codacy coverage](https://img.shields.io/codacy/coverage/de067a9402c64b989c76b27cfc74fefe.svg)](https://app.codacy.com/project/ocean-protocol/oceandb-elasticsearch-driver/dashboard)
[![PyPI](https://img.shields.io/pypi/v/oceandb-elasticsearch-driver.svg)](https://pypi.org/project/oceandb-elasticsearch-driver/)
[![GitHub contributors](https://img.shields.io/github/contributors/oceanprotocol/oceandb-elasticsearch-driver.svg)](https://github.com/oceanprotocol/oceandb-elasticsearch-driver/graphs/contributors)

---

## Table of Contents

  - [Features](#features)
  - [Prerequisites](#prerequisites)
  - [Quickstart](#quickstart)
  - [Environment variables](#environment-variables)
  - [Code style](#code-style)
  - [Testing](#testing)
  - [New Version](#new-version)
  - [License](#license)

---

## Features

The _fitchain verifier_ provides an interface (Python) to the smart contracts of the fitchain network (Registry and Validator Pool Contract). It also provides a Python interface to IPFS in order to store and retrieve assets in and from the fitchain network (and the other networks connected to).

## Prerequisites

You should have running *geth* or *ganache-cli* (for testing local blockchain) and IPFS daemon.

### WARNING

In order to keep the same configuration and the same addresses for contracts and accounts, run ganache in deterministic
mode with

` $ ganache-cli -d 42 `


## Quickstart

`$ pytest tests`


## Environment variables

The address of both VPC and Registry contracts can be configured from `connector/config/vpc_config.py` and `connector/config/registry_config.py` (Default configuration has been set with a fake pub,priv keypair generated from `ganache-cli`. DO NOT USE for public blockchains)

IPFS can be configured from `connector/config/ipfs_config.py`


## Sample use case

### Compute provider
Compute provider trains an image classifier on a private dataset and stores the trained model to IPFS

```Python
from connector.ipfs import IPFS
from connector.config.ipfs_config import IPFS_CONFIG

ipfs = IPFS(ipfs_config=IPFS_CONFIG['LOCAL'])
hash = ipfs.store_file('./model_params.h5')
```

or using ipfs cli

```
$ ipfs add model_params.h5
added QmRcs8Fa7r2749akdsM55AeyEZ6E8NYAENcw5tDt7TEXp1 model_params.h5
```

_Compute provider_ provides a `model_schema.json` as below

```Javascript
{
  "uuid": "0x0123456789",
  "type": "keras",
  "input_signature": "hgGDH7843hjds",
  "stored_as": "file",
  "format": "h5",
  "location" :
  [
    {
      "provider": "ipfs",
      "endpoint": "QmRcs8Fa7r2749akdsM55AeyEZ6E8NYAENcw5tDt7TEXp1"
    }
  ]
}
```

### Data Curator
A data curator (or equivalently a _data provider_) provides a testing dataset compatible with the training dataset used by compute provider. Such dataset is also stored to IPFS. A data schema is provided as below

```$ ipfs add testing_data.csv
   Qm...
```


```Javascript
{
  "uuid": "0x0123456789",
  "type": "collection",
  "input_signature": "hgGDH7843hjds",
  "stored_as": "csv",
  "location" :
  {
    "provider": "ipfs",
    "endpoint": "Qm..."
  }
}
```


### Model Verifier
A model verifier resolves a pending challenge for a model that has been previously trained.
Verifier performs the steps below
1. fetch model and testing data from the two json schemas attached to the challenge
2. perform model on testing data (off-chain computation)
3. updates VPC/Registry contracts with the obtained model metrics

```$ ipfs cat Qm...
   Qm...
```


```Python
# Load existing model
from keras.models import load_model
model = load_model('./model_params.h5')
model.summary()
```

## Code style

The information about code style in python is documented in this two links [python-developer-guide](https://github.com/oceanprotocol/dev-ocean/blob/master/doc/development/python-developer-guide.md)
and [python-style-guide](https://github.com/oceanprotocol/dev-ocean/blob/master/doc/development/python-style-guide.md).

## Testing

Our test use pytest framework.

## New Version

The `bumpversion.sh` script helps to bump the project version. You can execute the script using as first argument {major|minor|patch} to bump accordingly the version.

## License

```
Copyright 2018 Amethix Technologies

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
