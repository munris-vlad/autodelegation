# archway-autodelegation
Archway Autodelegation

The config.ini can be used for loading in the variables or the user's environmental variables may be utilized.

Environmental Variables:
- `CHAIN_ID`: Chain ID
- `WALLET_NAME`: Wallet Name
- `WALLET_ADDRESS`: Wallet Address
- `VALIDATOR_ADDRESS`: Validator Address
- `ARCHWAY_PASSWORD`: Wallet Password
- `ARCHWAY_RESERVE`: The balance of archway to maintain in the wallet in decimal
- `TELEGRAM_TOKEN`: Telegram Token
- `TELEGRAM_CHAT_ID`: Telegram Chat ID
- `SLEEP_TIME`: Sleep Time for Delegation Cycles

Refer to the config.ini.example for a template to populate.

Install python3 and install from the requirements file: <br>
```pip3 install -r requirements.txt```

Copy and populate the config.ini file with the necessary information: <br>
```cp config.ini.example config.ini```

Run the script:<br>
`python3 ./archway-autodelegation.py` <br>
Note: It will read in the configuration file local to the path of the script if not specified. <br>

Run the script with specifying the configuration file: <br>
`python3 ./archway-autodelegation.py -c <configuration file>`
