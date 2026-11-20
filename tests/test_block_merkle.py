"""区块 PoW + Merkle 根:链式哈希与交易承诺"""

from my_eth.block import Block
from my_eth.keccak_util import keccak256
from my_eth.merkle import merkle_root
from my_eth.transaction import Transaction

ALICE_KEY = b"a" * 32


def test_mine_meets_target():
    b = Block(0, b"\x00" * 32, [])
    b.mine()
    assert b.hash.hex().startswith("0")
    assert b.nonce >= 0


def test_chain_links():
    genesis = Block(0, b"\x00" * 32, [])
    genesis.mine()
    b1 = Block(1, genesis.hash, [])
    b1.mine()
    assert b1.parent_hash == genesis.hash
    assert b1.number == 1


def test_empty_block_root_is_sentinel():
    b = Block(0, b"\x00" * 32, [])
    b.mine()
    assert b.transactions_root == keccak256(b"")


def test_tampered_tx_changes_root():
    txs = [Transaction(0, "0x" + "bb" * 20, 500).sign(ALICE_KEY) for _ in range(3)]
    txs_t = [Transaction(0, "0x" + "bb" * 20, 501).sign(ALICE_KEY) for _ in range(3)]
    root = merkle_root([keccak256(t.tx_hash()) for t in txs])
    root_t = merkle_root([keccak256(t.tx_hash()) for t in txs_t])
    assert root != root_t


def test_merkle_odd_leaves():
    # 单叶子:while 不进循环,直接返回该叶子(与 Bitcoin 一致)
    leaf = keccak256(b"a")
    assert merkle_root([leaf]) == leaf
    # 三个叶子:第三个自我配对后正常归并
    r3 = merkle_root([keccak256(b"a"), keccak256(b"b"), keccak256(b"c")])
    assert r3 != merkle_root([keccak256(b"a"), keccak256(b"b")])
    assert r3 != merkle_root([])
