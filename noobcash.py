import argparse

def parse_command_line_arguments():    
    parser = argparse.ArgumentParser(description='Noobcash back-end', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--is_bootstrap', help='Whether node is the bootstrap node', action='store_true')
    parser.add_argument('--n', help='Number of nodes', type=int, default=5)
    return parser.parse_args()

def main():
    args = parse_command_line_arguments()
    
    if args.is_bootstrap is True:
        NBCs = 100 * args.n
        
        generate_genesis_block(NBCs)
        
        while not_all_nodes_contacted:
            listen_for_messages()
            send_id_to_node()
        
        
    

def generate_genesis_block(NBCs):
    42

if __name__ == '__main__':
    main()