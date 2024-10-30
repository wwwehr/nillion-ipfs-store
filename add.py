from pdb import set_trace as bp
import asyncio
import base64
from dotenv import load_dotenv
import json
import os
import tempfile
import sys

import ipfs_api


from buffered_encryption.aesgcm import EncryptionIterator


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


async def encrypt(files: list):
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

    for filename in files:
        key = os.urandom(32)
        sig = os.urandom(12)

        plaintext = open(filename, "rb+")
        enc = EncryptionIterator(plaintext, key, sig)
        ciphertext = tempfile.NamedTemporaryFile(mode="wb+", delete=False)

        for chunk in enc:
            ciphertext.write(chunk)
        ciphertext.close()

        # file is encrypted, ready to push to ipfs
        print(f"sending {ciphertext.name} to ipfs (agent id:{ ipfs_api.my_id() })")

        # Connecting to local Kubo node (go-ipfs, flatpak app, etc)

        cid = ipfs_api.publish(ciphertext.name)
        print(f"stored to ipfs cid {cid}")
        payload = {
            "cid": cid,
            "filename": os.path.basename(filename),
            "size": os.path.getsize(filename),
            "key": base64.b64encode(key).decode(),
            "sig": base64.b64encode(sig).decode(),
            "iv": base64.b64encode(enc.iv).decode(),
            "tag": base64.b64encode(enc.tag).decode(),
        }

        stored_secret = nillion.NadaValues(
            {
                "ipfs": nillion.SecretBlob(bytearray(json.dumps(payload), "utf-8")),
            }
        )

        permissions = nillion.Permissions.default_for_user(nilvm.user_id)
        receipt_store = await get_quote_and_pay(
            nilvm,
            nillion.Operation.store_values(stored_secret, ttl_days=5),
            payments_wallet,
            payments_client,
            cluster_id,
        )

        # Store a secret, passing in the receipt that shows proof of payment
        store_id = await nilvm.store_values(
            cluster_id, stored_secret, permissions, receipt_store
        )

        print(f"The secret is stored at store_id: {store_id}")

        os.remove(ciphertext.name)
        plaintext.close()


loop = asyncio.get_event_loop()
loop.run_until_complete(encrypt(sys.argv[1:]))
