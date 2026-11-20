"""公共 fixture:所有测试共享的身份与世界状态构造器"""

import pytest
from eth_keys import keys

from my_eth.state import WorldState

ALICE_KEY = b"a" * 32
BOB_KEY = b"b" * 32
TOKEN_ADDR = "0x" + "cc" * 20
BAD_ADDR = "0x" + "dd" * 20

# 第 7 步手写的最小 ERC-20 runtime bytecode
ERC20_CODE = bytes([
    0x60, 0x24, 0x35,          # PUSH1 36, CALLDATALOAD -> amount
    0x60, 0x04, 0x35,          # PUSH1 4,  CALLDATALOAD -> to
    0x55,                      # SSTORE: storage[to] = amount
    0x60, 0x01, 0x60, 0x00, 0x52,   # MSTORE mem[0] = 1
    0x60, 0x20, 0x60, 0x00, 0xF3,   # RETURN mem[0:32]
])

# 坏合约:先写一个存储槽,再撞未知 opcode 0xfe -> 必然 revert
BAD_CODE = bytes([0x60, 0x07, 0x60, 0x01, 0x55, 0xfe])


@pytest.fixture
def alice_key():
    return ALICE_KEY


@pytest.fixture
def bob_key():
    return BOB_KEY


@pytest.fixture
def alice_addr(alice_key):
    return keys.PrivateKey(alice_key).public_key.to_address().lower()


@pytest.fixture
def bob_addr(bob_key):
    return keys.PrivateKey(bob_key).public_key.to_address().lower()


@pytest.fixture
def token_addr():
    return TOKEN_ADDR


@pytest.fixture
def bad_addr():
    return BAD_ADDR


@pytest.fixture
def erc20_code():
    return ERC20_CODE


@pytest.fixture
def world(alice_addr):
    """预置世界:Alice 有钱 + ERC-20 与坏合约已部署"""
    w = WorldState()
    w.get_or_create(alice_addr).balance = 1_000_000
    w.deploy_contract(TOKEN_ADDR, ERC20_CODE)
    w.deploy_contract(BAD_ADDR, BAD_CODE)
    return w
