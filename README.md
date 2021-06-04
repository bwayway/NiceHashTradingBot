# Nice Hash Trading Bot

A python script to trade BTC mined on Nicehash to other cryptos listed on the Nicehash marketplace.

## Setting Up

**Please note that this script makes use of the [Selenium](https://selenium-python.readthedocs.io/) module. Make sure the drivers are up to date. I've included the most up to date drivers as of 6/3/2021 in the "drivers" folders**

The script can be run out of the box on a windows machine, as long as you're using either Chrome, Edge, or Firefox as your browser.

### config.js

The config.js file (.src/config/config.js) is where the nicehash settings are stored, including login information, and percentage of BTC you want to trade per token:

#### Login Information

Insert your Nicehash username and password here:

```json
{
  "Login": [
    {
      "username": "",
      "password": ""
    }
  ],
```

#### Token Exchange Percentages

The percentage of your BTC that you want to trade for another crypto currency. Tokens/Coins are listed by their ticker.

Percentage must be a whole number. For example "ETH": 10 is equal to 10% of your BTC to be traded as Ethereum.

Sum of percentages cannot be more than 100 or less than 0.

```json
  "Token Exchange Percentages": [
    {
      "AAVE": 0,
      "AERGO": 0,
      "ANT": 0,
      "AOA": 0,
      "AST": 0,
      "BAND": 0,
      "BAT": 0,
      "BCH": 0,
      "BNT": 0,
      "BTG": 0,
      "CVC": 0,
      "DASH": 0,
      "DATA": 0,
      "DOGE": 0,
      "ELF": 0,
      "ENJ": 0,
      "EOS": 0,
      "ETH": 0,
      "FET": 0,
      "FTM": 0,
      "GTO": 0,
      "KEY": 0,
      "KNC": 0,
      "LBA": 0,
      "LINK": 0,
      "LOOM": 0,
      "LTC": 0,
      "MATIC": 0,
      "MITH": 0,
      "MTL": 0,
      "NEXO": 0,
      "OMG": 0,
      "1INCH": 0,
      "POLY": 0,
      "POWR": 0,
      "PPT": 0,
      "RDN": 0,
      "REP": 0,
      "RVN": 0,
      "SNT": 0,
      "STORJ": 0,
      "SUSHI": 0,
      "SXP": 0,
      "UNI": 0,
      "WBTC": 0,
      "XLM": 0,
      "XMR": 0,
      "XRP": 0,
      "YFI": 0,
      "ZEC": 0,
      "ZRX": 0
    }
  ],
```

#### Settings

"Country" is the country you want to base your account from. Some countries do not allow for crypto trading at the moment. Using a VPN or deploying to a server in a country where it is legal will resolve this issue.

"Driver" Is to configure the driver for your web browser. The following values are accepted:

- "Chrome" (Google Chrome)
- "Edge" (Microsoft Edge)
- "Firefox" (Mozilla Firefox)

```json
  "Settings": [
    {
      "Country": "",
      "Driver": ""
    }
  ],
```

#### Logging

The location of the log files. Unless you want the logs to write to a different location, this can be left as the default.

```json
  "Logging": [
    {
      "LogFileLocation": "./src/config/logs"
    }
  ]
}
```

## Email_setup.py

I've included a script I use to email me a report at the end of each run. The script takes advantage of the [Mailgun](https://www.mailgun.com/) api. Simply replace/fill out the boilerplate information in the script with your personal Mailgun information.

You can also modify it to use the smtp module included in python, if you choose to go that route.

## Deployment:

If you're like me, you'll probably try to schedule the script to automate it. I had a lot of trouble doing so on [Heroku](https://www.heroku.com), but was able to get it to work. Feel free to modify the script to fit which ever platform you decide to use.

## License

[MIT](https://choosealicense.com/licenses/mit/)
