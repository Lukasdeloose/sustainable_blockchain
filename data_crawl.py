#!/usr/bin/env python
# coding: utf-8


# Import libraries
import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt
import os
import sys

import requests
from bs4 import BeautifulSoup
from datetime import date

def clean_names(names):
    return names.str.lower().str.replace(' ', '').str.replace('-','')

# Top 100 mineable coins
url = 'https://coinmarketcap.com/coins/views/filter-non-mineable/'

r = requests.get(url) 

page_body = r.text
soup = BeautifulSoup(page_body, 'html.parser')
table = soup.find_all('div', class_='cmc-table__table-wrapper-outer')

# Get column names
column_names = []
for header in table[0].find_all('th'):
    column_names.append(str(header.string))
# Drop graphs
column_names.pop()
column_names.pop()

data = []
for row in table[2].find_all('tr')[1:]:
    new_row = []
    for entry in row:
        new_row.append(entry.text)
    new_row.pop()
    new_row.pop()
    data.append(new_row)
mineable_100 = pd.DataFrame(data, columns = column_names)
mineable_100 = mineable_100.set_index('Name')
mineable_100 = mineable_100.set_index(clean_names(mineable_100.index))
mineable_100 = mineable_100[['#', "Market Cap", "Price"]]
mineable_100 = mineable_100.rename(columns={'Market Cap': 'market_cap', 'Price':'price'})


# ## What to mine, nethash

# ### ASIC

url = 'https://whattomine.com/asic.json'

r = requests.get(url) 
data = r.json()

whattomine_asic = pd.DataFrame(data)
# normalize + clean names
whattomine_asic = pd.json_normalize(whattomine_asic['coins']).set_index(clean_names(whattomine_asic.index.str.lower()))
whattomine_asic['block_time'] = pd.to_numeric(whattomine_asic['block_time'])
whattomine_asic['nethash'] = pd.to_numeric(whattomine_asic['nethash'])
# Drop some columns
whattomine_asic = whattomine_asic[['tag','algorithm', 'block_time', 'difficulty24', 'nethash', 'block_reward24', 'exchange_rate24', 'exchange_rate_curr']]
whattomine_asic = whattomine_asic.rename(columns={'difficulty24':'difficulty','block_reward24':'block_reward', 'exchange_rate24': 'exchange_rate'})

# ### GPU
url = 'https://whattomine.com/coins.json'

r = requests.get(url) 
data = r.json()

whattomine_gpu = pd.DataFrame(data)
whattomine_gpu = pd.json_normalize(whattomine_gpu['coins']).set_index(clean_names(whattomine_gpu.index.str.lower()))
whattomine_gpu['block_time'] = pd.to_numeric(whattomine_gpu['block_time'])
whattomine_gpu['nethash'] = pd.to_numeric(whattomine_gpu['nethash'])
# Drop some columns
whattomine_gpu = whattomine_gpu[['tag','algorithm', 'block_time', 'difficulty24', 'nethash', 'block_reward24', 'exchange_rate24', 'exchange_rate_curr']]
whattomine_gpu = whattomine_gpu.rename(columns={'difficulty24':'difficulty','block_reward24':'block_reward', 'exchange_rate24': 'exchange_rate'})


# ## CoinWarz

url = 'https://www.coinwarz.com/v1/api/profitability?apikey=58467a6f2e2d4c65b7ef720b26137453&algo=all'
r = requests.get(url) 
data = r.json()

coinwarz = pd.DataFrame(data)
    
coinwarz = pd.json_normalize(coinwarz['Data'])
coinwarz = coinwarz.set_index(clean_names(coinwarz['CoinName']))

# Drop and rename some columns
coinwarz = coinwarz[['CoinTag', 'Algorithm','BlockTimeInSeconds', 'Difficulty', 'BlockReward', 'ExchangeRate']]
coinwarz = coinwarz.rename(columns={'CoinTag': 'tag', 'Algorithm': 'algorithm','BlockTimeInSeconds':'block_time',
                                    'Difficulty': 'difficulty', 'BlockReward': 'block_reward', 'ExchangeRate': 'exchange_rate'})
coinwarz['nethash_scraped'] = 0

# Here, the exchange rate is relative the bitcoin, except for bitcoin itself, where it is in US$

# # Combining the data


def check_missing(data):
    missing_data = result[data.isnull().any(axis=1)]
    return missing_data.shape[0]

whattomine = whattomine_gpu.append(whattomine_asic)
whattomine = whattomine.rename(columns={'nethash':'nethash_scraped'})

result = mineable_100.join(whattomine, how="left")

for coin in coinwarz.index:
    if coin not in whattomine.index.values:
        if coin in result.index:
            result.loc[coin, ['tag','algorithm','block_time','difficulty','nethash_scraped']] = coinwarz.loc[coin]
check_missing(result)
try:
	os.chdir(r"C:\Users\Admin\Documents\Burgie\2e_Master\Thesis\sustainable_blockchain")
except: 
    print("Something wrong with specified directory. Exception- ", sys.exc_info()) 


file = 'data_analysis/data/hist/mineable_100_' + date.today().strftime("%m-%d-%Y") + '.csv'

result.to_csv(file)






