#!/usr/bin/env python3
import os, requests
import configparser
import pexpect
import getpass
import time 
from subprocess import Popen, PIPE

class ArchwayJailCheck():
    def __init__( self, config_file='config.ini' ):
        # obtain the host name
        self.name = os.uname()[1]

        # read the config and setup the telegram
        self.read_config( config_file )
        self.setup_telegram()
        self.setup_archway_info()
        
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
        if "TELEGRAM_TOKEN" in os.environ:
            self.telegram_token = os.environ['TELEGRAM_TOKEN']
        elif 'Telegram' in self.config and 'telegram_token' in self.config['Telegram']:
            self.telegram_token = self.config['Telegram']['telegram_token']
        else:
            self.telegram_token = None
        
        if "TELEGRAM_CHAT_ID" in os.environ:
            self.telegram_chat_id = os.environ['TELEGRAM_CHAT_ID']
        elif 'Telegram' in self.config and 'telegram_chat_id' in self.config['Telegram']:
            self.telegram_chat_id = self.config['Telegram']['telegram_chat_id']
        else:
            self.telegram_chat_id = None

    def setup_archway_info( self ):
        '''
        Setup archway info
        '''
        # sleep time between delegation cycles
        if "SLEEP_TIME" in os.environ:
            self.sleep_time = int(os.environ['SLEEP_TIME'])
        elif 'sleep_time' in self.config['ARCHWAY']:
            self.sleep_time = int(self.config['ARCHWAY']['sleep_time'])
        else:
            self.sleep_time = 600

        # chain id
        if "CHAIN_ID" in os.environ:
            self.chain_id = os.environ['CHAIN_ID']
        else:
            self.chain_id = self.config['ARCHWAY']['chain_id']

        if "VALIDATOR_KEY" in os.environ:
            self.validator_key = os.environ['VALIDATOR_KEY']
        elif 'validator_key' in self.config['ARCHWAY']:
            self.validator_key = self.config['ARCHWAY']['validator_key']
        elif "VALIDATOR_ADDRESS" in os.environ:
            self.validator_key = os.environ['VALIDATOR_ADDRESS']
        elif 'validator_address' in self.config['ARCHWAY']:
            self.validator_key = self.config['ARCHWAY']['validator_address']
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
    
    def get_status( self ):
        '''
        Obtain the ARCHWAY status
        '''
        proc = Popen([ f"archwayd query staking validator {self.validator_key}" ], stdout=PIPE, shell=True)
        (out, err) = proc.communicate()
        line = self.parse_subprocess( out, 'jailed' )
        status = line.split(': ')[1]
        return status

    def check_cycle( self ):
        '''
        Delegation cycle for distributing rewards and sending them out
        '''
        status = self.get_status()
        if (status == 'true'):
            self.send( f" Archway node jailed" )
        # self.send( f"Sleeping { self.sleep_time } Seconds\n" )
        time.sleep( self.sleep_time )

def parse_arguments( ):
    '''
    Parse the arguments passed in
    '''
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', '-c', type=str, required=False, default='jail-check-config.ini', help='Configuration File')
    return parser.parse_args()

# Parse arguments
args = parse_arguments()

# Create the object
archway_bot = ArchwayJailCheck( args.config )

# run periodic delegation cycle
while True:
    archway_bot.check_cycle()
