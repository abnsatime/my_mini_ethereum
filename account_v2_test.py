from my_eth.account import Account
from my_eth.keccak_util import to_checksum_address
from eth_keys import keys
from eth_utils import to_checksum_address as official


addr = to_checksum_address("0xfb6916095ca1df60bb79ce92c3f02527d4bbf2b4")
assert addr == official("0xfb6916095ca1df60bb79ce92c3f02527d4bbf2b4"), addr
print("EIP-55 ✅:", addr)

# EOA & 合约账户
eoa = Account(nonce=0, balance=100)
contract = Account(code=bytes.fromhex("6001600101"), storage={0: 5, 1: 7})
print("eoa is_contract:", eoa.is_contract)          # False
print("contract is_contract:", contract.is_contract)  # True
print("contract code_hash:", contract.code_hash.hex()[:16])
print("contract storage_root:", contract.storage_root.hex()[:16])

# 存储变化 -> storage_root 变化
contract.storage[0] = 6
print("改后 storage_root:", contract.storage_root.hex()[:16])


# 用 eth_keys 交叉验证我们手写的 EIP-55
pk = keys.PrivateKey(b"a" * 32)
real_addr = pk.public_key.to_address()
print("我们实现的校验和地址 == eth_keys库实现的:", to_checksum_address(real_addr) == pk.public_key.to_checksum_address())