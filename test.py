import unittest

import wallet
import transaction
import Crypto
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5


class TestWallet(unittest.TestCase):
    def test_wallet(self):
        print('hello')
        
class TestTransaction(unittest.TestCase):
    def test_signature(self):
        sender_wallet = wallet.Wallet()
        recipient_wallet = wallet.Wallet()
        sender_keys = sender_wallet.get_key_pair()
        recipient_keys = recipient_wallet.get_key_pair()
        
        new_transaction = transaction.Transaction(sender_keys[0], recipient_keys[0], 20)
        new_transaction.sign_transaction(sender_keys[1])
                
        assert PKCS1_v1_5.new(RSA.import_key(sender_keys[0])).verify(new_transaction.transaction_id, new_transaction.signature)
        
if __name__ == '__main__':
    unittest.main()