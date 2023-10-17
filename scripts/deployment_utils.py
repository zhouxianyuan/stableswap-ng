from dataclasses import dataclass
from typing import List

import click
from ape import networks, project
from ape.api.address import Address
from eth_utils import function_signature_to_4byte_selector

DOLLAR_VALUE_OF_TOKENS_TO_DEPOSIT = 5
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"


def _get_tx_params():

    if "mainnet-fork" == networks.active_provider.network.name:
        return {}

    if "sepolia" == networks.active_provider.network.name:
        return {}

    active_provider = networks.active_provider
    max_fee = int(active_provider.base_fee * 1.2)
    max_priority_fee = int(0.5e9)

    return {"max_fee": max_fee, "max_priority_fee": max_priority_fee}


def deploy_blueprint(contract, account):

    initcode = contract.contract_type.deployment_bytecode.bytecode
    if isinstance(initcode, str):
        initcode = bytes.fromhex(initcode.removeprefix("0x"))
    initcode = b"\xfe\x71\x00" + initcode  # eip-5202 preamble version 0
    initcode = b"\x61" + len(initcode).to_bytes(2, "big") + b"\x3d\x81\x60\x0a\x3d\x39\xf3" + initcode

    tx = project.provider.network.ecosystem.create_transaction(
        chain_id=project.provider.chain_id,
        data=initcode,
        gas_price=project.provider.gas_price,
        nonce=account.nonce,
        **_get_tx_params(),
    )
    receipt = account.call(tx)
    click.echo(f"blueprint deployed at: {receipt.contract_address}")
    return receipt.contract_address


# ------ IMMUTABLES ------


GAUGE_CONTROLLER = "0x2F50D538606Fa9EDD2B11E2446BEb18C9D5846bB"
ADDRESS_PROVIDER = "0x0000000022d53366457f9d5e68ec105046fc4383"
FIDDYRESEARCH = "0xE6DA683076b7eD6ce7eC972f21Eb8F91e9137a17"
FIDDYDEPLOYER = "0x2d12D0907A388811e3AA855A550F959501d303EE"


# -------------- CURVE DATA --------------


@dataclass
class CurveNetworkSettings:
    dao_ownership_contract: Address
    fee_receiver_address: Address
    metaregistry_address: Address = ""
    base_pool_registry_address: Address = ""
    address_provider: Address = "0x0000000022d53366457f9d5e68ec105046fc4383"


