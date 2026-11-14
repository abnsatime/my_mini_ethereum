from my_eth.block import Block

gensis = Block(number = 0, parent_hash = b'\x00'*32, transactions = [])
gensis.mine()
print(f"创世块 #{gensis.number} Nonce: {gensis.nonce} 时间戳: {gensis.timestamp}")
print(f"hash=0x{gensis.hash.hex()}")

block1 = Block(number = 1, parent_hash = gensis.hash, transactions = [])
block1.mine()
print(f"区块 #{block1.number} Nonce: {block1.nonce}")
print(f"hash=0x{block1.hash.hex()}")

print(f"parent正确？ {block1.parent_hash == gensis.hash}")