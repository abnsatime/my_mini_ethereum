from my_eth.state import WorldState
from my_eth.account import new_address

state = WorldState()

alice_addr, alice_key = new_address()
bob_addr, _ = new_address()

alice = state.get_or_create(alice_addr)
alice.balance = 1000

state.apply_transfer(alice_addr, bob_addr, 400, 0)

print(f"alice nonce={alice.nonce} balance={alice.balance}")
print(f"bob nonce={state.get_or_create(bob_addr).nonce} balance={state.get_or_create(bob_addr).balance}")

try:
    state.apply_transfer(alice_addr, bob_addr, 100, 0)
    print("错误：nonce 不符的交易应该被拒绝")
except ValueError as e:
    print(f"正确：nonce 不符的交易被拒绝: {e}")

# nonce =1 的合法交易
state.apply_transfer(alice_addr, bob_addr, 100, 1)
print("nonce = 1 后 alice", state.accounts[alice_addr].balance)