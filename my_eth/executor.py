"""交易执行器:签名验证 → 快照保护 → EVM 真实读写世界状态"""

from my_eth.evm import EVM, EVMRevert
from my_eth.state import WorldState
from my_eth.transaction import SignedTransaction


def execute_transaction(world: WorldState, stx: SignedTransaction, gas_price: int=1) -> dict:
    """在快照保护下 执行一笔已签名交易 返回: {"success": bool, "return": bytes}
    无效交易直接 raise(不进块)  revert 返回 success=False(进块但状态回滚)"""

    tx = stx.tx
    sender = stx.sender.lower()
    sender_acct = world.get_or_create(sender)

    if tx.nonce != sender_acct.nonce:
        raise ValueError(f"nonce 不符， 交易={tx.nonce}, 账户={sender_acct.nonce}")
    gas_fee = tx.gas_limit * gas_price
    if sender_acct.balance < tx.value + gas_fee:
        raise ValueError("余额不足（含gas预扣）")

    sender_acct.nonce += 1
    sender_acct.balance -= gas_fee

    snap = world.snapshot()
    evm = None
    try:
        target = world.get_or_create(tx.to.lower())
        sender_acct.balance -= tx.value
        target.balance += tx.value
        ret = b""

        if target.is_contract:
            evm = EVM(target.code, calldata=tx.data, storage=target.storage)
            evm.gas = tx.gas_limit
            ret = evm.execute()

        refund = (evm.gas if evm else tx.gas_limit) * gas_price
        sender_acct.balance += refund

        return {"success" : True, "return": ret}
    
    except EVMRevert:
        remaining = evm.gas if evm else tx.gas_limit
        sender_acct.balance += remaining * gas_price
        world.rollback(snap)
        return {"success": False, "return": b""}