curve_dao_network_settings = {
    "ethereum:mainnet": CurveNetworkSettings(
        dao_ownership_contract="0x40907540d8a6C65c637785e8f8B742ae6b0b9968",
        fee_receiver_address="0xeCb456EA5365865EbAb8a2661B0c503410e9B347",
        metaregistry_address="0xF98B45FA17DE75FB1aD0e7aFD971b0ca00e379fC",
        base_pool_registry_address="0xDE3eAD9B2145bBA2EB74007e58ED07308716B725",
    ),
    "ethereum:mainnet-fork": CurveNetworkSettings(
        dao_ownership_contract="0x40907540d8a6C65c637785e8f8B742ae6b0b9968",
        fee_receiver_address="0xeCb456EA5365865EbAb8a2661B0c503410e9B347",
        metaregistry_address="0xF98B45FA17DE75FB1aD0e7aFD971b0ca00e379fC",
        base_pool_registry_address="0xDE3eAD9B2145bBA2EB74007e58ED07308716B725",
    ),
    "ethereum:sepolia": CurveNetworkSettings(
        dao_ownership_contract="0xE6DA683076b7eD6ce7eC972f21Eb8F91e9137a17",
        fee_receiver_address="0xE6DA683076b7eD6ce7eC972f21Eb8F91e9137a17",
    ),
    "arbitrum:mainnet": CurveNetworkSettings(
        dao_ownership_contract="0xb055ebbacc8eefc166c169e9ce2886d0406ab49b",
        fee_receiver_address="0xd4f94d0aaa640bbb72b5eec2d85f6d114d81a88e",
    ),
    "optimism:mainnet": CurveNetworkSettings(
        dao_ownership_contract="0xB055EbbAcc8Eefc166c169e9Ce2886D0406aB49b",
        fee_receiver_address="0xbF7E49483881C76487b0989CD7d9A8239B20CA41",
    ),
    "polygon:mainnet": CurveNetworkSettings(
        dao_ownership_contract="0xB055EbbAcc8Eefc166c169e9Ce2886D0406aB49b",
        fee_receiver_address="0x774D1Dba98cfBD1F2Bc3A1F59c494125e07C48F9",
    ),
    "avalanche:mainnet": CurveNetworkSettings(
        dao_ownership_contract="0xbabe61887f1de2713c6f97e567623453d3c79f67",
        fee_receiver_address="0x06534b0BF7Ff378F162d4F348390BDA53b15fA35",
    ),
    "gnosis:mainnet": CurveNetworkSettings(
        dao_ownership_contract="0xB055EbbAcc8Eefc166c169e9Ce2886D0406aB49b",  # <--- need to deploy sidechain ownership contract  # noqa: E501
        fee_receiver_address="0xB055EbbAcc8Eefc166c169e9Ce2886D0406aB49b",  # <--- need to deploy sidechain pool proxy
    ),
    "fantom:mainnet": CurveNetworkSettings(
        dao_ownership_contract="0xB055EbbAcc8Eefc166c169e9Ce2886D0406aB49b",  # <--- thin proxy  # noqa: E501
        fee_receiver_address="0x2B039565B2b7a1A9192D4847fbd33B25b836B950",
    ),
    "celo:mainnet": CurveNetworkSettings(
        dao_ownership_contract="0x56bc95Ded2BEF162131905dfd600F2b9F1B380a4",  # <-- needs to accept transfer ownership for 0x5277A0226d10392295E8D383E9724D6E416d6e6C  # noqa: E501
        fee_receiver_address="",
    ),
    "kava:mainnet": CurveNetworkSettings(
        dao_ownership_contract="",
        fee_receiver_address="",
    ),
    "moonbeam": CurveNetworkSettings(
        dao_ownership_contract="",
        fee_receiver_address="",
    ),
    "aurora": CurveNetworkSettings(
        dao_ownership_contract="",
        fee_receiver_address="",
    ),
}


CURVE_DAO_OWNERSHIP = {
    "agent": "0x40907540d8a6c65c637785e8f8b742ae6b0b9968",
    "voting": "0xe478de485ad2fe566d49342cbd03e49ed7db3356",
    "token": "0x5f3b5DfEb7B28CDbD7FAba78963EE202a494e2A2",
    "quorum": 30,
}

# ------------- BASE POOLS ---------------


@dataclass
class BasePoolSettings:
    pool: Address
    lp_token: Address
    coins: List[Address]
    asset_types: List[int]
    n_coins: int


