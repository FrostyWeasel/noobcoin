import argparse
from platform import node
import requests

# TODO: To test parallel transaction creation add threads that send transaction creation requests to different nodes at the same time (put in another file)

def parse_command_line_arguments():    
    parser = argparse.ArgumentParser(description='Noobcash CLI By Kostakis AE', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--transactions', help='A file containing a list of transactions to be performed', type=str, required=False, default='transactions.txt')
    parser.add_argument('--ip', help='The ip address of the node creating the transactions', type=str, required=False, default='localhost')
    parser.add_argument('--port', help='The port address of the node creating the transactions', type=int, required=True)
    return parser.parse_args()

if __name__=='__main__':
    args = parse_command_line_arguments()
        
    with open(args.transactions, 'r') as transactions_fh:
        
        request_url = f"http://{args.ip}:{args.port}/transaction/create"
        print(f'[{args.ip}, {args.port}, {args.transactions}] {request_url}')
        
        for transaction in transactions_fh:
            trans_info = transaction.split(' ')
            node_id = trans_info[0][2:]
            amount = trans_info[-1]
            
            r = requests.post(request_url, data={'recipient_id': node_id, 'amount': amount})
            