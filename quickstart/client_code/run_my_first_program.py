import asyncio
import py_nillion_client as nillion
import os

from py_nillion_client import NodeKey, UserKey
from dotenv import load_dotenv
from nillion_python_helpers import get_quote_and_pay, create_nillion_client, create_payments_config

from cosmpy.aerial.client import LedgerClient
from cosmpy.aerial.wallet import LocalWallet
from cosmpy.crypto.keypairs import PrivateKey

home = os.getenv("HOME")
load_dotenv(f"{home}/.config/nillion/nillion-devnet.env")

async def main():
    cluster_id = os.getenv("NILLION_CLUSTER_ID")
    grpc_endpoint = os.getenv("NILLION_NILCHAIN_GRPC")
    chain_id = os.getenv("NILLION_NILCHAIN_CHAIN_ID")
    
    seed = "my_seed"
    userkey = UserKey.from_seed(seed)
    nodekey = NodeKey.from_seed(seed)

    client = create_nillion_client(userkey, nodekey)

    party_id = client.party_id
    user_id = client.user_id

    program_name = "my_first_program"
    program_mir_path = f"../nada_quickstart_programs/target/{program_name}.nada.bin"

    payments_config = create_payments_config(chain_id, grpc_endpoint)
    payments_client = LedgerClient(payments_config)
    payments_wallet = LocalWallet(
        PrivateKey(bytes.fromhex(os.getenv("NILLION_NILCHAIN_PRIVATE_KEY_0"))),
        prefix="nillion",
    )

    receipt_store_program = await get_quote_and_pay(
        client,
        nillion.Operation.store_program(program_mir_path),
        payments_wallet,
        payments_client,
        cluster_id,
    )

    action_id = await client.store_program(
        cluster_id, program_name, program_mir_path, receipt_store_program
    )

    program_id = f"{user_id}/{program_name}"

    secret_a = nillion.NadaValues({"A": nillion.SecretInteger(6)})
    permissions_a = nillion.Permissions.default_for_user(client.user_id)
    permissions_a.add_compute_permissions({client.user_id: {program_id}})

    receipt_store_a = await get_quote_and_pay(
        client,
        nillion.Operation.store_values(secret_a, ttl_days=5),
        payments_wallet,
        payments_client,
        cluster_id,
    )

    store_id_a = await client.store_values(
        cluster_id, secret_a, permissions_a, receipt_store_a
    )

    secret_b = nillion.NadaValues({"B": nillion.SecretInteger(7)})
    permissions_b = nillion.Permissions.default_for_user(client.user_id)
    permissions_b.add_compute_permissions({client.user_id: {program_id}})

    receipt_store_b = await get_quote_and_pay(
        client,
        nillion.Operation.store_values(secret_b, ttl_days=5),
        payments_wallet,
        payments_client,
        cluster_id,
    )

    store_id_b = await client.store_values(
        cluster_id, secret_b, permissions_b, receipt_store_b
    )

    secret_c = nillion.NadaValues({"C": nillion.SecretInteger(3)})
    permissions_c = nillion.Permissions.default_for_user(client.user_id)
    permissions_c.add_compute_permissions({client.user_id: {program_id}})

    receipt_store_c = await get_quote_and_pay(
        client,
        nillion.Operation.store_values(secret_c, ttl_days=5),
        payments_wallet,
        payments_client,
        cluster_id,
    )

    store_id_c = await client.store_values(
        cluster_id, secret_c, permissions_c, receipt_store_c
    )

    compute_bindings = nillion.ProgramBindings(program_id)
    compute_bindings.add_input_party("Party1", party_id)
    compute_bindings.add_input_party("Party2", party_id)
    compute_bindings.add_input_party("Party3", party_id)
    compute_bindings.add_output_party("Party3", party_id)

    receipt_compute = await get_quote_and_pay(
        client,
        nillion.Operation.compute(program_id, nillion.NadaValues({})),
        payments_wallet,
        payments_client,
        cluster_id,
    )

    compute_id = await client.compute(
        cluster_id,
        compute_bindings,
        [store_id_a, store_id_b, store_id_c],
        nillion.NadaValues({}),
        receipt_compute,
    )

    while True:
        compute_event = await client.next_compute_event()
        if isinstance(compute_event, nillion.ComputeFinishedEvent):
            print(compute_event.result.value['my_output'])
            return compute_event.result.value['my_output']

if __name__ == "__main__":
    asyncio.run(main())