_base_pool_list = {
    "ethereum:mainnet": [
        BasePoolSettings(  # 3pool
            pool="0xbEbc44782C7dB0a1A60Cb6fe97d0b483032FF1C7",
            lp_token="0x6c3F90f043a72FA612cbac8115EE7e52BDe6E490",
            coins=[
                "0x6B175474E89094C44Da98b954EedeAC495271d0F",  # dai
                "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",  # usdc
                "0xdAC17F958D2ee523a2206206994597C13D831ec7",  # usdt
            ],
            asset_types=[0, 0, 0],
            n_coins=3,
        ),
        BasePoolSettings(  # fraxusdc
            pool="0xDcEF968d416a41Cdac0ED8702fAC8128A64241A2",
            lp_token="0x3175Df0976dFA876431C2E9eE6Bc45b65d3473CC",
            coins=[
                "0x853d955aCEf822Db058eb8505911ED77F175b99e",  # frax
                "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",  # usdc
            ],
            asset_types=[0, 0],
            n_coins=2,
        ),
        BasePoolSettings(  # sbtc/wbtc
            pool="0xf253f83AcA21aAbD2A20553AE0BF7F65C755A07F",
            lp_token="0x051d7e5609917Bd9b73f04BAc0DED8Dd46a74301",
            coins=[
                "0xfE18be6b3Bd88A2D2A7f928d00292E7a9963CfC6",  # sbtc
                "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",  # wbtc
            ],
            asset_types=[0, 0],
            n_coins=2,
        ),
        BasePoolSettings(
            pool="0xaE34574AC03A15cd58A92DC79De7B1A0800F1CE3",
            lp_token="0xFC2838a17D8e8B1D5456E0a351B0708a09211147",
            coins=[
                "0x853d955aCEf822Db058eb8505911ED77F175b99e",  # frax
                "0x8E870D67F660D95d5be530380D0eC0bd388289E1",  # usdp
            ],
            asset_types=[0, 0],
            n_coins=2,
        ),
    ],
    "arbitrum:mainnet": [],
    "optimism:mainnet": [],
    "gnosis:mainnet": [
        BasePoolSettings(
            pool="0x7f90122bf0700f9e7e1f688fe926940e8839f353",
            lp_token="0x1337BedC9D22ecbe766dF105c9623922A27963EC",
            coins=[
                "0xe91D153E0b41518A2Ce8Dd3D7944Fa863463a97d",
                "0xDDAfbb505ad214D7b80b1f830fcCc89B60fb7A83",
                "0x4ECaBa5870353805a9F068101A40E0f32ed605C6",
            ],
            asset_types=[0, 0, 0],
            n_coins=3,
        ),
    ],
    "polygon:mainnet": [],
    "base:mainnet": [],
}
_base_pool_list["ethereum:mainnet-fork"] = _base_pool_list["ethereum:mainnet"]
base_pool_list = _base_pool_list

# -------------------------- POOL SETUP --------------------------


@dataclass
class PoolSettings:
    name: str
    symbol: str
    coins: List[Address]
    A: int
    fee: int
    offpeg_fee_multiplier: int
    ma_exp_time: int
    implementation_idx: int
    asset_types: List[int]
    method_ids: List[int]
    oracles: List[Address]


pool_settings = {
    "gnosis:mainnet": {
        "plain": [
            "WXDAI/USDC/USDT",  # name
            "3pool-ng",  # symbol
            [
                "0xe91D153E0b41518A2Ce8Dd3D7944Fa863463a97d",  # wxdai
                "0xDDAfbb505ad214D7b80b1f830fcCc89B60fb7A83",  # usdc
                "0x4ECaBa5870353805a9F068101A40E0f32ed605C6",  # usdt
            ],
            1000,  # A
            1000000,  # fee
            20000000000,  # offpeg_fee_multiplier
            865,  # ma_exp_time
            0,  # implementation index
            [0, 0, 0],  # asset_types
            [b"", b"", b""],  # method_ids
            [ZERO_ADDRESS, ZERO_ADDRESS, ZERO_ADDRESS],  # oracles
        ],
        "oracles": [
            "WETH<>wstETH",  # name
            "wstETH-ng",  # symbol
            [
                "0x6C76971f98945AE98dD7d4DFcA8711ebea946eA6",  # wsteth
                "0x6A023CCd1ff6F2045C3309768eAd9E68F978f6e1",  # weth
            ],
            500,
            1000000,  # fee
            20000000000,  # offpeg_fee_multiplier
            865,  # ma_exp_time
            0,  # implementation index
            [1, 0],  # asset_types
            [function_signature_to_4byte_selector("exchangeRate()"), 0],  # method_ids
            ["0x6C76971f98945AE98dD7d4DFcA8711ebea946eA6", ZERO_ADDRESS],  # oracles
        ],
        "rebasing": [
            "sGNO<>GNO" "sGNO-ng",  # name  # symbol
            [
                "0xA4eF9Da5BA71Cc0D2e5E877a910A37eC43420445",  # sGNO
                "0x9C58BAcC331c9aa871AFD802DB6379a98e80CEdb",  # GNO
            ],
            50,  # A,
            1000000,  # fee
            20000000000,  # offpeg_fee_multiplier
            865,  # ma_exp_time
            0,  # implementation index
            [2, 0],  # asset_types
            [b"", b""],  # method_ids
            [ZERO_ADDRESS, ZERO_ADDRESS],  # oracles
        ],
        "meta-plain": [],
        "meta-oracle": [],
        "meta-rebasing": [],
    }
}
