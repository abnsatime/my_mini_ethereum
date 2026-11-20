"""签名交易:公钥恢复、防篡改、防冒签"""

from eth_keys import keys

from my_eth.transaction import Transaction


def test_sign_and_recover(alice_key, alice_addr):
    stx = Transaction(0, "0x" + "bb" * 20, 500).sign(alice_key)
    assert stx.sender.lower() == alice_addr


def test_tamper_detection(alice_key, alice_addr):
    stx = Transaction(0, "0x" + "bb" * 20, 500).sign(alice_key)
    tampered = Transaction(0, "0x" + "bb" * 20, 501)
    assert tampered.recover_from(stx.r, stx.s, stx.v).lower() != alice_addr


def test_wrong_signer_recovers_own_address():
    bob_key = b"b" * 32
    stx = Transaction(0, "0x" + "bb" * 20, 500).sign(bob_key)
    bob = keys.PrivateKey(bob_key).public_key.to_address().lower()
    assert stx.sender.lower() == bob


def test_verify_helpers(alice_key, alice_addr):
    stx = Transaction(0, "0x" + "bb" * 20, 500).sign(alice_key)
    assert stx.verify(alice_addr)
    assert not stx.verify("0x" + "ee" * 20)


def test_tx_hash_changes_with_content(alice_key):
    a = Transaction(0, "0x" + "bb" * 20, 500).sign(alice_key)
    b = Transaction(0, "0x" + "bb" * 20, 500).sign(b"c" * 32)
    assert a.tx_hash() != b.tx_hash()  # 不同签名者 -> 不同哈希
