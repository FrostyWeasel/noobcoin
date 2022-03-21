# %%
import threading
from time import sleep

lock_mining = threading.Lock()

class Node():
    def __init__(self):
        self.current_block = 'if you are seeing me then the world fucking sucks'

# def father():
#     for i in range(20):
#         mine()
        
    def threaded_mining(self, callback):
        lock_mining.acquire()
        print(f'I acquired the lock')
        print('diggy diggy')
        sleep(2)
        callback()
        
    def mining_end(self):
        print(f'Callback')
        self.current_block = 'If you see this then the world is wonderful and i love everyone'
        lock_mining.release()
            
    def mine(self):
        active = {}
        
        mining_thread = threading.Thread(target=self.threaded_mining, args=[self.mining_end])
        mining_thread.start()
        
        while True:
            print(self.current_block)
    
# %%
n = Node()
n.mine()
# %%
