import boa
import pytest
from boa.environment import AddressType
from eth_account.account import Account, LocalAccount

from tests.utils.tokens import mint_for_testing


@pytest.fixture(scope="module")
def deployer() -> AddressType:
    return boa.env.generate_address()


@pytest.fixture(scope="module")
def owner() -> AddressType:
    return boa.env.generate_address()


@pytest.fixture(scope="module")
def fee_receiver() -> AddressType:
    return boa.env.generate_address()


@pytest.fixture(scope="module")
def eth_acc() -> LocalAccount:
    return Account.create()


@pytest.fixture(scope="module")
def alice():
    return boa.env.generate_address()


@pytest.fixture(scope="module")
def bob():
    return boa.env.generate_address()


@pytest.fixture(scope="module")
def charlie():
    return boa.env.generate_address()


@pytest.fixture(scope="module")
def dave():
    return boa.env.generate_address()


@pytest.fixture(scope="module")
def erin():
    return boa.env.generate_address()


@pytest.fixture(scope="module")
def frank():
    return boa.env.generate_address()


@pytest.fixture(scope="module")
def accounts(bob, charlie, dave, erin, frank):
    return [bob, charlie, dave, erin, frank]


# <---------------------   Functions   --------------------->
def mint_account(account, pool_tokens, initial_balance, initial_amounts):
    mint_for_testing(account, initial_balance, None, True)
    for pool_token, amount in zip(pool_tokens, initial_amounts):
        mint_for_testing(account, amount, pool_token, False)


def approve_account(account, pool_tokens, swap):
    for pool_token in pool_tokens:
        with boa.env.prank(account):
            pool_token.approve(swap.address, 2**256 - 1)


@pytest.fixture(scope="function")
def mint_owner(owner, pool_tokens, initial_balance, initial_amounts):
    mint_account(owner, pool_tokens, initial_balance, initial_amounts)


@pytest.fixture(scope="function")
def approve_owner(owner, pool_tokens, swap):
    approve_account(owner, pool_tokens, swap)


@pytest.fixture(scope="function")
def mint_alice(alice, pool_tokens, initial_balance, initial_amounts):
    mint_account(alice, pool_tokens, initial_balance, initial_amounts)


@pytest.fixture(scope="function")
def approve_alice(alice, pool_tokens, swap):
    approve_account(alice, pool_tokens, swap)


@pytest.fixture(scope="function")
def mint_bob(bob, pool_tokens, initial_balance, initial_amounts):
    mint_account(bob, pool_tokens, initial_balance, initial_amounts)


@pytest.fixture(scope="function")
def approve_bob(bob, pool_tokens, swap):
    approve_account(bob, pool_tokens, swap)


# <---------------------   Functions   --------------------->
def add_base_pool_liquidity(user, base_pool, base_pool_tokens, base_pool_decimals):
    amount = 1_000_000 // 3 + 1
    with boa.env.prank(user):
        for d, token in zip(base_pool_decimals, base_pool_tokens):
            token._mint_for_testing(user, amount * 10**d)
            token.approve(base_pool.address, 2**256 - 1)

        amounts = [amount * 10**d for d in base_pool_decimals]
        base_pool.add_liquidity(amounts, 0)


@pytest.fixture(scope="function")
def add_initial_liquidity_owner(
    owner,
    approve_owner,
    mint_owner,
    deposit_amounts,
    swap,
    pool_type,
    underlying_tokens,
    base_pool,
    base_pool_tokens,
    base_pool_decimals,
    base_pool_lp_token,
):
    if pool_type == 0:
        with boa.env.prank(owner):
            swap.add_liquidity(deposit_amounts, 0)
    else:
        add_base_pool_liquidity(owner, base_pool, base_pool_tokens, base_pool_decimals)
        with boa.env.prank(owner):
            base_pool_lp_token.approve(swap.address, 2**256 - 1)
            lp_token_bal = base_pool_lp_token.balanceOf(owner)
            to_mint_token0 = lp_token_bal * 10 ** underlying_tokens[0].decimals() // 10 ** base_pool_lp_token.decimals()

            mint_for_testing(owner, to_mint_token0, underlying_tokens[0], False)
            underlying_tokens[0].approve(swap.address, 2**256 - 1)

            swap.add_liquidity([to_mint_token0, lp_token_bal], 0)


@pytest.fixture(scope="function")
def add_initial_liquidity_alice(
    alice,
    approve_alice,
    mint_alice,
    deposit_amounts,
    swap,
    pool_type,
    base_pool,
    base_pool_tokens,
    base_pool_decimals,
    base_pool_lp_token,
):
    if pool_type == 0:
        with boa.env.prank(alice):
            swap.add_liquidity(deposit_amounts, 0)
    else:
        add_base_pool_liquidity(alice, base_pool, base_pool_tokens, base_pool_decimals)
        with boa.env.prank(alice):
            base_pool_lp_token.approve(swap.address, 2**256 - 1)
            swap.add_liquidity(deposit_amounts, 0)


@pytest.fixture(scope="function")
def mint_meta_bob(
    bob,
    mint_bob,
    base_pool,
    base_pool_tokens,
    base_pool_decimals,
    underlying_tokens,
    initial_amounts,
    base_pool_lp_token,
):
    add_base_pool_liquidity(bob, base_pool, base_pool_tokens, base_pool_decimals)
    mint_for_testing(bob, initial_amounts[0], underlying_tokens[0], False)


@pytest.fixture(scope="function")
def approve_meta_bob(bob, underlying_tokens, swap):
    for token in underlying_tokens:
        token.approve(swap.address, 2**256 - 1)
