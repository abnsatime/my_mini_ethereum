"""世界状态：所有账户的当前余额和 nonce"""

from my_eth.account import Account

class WorldState:
    def __init__(self):
        self.accounts: dict[str, Account] = {}

    def get_or_create(self, addr: str) -> Account:
        if addr not in self.accounts:
            self.accounts[addr] = Account()
        return self.accounts[addr]

    def apply_transfer(self, sender: str, to: str, amount: int, tx_nonce: int) -> None:
        """执行一笔转账的核心状态转移"""
        sender_account = self.get_or_create(sender)
        if tx_nonce != sender_account.nonce:
            raise ValueError(f"nonce 不符: 交易={tx_nonce}, 账户={sender_account.nonce}")
        if sender_account.balance < amount:
            raise ValueError("余额不足")
        
        sender_account.balance -= amount
        sender_account.nonce += 1
        self.get_or_create(to).balance += amount

