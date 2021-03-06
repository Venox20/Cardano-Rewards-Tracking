import json
import requests
import subprocess
import re
import os.path
from datetime import datetime, timezone
import pytz
import argparse


parser = argparse.ArgumentParser(description="Log Rewards using Stake Address.")
parser.add_argument('--stake-addr', dest='stakeAdd', help='REQUIRED - Provie a Stake Address [stake.......]', required=True)
parser.add_argument('--tz', dest='tz', default='America/Los_Angeles', help='the local timezone name [Default: America/Los_Angeles]')


args = parser.parse_args()

# Get Epoch Number

response_Epoch = requests.get('http://127.0.0.1:12798/metrics').text
pattern = re.compile(r'cardano_node_metrics_epoch_int (\d*)')
matches = pattern.finditer(response_Epoch)

for match in matches:
    Epoch = match.group(1) 

print(Epoch)


# Get Date and Time  YYYY-mm-dd H:M:S

local_tz = pytz.timezone(args.tz)

now = datetime.now(tz=local_tz)
Date = now.strftime("%Y-%m-%d %H:%M:%S")

print(Date)


# Get ADA Price

response_ADA = requests.get("https://data.messari.io/api/v1/assets/ADA/metrics/market-data")
dict_ADA = response_ADA.json()
Price = dict_ADA['data']['market_data']['price_usd']

print(Price)


# Get Current balance

stakeAdd = args.stakeAdd
bal_cmd = f"cardano-cli query stake-address-info  --allegra-era --address {stakeAdd} --mainnet"

response_Bal = subprocess.run(bal_cmd, shell=True, capture_output=True, text=True)
list_Bal = json.loads(response_Bal.stdout)
Current_balance = (int((list_Bal[0])['rewardAccountBalance'])) / 1000000

print(Current_balance)


# Test for rewards.json, create file if it does not exist else append to file

check_File = os.path.isfile('rewards.json')


if check_File == True:
  print('Logging data to rewards.json')
  result_dictionary = {'Epoch': Epoch, 'Date': Date, 'Price': Price, 'Current_Balance': Current_balance}
  with open("rewards.json", "r+") as file:
    data = json.load(file)
    data.append(result_dictionary)
    file.seek(0)
    json.dump(data, file, indent=2)
else:
  print('Creating rewards.json to track your rewards balance.')
  result = [{'Epoch': Epoch, 'Date': Date, 'Price': Price, 'Current_Balance': Current_balance}]
  with open("rewards.json", "w") as f:
    json.dump(result, f, indent=2)
