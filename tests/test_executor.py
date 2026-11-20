"""执行器集成:三层错误模型 + 快照保护下的真实状态读写"""

from my_eth.abi import encode_transfer
from my_eth.executor import execute_transaction
from my_eth.transaction import Transaction


def _slot_of(addr_hex20: str) -> int:
    """地址(20字节hex)转存储槽位 —— 与合约里 CALLDATALOAD 得到的 to 一致"""
    return int.from_bytes(bytes.fromhex(addr_hex20), "big")


def test_transfer_writes_contract_storage_in_world(world, alice_key, alice_addr, token_addr):
    cd = encode_transfer("0x" + "bb" * 20, 500)
    r = execute_transaction(world, Transaction(0, token_addr, 0, cd, 100_000).sign(alice_key))
    assert r["success"]
    # SSTORE 落在了世界状态的合约账户上,不是临时字典
    assert world.accounts[token_addr].storage[_slot_of("bb" * 20)] == 500


def test_revert_rolls_back_storage_but_keeps_nonce_gas(world, alice_key, alice_addr, bad_addr):
    alice_acct = world.accounts[alice_addr]
    nonce_before = alice_acct.nonce           # fixture 里是 0
    balance_before = alice_acct.balance

    r = execute_transaction(world, Transaction(0, bad_addr, 0, b"", 100_000).sign(alice_key))

    assert not r["success"]
    assert world.accounts[bad_addr].storage == {}          # SSTORE 写到一半被回滚
    assert alice_acct.nonce == nonce_before + 1            # revert 不回滚 nonce
    assert alice_acct.balance < balance_before              # 已烧 gas 不退


def test_invalid_tx_rejected_outright(world, alice_key, token_addr):
    import pytest
    cd = encode_transfer("0x" + "bb" * 20, 500)
    # 合法地消耗掉 nonce=0
    execute_transaction(world, Transaction(0, token_addr, 0, cd, 100_000).sign(alice_key))
    # 再用旧的 nonce=0 重放 -> 无效交易,直接拒收
    with pytest.raises(ValueError):
        execute_transaction(world, Transaction(0, token_addr, 0, cd, 100_000).sign(alice_key))


def test_successful_tx_survives_later_revert(world, alice_key, token_addr):
    cd = encode_transfer("0x" + "bb" * 20, 500)
    execute_transaction(world, Transaction(0, token_addr, 0, cd, 100_000).sign(alice_key))
    from my_eth.transaction import Transaction as Tx
    import pytest
    with pytest.raises(ValueError):
        execute_transaction(world, Tx(99, token_addr, 0, cd, 100_000).sign(alice_key))
    # 第一笔成功交易的状态不受影响
    assert world.accounts[token_addr].storage[_slot_of("bb" * 20)] == 500


def test_value_transfer_to_eoa(world, alice_key, bob_addr):
    r = execute_transaction(world, Transaction(0, bob_addr, 300, b"", 21_000).sign(alice_key))
    assert r["success"]
    assert world.accounts[bob_addr].balance == 300


def test_state_root_reflects_execution(world, alice_key, token_addr):
    r0 = world.root()
    cd = encode_transfer("0x" + "bb" * 20, 500)
    execute_transaction(world, Transaction(0, token_addr, 0, cd, 100_000).sign(alice_key))
    r1 = world.root()
    assert r0 != r1          # 执行真实改变了世界状态根
