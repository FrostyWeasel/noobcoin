import logging
import sys
import unittest

import Crypto
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

from noobcash.transaction import Transaction
from noobcash.transaction_input import TransactionInput
from noobcash.transaction_output import TransactionOutput

logging.basicConfig(filename='debug.log', filemode='w', level=logging.DEBUG)

class TestTransaction(unittest.TestCase):
    def test_creation(self):
        new_trans = Transaction('sender_address', 'recipient_address', 0.00001, [TransactionInput(TransactionOutput('sender_address', 0.00002, 'parent_transaction_id'))])
        
        logging.debug(f'Transaction created: {new_trans.to_dict()}')
        
# class TestWallet(unittest.TestCase):
#     def test_wallet(self):
#         print('hello')
        
# class TestTransaction(unittest.TestCase):
#     def test_signature(self):
#         sender_wallet = wallet.Wallet()
#         recipient_wallet = wallet.Wallet()
#         sender_keys = sender_wallet.get_key_pair()
#         recipient_keys = recipient_wallet.get_key_pair()
        
#         new_transaction = transaction.Transaction(sender_keys[0], recipient_keys[0], 20, [TransactionInput(TransactionOutput(1, 20, 0))])
#         new_transaction.sign_transaction(sender_keys[1])
                
#         assert PKCS1_v1_5.new(RSA.import_key(sender_keys[0])).verify(new_transaction.transaction_id, new_transaction.signature)
        
# class TestNode(unittest.TestCase):
#     def test_create_transaction(self):
#         my_node = Node()
#         receiver_node = Node()
        
#         my_node.wallet.add_transaction_output(TransactionOutput(my_node.wallet.public_key, 10, 0))
#         my_node.wallet.add_transaction_output(TransactionOutput(my_node.wallet.public_key, 20, 42))
        
#         assert my_node.wallet.balance() == 30
        
#         my_node.create_transaction(receiver_node.wallet.public_key, 20)
        
#         assert my_node.wallet.balance() == 10
        
#         try:
#             my_node.create_transaction(receiver_node.wallet.public_key, 20)
#             assert False
#         except Exception as e:
#             assert True
        
        
if __name__ == '__main__':
    unittest.main()