# idep-sanford-autodelegation
IDEP Sanford Autodelegation

The script will automatically perform the calls for withdrawing the rewards and send the necessary transactions to delegate to the validator. 

The bot will print out the information to both the terminal and send telegram for notifications, if available. The information provided includes the transaction hashes and the delegation amount.

The amount to hold in reserve and refrain from delegation can be specified by the `reserve` token in the configuration file. The default amount is 0.1 if not specified.

When executing the script, if the password is not in the `IDEP_PASSWORD` environmental variable, it will check the config.ini file for the `password` variable. If the password is not found in either the environment or in the config.ini, a prompt will request a password for the wallet. The password is necessary for the delegation and reward transactions.

The config.ini can be used for loading in the variables or the user's environmental variables may be utilized.

Environmental Variables:
- `CHAIN_ID`: Chain ID
- `WALLET_NAME`: Wallet Name
- `WALLET_ADDRESS`: Wallet Address
- `VALIDATOR_ADDRESS`: Validator Address
- `IDEP_PASSWORD`: Wallet Password
- `IDEP_RESERVE`: The balance of IDEP to maintain in the wallet in decimal
- `TELEGRAM_TOKEN`: Telegram Token
- `TELEGRAM_CHAT_ID`: Telegram Chat ID
- `SLEEP_TIME`: Sleep Time for Delegation Cycles

Refer to the config.ini.example for a template to populate.

Assumptions:
- iond is in the path of the user
- nominal transaction path only
- no fees taken into account for the delegation transactions

Install python3 and install from the requirements file: <br>
```pip3 install -r requirements.txt```

Copy and populate the config.ini file with the necessary information: <br>
```cp config.ini.example config.ini```

Run the script:<br>
`python3 ./idep-sanford-autodelegation.py` <br>
Note: It will read in the configuration file local to the path of the script if not specified. <br>

Run the script with specifying the configuration file: <br>
`python3 ./idep-sanford-autodelegation.py -c <configuration file>`
