import os
import threading

CLI_SCRIPT_PATH = '/home/jim/Documents/Code/9th_Semester/Distributed_Project/noobcash/cli/cli.py'

def call_cli(ip, port, transaction_file):
    os.system(f'python3 {CLI_SCRIPT_PATH} --ip {ip} --port {port} --transactions {transaction_file}')
    
t1 = threading.Thread(target=call_cli, args=('localhost', '5000', 'transactions_node_0.txt'))
t2 = threading.Thread(target=call_cli, args=('localhost', '5001', 'transactions_node_1.txt'))
t3 = threading.Thread(target=call_cli, args=('localhost', '5002', 'transactions_node_2.txt'))
t4 = threading.Thread(target=call_cli, args=('localhost', '5003', 'transactions_node_3.txt'))

t1.start()
t2.start()
t3.start()
t4.start()
