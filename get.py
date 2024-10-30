from pdb import set_trace as bp
import asyncio
import base64
from dotenv import load_dotenv
import json
import os
import tempfile
import sys

import ipfs_api


from buffered_encryption.aesgcm import DecryptionIterator


import py_nillion_client as nillion
from py_nillion_client import NodeKey, UserKey

from cosmpy.aerial.client import LedgerClient
from cosmpy.aerial.wallet import LocalWallet
from cosmpy.crypto.keypairs import PrivateKey

from nillion_python_helpers import (
    get_quote_and_pay,
    create_nillion_client,
    create_payments_config,
)

# default project env
load_dotenv()

# default nillion devnet
home = os.getenv("HOME")
load_dotenv(f"{home}/.config/nillion/nillion-devnet.env")


async def decrypt(store_id: str):
    cluster_id = os.getenv("NILLION_CLUSTER_ID")
    grpc_endpoint = os.getenv("NILLION_NILCHAIN_GRPC")
    chain_id = os.getenv("NILLION_NILCHAIN_CHAIN_ID")

    seed = os.getenv("NILLION_USERKEY_SEED")
    userkey = UserKey.from_seed(seed)
    nodekey = NodeKey.from_seed(seed)

    nilvm = create_nillion_client(userkey, nodekey)

    payments_config = create_payments_config(chain_id, grpc_endpoint)
    payments_client = LedgerClient(payments_config)
    payments_wallet = LocalWallet(
        PrivateKey(bytes.fromhex(os.getenv("NILLION_NILCHAIN_PRIVATE_KEY_0"))),
        prefix="nillion",
    )

    receipt_retrieve = await get_quote_and_pay(
        nilvm,
        nillion.Operation.retrieve_value(),
        payments_wallet,
        payments_client,
        cluster_id,
    )

    result_tuple = await nilvm.retrieve_value(
        cluster_id, store_id, "ipfs", receipt_retrieve
    )

    decoded_secret_value = result_tuple[1].value.decode("utf-8")
    print(f"The nillion secret value is '{decoded_secret_value}'")

    payload = json.loads(decoded_secret_value)

    key = base64.b64decode(payload["key"])
    sig = base64.b64decode(payload["sig"])
    iv = base64.b64decode(payload["iv"])
    tag = base64.b64decode(payload["tag"])

    ciphertext = tempfile.NamedTemporaryFile(delete=False).name
    ipfs_api.download(payload["cid"], ciphertext)
    ciphertext_fh = open(ciphertext, "rb")

    target_filepath = os.path.join(tempfile.mkdtemp(), payload["filename"])

    dec = DecryptionIterator(ciphertext_fh, key, sig, iv, tag)
    with open(target_filepath, "wb") as decrypted:
        for chunk in dec:
            decrypted.write(chunk)

    print(f"file decrypted to: [{target_filepath}]")


loop = asyncio.get_event_loop()
loop.run_until_complete(decrypt(sys.argv[1]))
