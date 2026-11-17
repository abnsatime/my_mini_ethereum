from my_eth.evm import EVM
from my_eth.abi import encode_transfer, decode_transfer, SELECTOR_TRANSFER
from my_eth.keccak_util import keccak256

print("selector:", SELECTOR_TRANSFER.hex())

# ---    1. 手写合约 runtime bytecode    ---
CODE = bytes([
    0x60, 0x24, 0x35,       # PUSH1 36, CALLDATALOAD  -> amount
    0x60, 0x04, 0x35,       # PUSH1 4,  CALLDATALOAD  -> to
    0x55,                   # SSTORE: storage[to] = amount
    0x60, 0x01,             # PUSH1 1
    0x60, 0x00, 0x52,       # MSTORE: mem[0] = 1
    0x60, 0x20,             # PUSH1 32
    0x60, 0x00, 0xF3,       # RETURN mem[0:32]
])

# --- 2. 用 ABI 编码一笔 transfer ---
bob = "0x" + "bb" * 20
calldata = encode_transfer(bob, 500)
print("calldata:", calldata.hex())
assert calldata.hex().startswith("a9059cbb")

# --- 3. 解码验证(ABI 往返一致) ---
to, amount = decode_transfer(calldata)
assert to == bob.lower() and amount == 500
print("解码 ✅ to =", to, "amount =", amount)

# --- 4. 喂给 EVM 执行,检查存储真的变了 ---
storage = {}
evm = EVM(CODE, calldata=calldata, storage=storage)
ret = evm.execute()
assert int.from_bytes(ret, "big") == 1
bob_as_slot = int.from_bytes(bytes.fromhex(bob[2:]), "big")
print("EVM 返回 ✅ 1 (true)")
print("storage[to] =", storage.get(bob_as_slot), "← 状态真的被合约改了!")
assert storage[bob_as_slot] == 500
print("\n全链路打通: ABI calldata → EVM → 世界状态")