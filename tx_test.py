from eth_keys import keys
from my_eth.transaction import Transaction

# 生成两个身份
alice_key = b"a" * 32
alice_addr = keys.PrivateKey(alice_key).public_key.to_checksum_address()
print("alice的地址:", alice_addr)

# 构建一笔转账
tx = Transaction(nonce=0, to="0x" + "bb" * 20, value=500, data=b"")
sign_tx = tx.sign(alice_key)
print(f"tx签名，得到 r, s, v: \n r={sign_tx.r} s={sign_tx.s} v={sign_tx.v}")
print(f"恢复出的sender: {sign_tx.sender}")

# 验证 1: 验证 正确的发送者
print("alice 签的,声称是 alice:", sign_tx.verify(alice_addr))   # True

# 验证 2: 篡改交易 (value 500 -> 501)   交易哈希变了，恢复会错误
tx2 = Transaction(nonce=0, to="0x" + "bb" * 20, value=501, data=b"")
print("篡改后仍声称是 alice:", sign_tx.sender == alice_addr and tx2.recover_from(sign_tx.r, sign_tx.s, sign_tx.v) == alice_addr)  # False

# 验证 3: bob 拿自己的私钥去签同一笔交易
bob_key = b"b" * 32
bob_stx = tx.sign(bob_key)
print("bob 冒签,恢复出的是:", bob_stx.sender)  # bob 自己的地址

