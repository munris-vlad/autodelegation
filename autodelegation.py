#!/usr/bin/env python3
import os, requests
import configparser
import pexpect
import getpass
import time 
from subprocess import Popen, PIPE

# constants
TRANSACTION_WAIT_TIME = 10

class Autodelegation():
    def __init__( self, config_file='config.ini' ):
        # obtain the host name
        self.name = os.uname()[1]

        # read the config and setup the telegram
        self.read_config( config_file )
        self.setup_telegram()
        self.setup_info()

        # send the hello message
        self.send( f'Hello from Autodelegation Bot on {self.name}!' )
        
    def read_config( self, config_file ):
        '''
        Read the configuration file
        '''
        config = configparser.ConfigParser()
        if os.path.exists( config_file ):
            print( f"Using Configuration File: { config_file }")
            config.read( config_file )
        else:
            print( f"Configuration File Does Not Exist: { config_file }")

        # save the config
        self.config = config

    def setup_telegram( self ):
        '''
        Setup telegram
        '''
        if "TELEGRAM_TOKEN" in os.environ['VARIABLES']:
            self.telegram_token = os.environ['VARIABLES']['TELEGRAM_TOKEN']
        else:
            self.telegram_token = None
        
        if "TELEGRAM_CHAT_ID" in os.environ['VARIABLES']:
            self.telegram_chat_id = os.environ['VARIABLES']['TELEGRAM_CHAT_ID']
        else:
            self.telegram_chat_id = None

    def setup_info( self ):
        '''
        Setup info
        '''

        if "TIKER" in os.environ['VARIABLES']:
            self.tiker = os.environ['VARIABLES']['TIKER']

        if "TOKEN" in os.environ['VARIABLES']:
            self.token = os.environ['VARIABLES']['TOKEN']

        if "DECIMALS" in os.environ['VARIABLES']:
            self.decimals = os.environ['VARIABLES']['DECIMALS']

        # sleep time between delegation cycles
        if "SLEEP_TIME" in os.environ['VARIABLES']:
            self.sleep_time = int(os.environ['VARIABLES']['SLEEP_TIME'])
        else:
            self.sleep_time = 600
        
        # bank reserve
        if "RESERVE" in os.environ['VARIABLES']:
            self.reserve = float(os.environ['VARIABLES']['RESERVE'])
        else:
            self.reserve = 0.1000

        # Prompt for the password if not in environment
        if "PASSWORD" in os.environ['VARIABLES']:
            self.password = os.environ['VARIABLES']['PASSWORD']
        else:
            self.password = getpass.getpass("Enter the wallet password: ")

        # chain id
        if "CHAIN" in os.environ['VARIABLES']:
            self.chain = os.environ['VARIABLES']['CHAIN']

        # wallet name
        if "WALLET_NAME" in os.environ['VARIABLES']:
            self.wallet_name = os.environ['VARIABLES']['WALLET_NAME']
        
        # wallet and validator keys
        if "WALLET_ADDRESS" in os.environ['VARIABLES']:
            self.wallet_key = os.environ['VARIABLES']['WALLET_ADDRESS']
        else:
            print('Unable to find the wallet address in the configuration file. Exiting...')
            exit()

        if "VALIDATOR_ADDRESS" in os.environ['VARIABLES']:
            self.validator_key = os.environ['VARIABLES']['VALIDATOR_ADDRESS']
        else:
            print('Unable to find the validator address in the configuration file. Exiting...')
            exit()

    def send( self, msg ):
        '''
        Print the message and send telegram message, if available
        '''
        if self.telegram_token != None and self.telegram_chat_id != None:
            requests.post( f'https://api.telegram.org/bot{self.telegram_token}/sendMessage?chat_id={self.telegram_chat_id}&text={msg}' )
        print( msg )

    def parse_subprocess( self, response, keyword ):
        '''
        Parse and return the line
        '''
        for line in response.decode("utf-8").split('\n'):
            if keyword in line:
                return line
    
    def shares_to_decimal( self, shares ):
        '''
        return the share to decimal conversion
        '''
        return float( shares ) * ( 1/self.decimals )

    def decimal_to_shares( self, amount ):
        '''
        return the decimal to shares conversion
        '''
        return int( amount * self.decimals )

    def get_balance( self ):
        '''
        Obtain the balance
        '''
        proc = Popen([ f"{ self.tiker } q bank balances {self.wallet_key}" ], stdout=PIPE, shell=True)
        (out, err) = proc.communicate()
        line = self.parse_subprocess( out, 'amount' )
        balance = line.split('"')[1]
        return int( balance )

    def distribute_rewards( self ):
        '''
        Distribute the rewards from the validator and return the hash
        '''
        child = pexpect.spawn(f"{ self.tiker } tx distribution withdraw-rewards { self.validator_key } --chain-id={ self.chain } --from {self.wallet_name} -y", timeout=10)
        child.expect( b'Enter keyring passphrase:' ) 
        child.sendline( self.password )   
        child.expect( pexpect.EOF )                                                                                                                                     
        child.close()
        line = self.parse_subprocess( child.before, 'txhash:' )
        txhash = line.split('txhash: ')[1]
        return txhash

    def distribute_rewards_commission( self ):
        '''
        Distribute the commission for the validator and return the hash
        '''
        child = pexpect.spawn(f"{ self.tiker } tx distribution withdraw-rewards { self.validator_key } --chain-id={ self.chain } --from {self.wallet_name} --commission -y", timeout=10)
        child.expect( b'Enter keyring passphrase:' ) 
        child.sendline( self.password )   
        child.expect( pexpect.EOF )                                                                                                                                     
        child.close()
        line = self.parse_subprocess( child.before, 'txhash:' )
        txhash = line.split('txhash: ')[1]
        return txhash

    def delegate( self, amount ):
        '''
        Delegate the amount to the validator
        '''
        child = pexpect.spawn( f'{ self.tiker } tx staking delegate { self.validator_key } { amount }{ self.token } --from { self.wallet_name } --chain-id { self.chain } -y', timeout=10)
        child.expect( b'Enter keyring passphrase:' ) 
        child.sendline( self.password )   
        child.expect( pexpect.EOF )                                                                                                                                     
        child.close()
        line = self.parse_subprocess( child.before, 'txhash:' )
        txhash = line.split('txhash: ')[1]
        return txhash
    
    def get_delegations( self ):
        '''
        Obtain the delegation amount for the validator
        '''
        proc = Popen([ f"{ self.tiker } q staking delegations-to {self.validator_key} --chain-id={self.chain}" ], stdout=PIPE, shell=True)
        (out, err) = proc.communicate()
        line = self.parse_subprocess( out, 'shares' )
        balance = self.shares_to_decimal( line.split('"')[1].split(".")[0]) 
        return balance

    def delegation_cycle( self ):
        '''
        Delegation cycle for distributing rewards and sending them out
        '''
        self.send( f"Start Delegation Cycle!" )
        curr_delegations = self.get_delegations()
        self.send( f" - Current Delegation: { curr_delegations } " )

        self.send( f" - Distribution Tx Hash: { self.distribute_rewards() }" )
        time.sleep( TRANSACTION_WAIT_TIME )

        self.send( f" - Commission Tx Hash: { self.distribute_rewards_commission() }" )
        time.sleep( TRANSACTION_WAIT_TIME )
        
        balance = self.get_balance()
        self.send( f" - Current Balance ( post distribution ): { self.shares_to_decimal( balance ) } " )

        # determine if the balance exceeds the reserve for a re-delegation
        proposed_delegation = balance - self.decimal_to_shares( self.reserve )

        # if the proposed delegation meets criteria
        if proposed_delegation > 0:
            self.send( f" - Proposed Amount for Delegation: { self.shares_to_decimal( proposed_delegation ) } ( { proposed_delegation } shares )" )
            self.send( f" - Delegation Tx Hash: { self.delegate( proposed_delegation ) }" )
            time.sleep( TRANSACTION_WAIT_TIME )

            new_delegations = self.get_delegations()
            self.send( f" - New Delegation: { new_delegations } ( Delta: { new_delegations - curr_delegations } )" )
        else:
            self.send( f" - Balance of { self.shares_to_decimal( balance ) } does not exceed the reserve amount { self.reserve } for delegation - Skipping..." )
        self.send( f"End Delegation Cycle" )

        self.send( f"Sleeping { self.sleep_time } Seconds\n" )
        time.sleep( self.sleep_time )

def parse_arguments( ):
    '''
    Parse the arguments passed in
    '''
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', '-c', type=str, required=False, default='config.ini', help='Configuration File')
    return parser.parse_args()

# Parse arguments
args = parse_arguments()

# Create the object
bot = Autodelegation( args.config )

# run periodic delegation cycle
while True:
    bot.delegation_cycle()
