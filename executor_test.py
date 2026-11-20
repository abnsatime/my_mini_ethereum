# executor_test.py
from eth_keys import keys
from my_eth.state import WorldState
from my_eth.transaction import Transaction
from my_eth.executor import execute_transaction
from my_eth.abi import encode_transfer

alice_key = b"a" * 32
alice = keys.PrivateKey(alice_key).public_key.to_address().lower()  # 统一小写
token_addr = "0x" + "cc" * 20
bad_addr = "0x" + "dd" * 20

ERC20_CODE = bytes([           # 第 7 步那个 transfer 合约
    0x60, 0x24, 0x35,          # PUSH1 36, CALLDATALOAD -> amount
    0x60, 0x04, 0x35,          # PUSH1 4,  CALLDATALOAD -> to
    0x55,                      # SSTORE
    0x60, 0x01, 0x60, 0x00, 0x52,
    0x60, 0x20, 0x60, 0x00, 0xF3,
])
# 坏合约:先写一个存储,再撞未知 opcode 0xfe -> 必然 revert
BAD_CODE = bytes([0x60, 0x07, 0x60, 0x01, 0x55, 0xfe])

world = WorldState()
world.deploy_contract(token_addr, ERC20_CODE)
world.deploy_contract(bad_addr, BAD_CODE)
world.get_or_create(alice).balance = 1_000_000  # 空投

# ---- 交易 1:成功调用 ERC-20 transfer ----
cd = encode_transfer("0x" + "bb" * 20, 500)
r = execute_transaction(world, Transaction(0, token_addr, 0, cd, 100_000).sign(alice_key))
bob_slot = int.from_bytes(bytes.fromhex("bb" * 20), "big")
assert r["success"] and world.accounts[token_addr].storage[bob_slot] == 500
print("✅ 交易1: transfer 真实写入了世界状态中的合约账户 storage")

# ---- 交易 2:revert —— 状态回滚,但 nonce 走了、gas 扣了 ----
balance_before = world.accounts[alice].balance
r = execute_transaction(world, Transaction(1, bad_addr, 0, b"", 100_000).sign(alice_key))
assert not r["success"]
assert world.accounts[bad_addr].storage == {}          # 写到一半的 SSTORE 被回滚
assert world.accounts[alice].nonce == 2                # revert 不回滚 nonce
assert world.accounts[alice].balance < balance_before  # 已用 gas 不退
print("✅ 交易2: revert 回滚了存储,但 nonce/gas 照常消耗")

# ---- 交易 3:无效交易 —— 直接拒收,什么都没发生 ----
try:
    execute_transaction(world, Transaction(0, token_addr, 0, cd, 100_000).sign(alice_key))
    print("❌ 不该到这")
except ValueError as e:
    assert world.accounts[alice].nonce == 2            # 拒收不消耗任何东西
    print("✅ 交易3: 无效交易被拒收:", e)

# ---- 顺带验证:上一笔成功的 transfer 不受 revert 影响 ----
assert world.accounts[token_addr].storage[bob_slot] == 500
print("✅ 成功交易的状态不受后续 revert 影响")
print("\n🎉 交易执行器完工:签名→快照→EVM→世界状态,全链路在真实状态下运转")