from my_eth.block import Block
from my_eth.keccak_util import keccak256
from my_eth.transaction import Transaction

alice_key = b"a" * 32
txs = [Transaction(nonce=0, to="0x" + "bb" * 20, value=500).sign(alice_key) for _ in range(3)]

genesis = Block(0, b"\x00" * 32, [])
genesis.mine()
print("空块 root:", genesis.transactions_root.hex()[:16], "（应为 c5d2460186f7233c）")

b1 = Block(1, genesis.hash, txs)
b1.mine()
print("3笔交易 root:", b1.transactions_root.hex()[:16])

# 篡改一笔交易的 value，root 应该变
txs_tampered = [Transaction(nonce=0, to="0x" + "bb" * 20, value=501).sign(alice_key) for _ in range(3)]
b1_tampered = Block(1, genesis.hash, txs_tampered)
b1_tampered.mine()
print("篡改后   root:", b1_tampered.transactions_root.hex()[:16])
print("root 改变?", b1.transactions_root != b1_tampered.transactions_root)