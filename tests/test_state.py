"""state_root + 世界状态:确定性、敏感性、快照回滚"""

from my_eth.state import WorldState


def test_empty_world_root_is_sentinel():
    from my_eth.keccak_util import keccak256
    assert WorldState().root() == keccak256(b"")


def test_root_changes_on_new_account():
    w = WorldState()
    r0 = w.root()
    w.get_or_create("0x" + "aa" * 20).balance = 1
    assert w.root() != r0


def test_root_changes_on_balance_mutation():
    w = WorldState()
    acct = w.get_or_create("0x" + "aa" * 20)
    acct.balance = 1
    r1 = w.root()
    acct.balance = 2
    assert w.root() != r1


def test_root_changes_on_nonce_mutation():
    w = WorldState()
    acct = w.get_or_create("0x" + "aa" * 20)
    acct.balance = 1
    r1 = w.root()
    acct.nonce += 1
    assert w.root() != r1


def test_root_changes_on_storage_mutation():
    w = WorldState()
    acct = w.get_or_create("0x" + "bb" * 20)
    acct.code = bytes([0x60])
    acct.storage[0] = 42
    r1 = w.root()
    acct.storage[0] = 43
    assert w.root() != r1


def test_root_deterministic():
    def build():
        w = WorldState()
        a = w.get_or_create("0x" + "aa" * 20)
        a.balance, a.nonce = 100, 1
        c = w.get_or_create("0x" + "bb" * 20)
        c.code = bytes([0x60])
        c.storage[0] = 42
        return w
    assert build().root() == build().root()


def test_snapshot_rollback_restores_state():
    w = WorldState()
    acct = w.get_or_create("0x" + "aa" * 20)
    acct.balance, acct.nonce = 100, 3
    snap = w.snapshot()

    acct.balance = 0
    w.get_or_create("0x" + "bb" * 20).balance = 999   # 幽灵账户
    acct.code = b"\x60"

    w.rollback(snap)
    assert acct.balance == 100
    assert "0x" + "bb" * 20 not in w.accounts          # 幽灵被清理
    assert w.root() != WorldState().root()


def test_rollback_preserves_current_nonce():
    """revert 语义:nonce 不随快照回滚"""
    w = WorldState()
    acct = w.get_or_create("0x" + "aa" * 20)
    acct.balance, acct.nonce = 100, 3
    snap = w.snapshot()
    acct.nonce = 4                                     # "已上链"的消耗
    w.rollback(snap)
    assert acct.nonce == 4                              # 保留!
    assert acct.balance == 100
