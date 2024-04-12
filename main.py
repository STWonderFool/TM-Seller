from datetime import datetime
from json import dumps
from json import load, dump
from os import environ
from random import randint
from re import findall
from statistics import median
from string import capwords
from struct import unpack
from threading import Thread
from time import sleep, time
from traceback import format_exc
from urllib.parse import quote

from MySteam.login import LoginExecutor
from MySteam.steam import get_sent_offers
from bs4 import BeautifulSoup
from notifiers import get_notifier
from printy import printy
from requests import get, post
from requests.utils import dict_from_cookiejar
from steampy.confirmation import ConfirmationExecutor

stop_flag = False


def get_user_agent_function():
    user_agents_list = ['Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/538 (KHTML, like Gecko) Chrome/36 Safari/538', 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2638.0 Safari/537.36', 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2018.0 Safari/537.36', 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.14 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.14', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.0.9757 Safari/537.36', 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2583.0 Safari/537.36', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.114 Safari/537.36', 'Mozilla/5.0 (Windows NT 8.0; WOW64) AppleWebKit/536.24 (KHTML, like Gecko) Chrome/32.0.2019.89 Safari/536.24', 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.68 Safari/537.36', 'Mozilla/5.0 (Windows NT 6.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.111 Safari/537.36,gzip(gfe)', 'Mozilla/5.0 (Windows NT 6.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.29 Safari/537.36', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.150 Safari/537.36', 'Google Chrome 51.0.2704.103 on Windows 10', 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2151.2 Safari/537.36', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.90 Safari/537.36 2345Explorer/9.4.3.17934', 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) coc_coc_browser/49.0 Chrome/43.0.2357.138 Safari/537.36', 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1204.0 Safari/537.1', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/533.16 (KHTML, like Gecko) Chrome/5.0.335.0 Safari/533.16', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1671.3 Safari/537.36', 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36,gzip(gfe)', 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/6.0 Safari/537.36', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/ (KHTML, like Gecko) Chrome/ Safari/', 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2419.0 Safari/537.36', 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Chrome/36.0.1985.125 CrossBrowser/36.0.1985.138 Safari/537.36', 'Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US) AppleWebKit/532.0 (KHTML, like Gecko) Chrome/3.0.195.4 Safari/532.0', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.111 Safari/537.36 TC2', 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.45 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.45', 'Mozilla/5.0 (Windows NT 10.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36', 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.97 Safari/537.36 Viv/1.9.818.49,gzip(gfe)', 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2673.0 Safari/537.36', 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.104 Safari/537.36', 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/536.36 (KHTML, like Gecko) Chrome/67.2.3.4 Safari/536.36', 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.61 Safari/537.36', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3258.0 Safari/537.36', 'Mozilla/5.0 (Windows NT 5.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.41 Safari/537.36', 'Mozilla/5.0 (Windows NT 6.4; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.89 Safari/537.36', 'Mozilla/5.0 (Windows NT 8.0; WOW64) AppleWebKit/536.23.38 (KHTML, like Gecko) Chrome/57.0.2740.20 Safari/536.23.38', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357 Safari/537.36', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.101 Safari/537.36 Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36', 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2851.0 Safari/537.36', 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3608.0 Safari/537.36', 'Mozilla/5.0 (Windows NT 6.0; Win64; x64) AppleWebKit/536.14 (KHTML, like Gecko) Chrome/32.0.2008.86 Safari/536.14', 'Mozilla/5.0 (Windows NT 6.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.99 Safari/537.36', 'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/537.35 (KHTML, like Gecko) Chrome/27.0.1453.0 Safari/537.35', 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) UR/61.1.3163.34 Chrome/63.0.3239.108  Safari/537.36', 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3058.0 Safari/537.36', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1615.0 Safari/537.36', 'Mozilla/5.0 (Windows NT 5.2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.57 Safari/537.36', 'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/537.36 (KHTML, like Gecko) coc_coc_browser/54.2.133 Chrome/48.2.2564.133 Safari/537.36', 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2568.0 Safari/537.36', 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3251.0 Safari/537.36', 'Mozilla/5.0 (Windows NT 8.1) AppleWebKit/537.27.34 (KHTML, like Gecko) Chrome/54.0.2725.19 Safari/537.27.34', 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36,gzip(gfe)', 'Mozilla/5.0 (Windows; U; Windows 95) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/13.0.782.43 Safari/535.1', 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Avast/70.0.917.102', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/46.0.1180.75 Safari/537.1', 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3282.92 Safari/537.36', 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.18 Safari/535.1', 'Mozilla/5.0 (Windows NT 8.1; WOW64) AppleWebKit/537.34 (KHTML, like Gecko) Chrome/36.0.2039.82 Safari/537.34', 'Mozilla/5.0 (Windows NT 6.2;en-US) AppleWebKit/537.32.36 (KHTML, live Gecko) Chrome/56.0.3075.83 Safari/537.32', 'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.16 Safari/537.36', 'Mozilla/5.0 (Windows NT 7.1; en-US) AppleWebKit/535.12 (KHTML, like Gecko) Chrome/28.0.1410.43 Safari/535.12', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2531.0 Safari/537.36', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.775 Safari/537.36', 'Mozilla/5.0 (Windows NT 6.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.152 Safari/537.36', 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.18 Safari/537.36', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/533.3 (KHTML, like Gecko) Chrome/5.0.355.0 Safari/533.3', 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.139 Safari/537.36', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.69 Safari/537.36', 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/38.0.2125.101 Safari/537.1', 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2714.0 Safari/537.36', 'Mozilla/5.0 (Windows NT 7.0; Win64; x64) AppleWebKit/535.15 (KHTML, like Gecko) Chrome/53.0.2710.66 Safari/535.15', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2883.95 Safari/537.36', '24.0.1284.0.0 (Windows NT 5.1) AppleWebKit/534.0 (KHTML, like Gecko) Chrome/24.0.1284.0.3.742.3 Safari/534.3', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3359.181 Safari/537.36', 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.102 Safari/537.36', 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2427.7 Safari/537.36', 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.62 Safari/537.36,gzip(gfe)', 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.144 Safari/537.36', 'Mozilla/5.0 (Windows NT 5.2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2327.5 Safari/537.36', 'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/30.0.963.12 Safari/535.11', 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36', 'Mozilla/5.0 (Windows NT 6.0; x64) AppleWebKit/537.78 (KHTML, like Gecko) Chrome/31.0.1650.16 Safari/537.78', 'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/537.22 (KHTML, like Gecko) Chrome/25.2.0.0 Safari/537.22', 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2255.0 Safari/537.36', 'Mozilla/5.0 (Windows NT 6.2;en-US) AppleWebKit/537.32.36 (KHTML, live Gecko) Chrome/53.0.3036.83 Safari/537.32', 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36 TungstenBrowser/2.0', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.20 (KHTML, like Gecko) Chrome/25.0.1330.0 Safari/537.20', 'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/537.21 (KHTML, like Gecko) Chrome/25.0.1353.0 Safari/537.21', 'Chrome/Soldier_0.3.0 (Windows NT 10.0)', 'Mozilla/5.0 (Windows NT 6.1; Windows NT 5.1; en-US) AppleWebKit/525.13 (KHTML, like Gecko) Chrome/stable Safari/525.13', 'Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US) AppleWebKit/532.1 (KHTML, like Gecko) Chrome/4.0.219.4 Safari/532.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2390.0 Safari/537.36', 'Mozilla/5.0 (Windows NT 5.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2199.73 Safari/537.36', 'Mozilla/5.0 (Windows; U; Windows NT 6.2; en-US) AppleWebKit/534.13 (KHTML, like Gecko) Chrome/9.0.597.42 Safari/534.13', 'Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US) AppleWebKit/533.4 (KHTML, like Gecko) Chrome/5.0.366.2 Safari/533.4', 'Windows / Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202 Safari/537.36', 'Mozilla/1.0 (Windows NT 4.0, Windows NT 5.0, Windows NT 5.1, Windows NT 6.0, Windows NT 6.1, Windows NT 6.2, Windows NT 10.0) AppleWebKit (KHTML, like Gecko) Safari/1 Chrome/1', 'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.39 Safari/537.36']

    useragent = user_agents_list[randint(1, 99)]
    return useragent

def account_id_to_steam_id(account_id):
    first_bytes = int(account_id).to_bytes(4, byteorder='big')
    last_bytes = 0x1100001.to_bytes(4, byteorder='big')
    return str(unpack('>Q', last_bytes + first_bytes)[0])

def telegram_notify(text):
    with open('Accounts & Settings.json') as file:
        settings = load(file)
        chat_id = settings['chat_id']
        token = settings['token']
    if chat_id and token:
        telegram = get_notifier('telegram')
        telegram.notify(chat_id=chat_id, token=token, message=text)

def message(account_name, color, text):
    printy(f'[m][{datetime.now().strftime("%H:%M")} {account_name}]@ [{color}]{text}')

def update_inventory(tm_api):
    url = 'https://market.csgo.com/api/v2/update-inventory/?key=' + tm_api
    for i in range(3):
        try:
            response = get(url, timeout=60)
            if response.json()['success']:
                return True
        except:
            continue
    return False

def check_active_offers(tm_api, counter=0):
    counter += 1
    if counter == 3:
        return False

    check_offers_url = 'https://market.csgo.com/api/v2/trade-request-give-p2p-all?key=' + tm_api
    try:
        response = get(check_offers_url, timeout=60)
        if response.json()['success']:
            return response.json()['offers']
        else:
            update_inventory(tm_api)
            return check_active_offers(tm_api, counter)
    except:
        return False

def get_my_items_to_list(tm_api):
    update_inventory(tm_api)
    url = 'https://market.csgo.com/api/v2/my-inventory/?key=' + tm_api
    for i in range(3):
        try:
            items = get(url, timeout=60).json()['items']
            return items
        except:
            continue
    return False

def get_single_item_id(item_name, account_name):
    url = 'https://steamcommunity.com/market/listings/730/'
    try:
        response = get(url + item_name, timeout=60).text
        item_id = findall(r'Market_LoadOrderSpread\(\s(\d+)', response)[0]
    except:
        message(account_name, 'r', 'Error getting item ID :(')
        return None
    message(account_name, 'n', 'Got new item ID ^ ^')
    return item_id

def register_trade(tm_api, trade_id, account_name):
    for i in range(10):
        url = f'https://market.csgo.com/api/v2/trade-ready?key={tm_api}&tradeoffer={trade_id}'
        try:
            response = get(url, timeout=60)
            if '"success":true' in response.text:
                message(account_name, 'y>', f'Offer #{trade_id} registered by TM')
                return
        except:
            pass
        message(account_name, 'r', 'Some error in registering offer')
        sleep(30)


class TmFighter:
    def __init__(self):
        self.account_name = input('Account name: ')
        while True:
            if self.account_name not in settings:
                self.account_name = input('Incorrect account name, try again: ')
            else:
                break

        # Login data
        self.login = settings[self.account_name]['login']
        self.password = settings[self.account_name]['password']
        self.tm_api = settings[self.account_name]['tm_api']
        self.mafile_name = settings[self.account_name]['maFile']

        self.user_agent = get_user_agent_function()

        # Fighter settings
        self.tm_coefficient = settings['tm_min_threshold']
        self.steam_coefficient = settings['steam_min_threshold']

        currency_codes = {"RUB": "5", "USD": "1", "EUR": "3"}
        self.currency_name = settings['currency']
        self.currency_code = currency_codes[self.currency_name]
        if self.currency_name == 'RUB':
            self.currency_coefficient = 100
        else:
            self.currency_coefficient = 1000

        self.price_per_days = settings['price_per_days']
        self.get_thresholds_every = settings['get_thresholds_every']
        self.list_items_every = settings['list_items_every']

        self.my_items_on_sale_dict = {}
        self.min_thresholds = {}
        self.error_getting_thresholds = []
        self.threads = []

        # Getting items ID
        with open('All Items ID.json') as file:
            self.all_items_id = load(file)
            self.cs_items_id = self.all_items_id['cs']

        self.run()

    def run(self):
        global stop_flag

        # Start sending items
        Thread(target=ItemsSender, args=(self.account_name, self.login, self.password, self.tm_api,
                                         self.mafile_name)).start()

        last_getting_thresholds_time = 0
        list_items_time = 0
        while True:
            if stop_flag:
                message(self.account_name, 'y', 'Exit from Fighter')
                return

            # List items every ..
            if time() - list_items_time > self.list_items_every * 3600:
                self.list_all_items()
                list_items_time = time()

            # Check my items on sale
            if not self.get_my_items_on_sell():
                continue

            # Getting min thresholds
            if time() - last_getting_thresholds_time > self.get_thresholds_every * 3600:
                self.get_min_thresholds_on_sell_items()
                last_getting_thresholds_time = time()

            # Fight prices!
            changing_prices_time = time()
            self.change_item_prices()
            message(self.account_name, 'w', f'Cycle time {round((time() - changing_prices_time) / 60, 2)} minutes')

    def list_all_items(self):
        items = get_my_items_to_list(self.tm_api)
        if not items:
            message(self.account_name, 'n>', 'No items to list')
            return

        message(self.account_name, 'n>', 'Updated inventory, starting list items..')
        for i in items:
            item_id = i['id']
            url = f'https://market.csgo.com/api/v2/add-to-sale?key={self.tm_api}&id={item_id}&price=1000000000&' \
                  f'cur={self.currency_name}'
            try:
                get(url, timeout=60)
            except:
                continue
            message(self.account_name, 'n>', f'{i["market_hash_name"]} is listed!')

        message(self.account_name, 'n', 'Listed All items!')

    def get_min_thresholds_on_sell_items(self):
        self.min_thresholds = {}
        message(self.account_name, 'm', 'Getting min thresholds..')
        self.get_min_thresholds_from_list(self.my_items_on_sale_dict)

        for i in range(3):
            message(self.account_name, 'r', f'Errors getting min thresholds: {len(self.error_getting_thresholds)}'
                                            f' (Iter {i + 1})')
            if len(self.error_getting_thresholds) < 2:
                break
            temp_errors = self.error_getting_thresholds
            self.error_getting_thresholds = []
            self.get_min_thresholds_from_list(temp_errors)

        self.all_items_id['cs'] = self.cs_items_id
        with open('All Items ID.json', 'w') as file:
            dump(self.all_items_id, file)

    def get_min_thresholds_from_list(self, my_list):
        counter = 0

        for item_name in my_list:
            thread = Thread(target=self.get_min_threshold, args=(item_name,))
            self.threads.append(thread)
            counter += 1

            if counter > 0 and counter % 60 == 0:
                self.start_and_join_threads()
        self.start_and_join_threads()

    def get_min_threshold(self, item_name):
        tm_url = f'https://market.csgo.com/api/v2/get-list-items-info?key={self.tm_api}&list_hash_name[]=' + item_name
        try:
            response = get(tm_url, timeout=60)
            if response.status_code != 200:
                message(self.account_name, 'r', 'TM is not responding')
                return self.error_getting_thresholds.append(item_name)
            try:
                history = response.json()['data'][item_name]['history']
            except:
                return
        except:
            return self.error_getting_thresholds.append(item_name)

        prices = []
        for i in history:
            if time() - i[0] > 86400 * self.price_per_days:
                break
            prices.append(i[1])

        if not prices:
            if len(history) > 10:
                for i in range(10):
                    prices.append(history[i][1])
            else:
                for i in range(len(history)):
                    prices.append(history[i][1])

        average_tm = round(median(prices), 2)
        steam_buy_order = self.get_steam_buy_order(item_name)
        if not steam_buy_order:
            return self.error_getting_thresholds.append(item_name)

        message(self.account_name, 'm', f'{item_name} - TM: {average_tm}, Steam S/O: {steam_buy_order}')

        tm_threshold = average_tm * self.tm_coefficient
        steam_threshold = steam_buy_order * self.steam_coefficient
        if tm_threshold < steam_threshold:
            message(self.account_name, '<m', 'TM price is too low, min threshold will be set by Steam S/O')
            tm_threshold = steam_threshold
        self.min_thresholds[item_name] = tm_threshold

    def get_steam_buy_order(self, item_name):
        if item_name in self.cs_items_id:
            item_id = self.cs_items_id[item_name]
        else:
            item_id = get_single_item_id(item_name, self.account_name)
            if not item_id:
                return None
            self.cs_items_id[item_name] = item_id

        url = f'https://steamcommunity.com/market/itemordershistogram?country=RU&language=english&currency=' \
              f'{self.currency_code}&item_nameid=' + item_id

        headers = {
            'Referer': quote(f'https://steamcommunity.com/market/listings/730/{item_name}'),
            'User-Agent': self.user_agent
        }

        try:
            response = get(url, headers=headers, timeout=60)
            if response.status_code != 200:
                message(self.account_name, 'r', 'Steam is not responding')
                return None
        except:
            message(self.account_name, 'r', 'Steam is not responding..')
            return None
        try:
            steam_buy_order = response.json()['sell_order_graph'][0][0]
            return steam_buy_order
        except:
            try:
                steam_buy_order = response.json()['buy_order_graph'][0][0]
                return steam_buy_order
            except:
                message(self.account_name, 'r', f'{item_name} - No listings for this item')
                return None

    def start_and_join_threads(self):
        for thread in self.threads:
            thread.start()
        for thread in self.threads:
            thread.join()

        self.threads = []

    def get_my_items_on_sell(self):
        self.my_items_on_sale_dict = {}
        url = 'https://market.csgo.com/api/v2/items?key=' + self.tm_api
        try:
            non_filtered_list = get(url, timeout=60).json()['items']
        except:
            message(self.account_name, 'r', 'TM is not responding')
            return False

        if not non_filtered_list:
            if not get_my_items_to_list(self.tm_api):
                message(self.account_name, 'y', 'All Items are Sold!')
                telegram_notify(f'All Items of {capwords(self.account_name)} are Sold!')
                global stop_flag
                stop_flag = True
            else:
                self.list_all_items()
            return False

        for i in non_filtered_list:
            if i['status'] != '1':
                continue

            item_name, item_price, item_id = i['market_hash_name'], i['price'], i['item_id']
            if item_name not in self.my_items_on_sale_dict:
                self.my_items_on_sale_dict[item_name] = item_price, [item_id]
            else:
                self.my_items_on_sale_dict[item_name][1].append(item_id)
                last_price = self.my_items_on_sale_dict[item_name][0]
                if item_price > last_price:
                    self.my_items_on_sale_dict[item_name] = item_price, self.my_items_on_sale_dict[item_name][1]
        return True

    def change_item_prices(self):
        for item_name in self.my_items_on_sale_dict:
            if item_name in self.min_thresholds:
                my_price, item_ids = self.my_items_on_sale_dict[item_name]
                self.change_item_price(item_name, my_price * self.currency_coefficient, item_ids)
            else:
                self.get_min_threshold(item_name)

    def get_max_price(self, item_name):
        message(self.account_name, 'm>', f'Getting max price of {item_name}')
        url = f'https://market.csgo.com/api/v2/get-list-items-info?key={self.tm_api}&list_hash_name[]=' + item_name
        try:
            response = get(url, timeout=60)
            max_price = response.json()['data'][item_name]['max']
            return max_price * self.currency_coefficient
        except:
            return 1000000000

    def change_item_price(self, item_name, my_price, item_ids):
        get_prices_url = f'https://market.csgo.com/api/v2/search-item-by-hash-name-specific?key={self.tm_api}' \
                         f'&hash_name=' + item_name
        try:
            data = get(get_prices_url, timeout=60).json()['data']
        except:
            message(self.account_name, 'r', f'Error getting prices on TM - {item_name}')
            return

        prices = []
        for i in data:
            if str(i['id']) in item_ids:
                continue
            prices.append(i['price'])

        min_threshold = self.min_thresholds[item_name] * self.currency_coefficient

        new_price = 1000000000
        for price in prices:
            if price - 1 > min_threshold:
                new_price = price - 1
                break

        if new_price > min_threshold * 4:
            new_price = self.get_max_price(item_name)

        if new_price == my_price:
            if not prices:
                return message(self.account_name, 'g', f'Skip, no competitors {item_name}')
            return message(self.account_name, 'g',
                           f'Skip {item_name}, Min price: {prices[0] / self.currency_coefficient}, '
                           f'My price: {my_price / self.currency_coefficient}, '
                           f'Min Threshold: {round(min_threshold / self.currency_coefficient, 2)}')

        for item_id in item_ids:
            url = f'https://market.csgo.com/api/v2/set-price?key={self.tm_api}&item_id={item_id}' \
                  f'&price={new_price}&cur={self.currency_name}'
            try:
                get(url, timeout=60)
            except:
                continue

        if not prices:
            return message(self.account_name, 'b>',
                           f'Changed price of {item_name} to {new_price / self.currency_coefficient},'
                           f' No competitors. Min threshold: {round(min_threshold / self.currency_coefficient, 2)}')
        message(self.account_name, 'b>', f'Changed price of {item_name} to {new_price / self.currency_coefficient},'
                                         f' First price: {prices[0] / self.currency_coefficient}, Min threshold: {round(min_threshold / self.currency_coefficient, 2)}')


class ItemsSender:
    def __init__(self, account_name, login, password, tm_api, mafile_name):
        with open(f'mafiles/{mafile_name}') as second_file:
            mafile = load(second_file)
            self.account_name = account_name
            self.login = login
            self.password = password
            self.tm_api = tm_api
            self.shared_secret = mafile['shared_secret']
            self.steam_id = str(mafile['Session']['SteamID'])
            self.identity_secret = mafile['identity_secret']

        while True:
            if self.login_to_account() and self.get_access_token():
                self.steam_api = self.get_my_steam_api()
                break

        self.sent_offers_messages = []

        self.run()

    def run(self):
        global stop_flag

        try:
            Thread(target=self.ping_pong_cycle).start()
        except:
            telegram_notify(f'Critical error: {format_exc()}')

        while True:
            try:
                while True:
                    if stop_flag:
                        message(self.account_name, 'y', 'Exit from sender')
                        return

                    message(self.account_name, 'y>', 'Checking for new trades..')
                    offers = check_active_offers(self.tm_api)
                    if not offers:
                        message(self.account_name, 'y>', 'No active offers')
                        sleep(30)
                        continue

                    offers = self.filter_offers_list(offers)
                    if not offers:
                        message(self.account_name, 'y>', 'No active offers')
                        sleep(30)
                        continue
                    try:
                        self.create_offers(offers)
                    except:
                        message(self.account_name, 'r', 'Some error in creating offers')

                    message(self.account_name, 'y>', 'Sent all offers!')
                    sleep(30)
            except:
                telegram_notify(f'Critical error in Sender module {self.account_name}')
                print(format_exc())

    def ping_pong_cycle(self):
        global stop_flag

        url = 'https://market.csgo.com/api/v2/ping-new?key=' + self.tm_api
        while True:
            if stop_flag:
                message(self.login, 'y', 'Exit from ping-pong')
                return

            while True:
                try:
                    json = {'access_token': self.access_token}
                    response = post(url, json=json, timeout=60).text
                    if 'success":true' in response:
                        message(self.login, 'w', f'Ping pong - {response}')
                        break
                    message(self.login, 'r', f'Ping pong - {response}')
                    if 'invalid_access_token' in response or 'token expired' in response:
                        self.get_access_token()
                except:
                    continue
            sleep(160)

    def get_access_token(self):
        url = 'https://steamcommunity.com/pointssummary/ajaxgetasyncconfig'
        try:
            token = self.session.get(url).json()['data']['webapi_token']
            message(self.login, 'n', 'Got access token!')
            self.access_token = token
            return True
        except:
            message(self.login, 'r', 'Error getting access token, sleeping for 30s..')
            if not self.is_session_alive():
                message(self.login, 'r', 'Seems like session is expired, need relogin..')
                self.login_to_account()

        sleep(30)
        return self.get_access_token()

    def is_session_alive(self):
        try:
            main_page_response = self.session.get('https://steamcommunity.com/', timeout=60)
            response = self.login.lower() in main_page_response.text.lower()
        except:
            return False
        return response

    def get_my_steam_api(self):
        global stop_flag

        url = 'https://steamcommunity.com/dev/apikey'
        try:
            response = self.session.get(url, timeout=60)
            soup = BeautifulSoup(response.content, 'html.parser')
            steam_api = soup.find('div', id='bodyContents_ex').p.text.split()[1]
            return steam_api
        except:
            message(self.account_name, 'r', f'Error getting your steam api')
            stop_flag = True

    def filter_offers_list(self, offers):
        for offer in offers.copy():
            if offer['tradeoffermessage'] in self.sent_offers_messages:
                offers.remove(offer)
        return offers

    def create_single_offer(self, offer):
        create_offer_link = 'https://steamcommunity.com/tradeoffer/new/send'
        headers = {
            'Referer': f'https://steamcommunity.com/tradeoffer/new/?partner={offer["partner"]}&token={offer["token"]}',
            'Origin': 'https://steamcommunity.com'}
        json_tradeoffer = f'{{"newversion": "true", "version": 2, "me": {{"assets": {dumps(offer["items"])},' \
                          f' "currency": [], "ready": "false"}}, "them": {{"assets": [], "currency": [], "ready": "false"}}}}'
        trade_offer_create_params = {'trade_offer_access_token': offer["token"]}
        data = {'sessionid': self.cookies['sessionid'], 'serverid': 1,
                'partner': account_id_to_steam_id(offer['partner']),
                'tradeoffermessage': offer['tradeoffermessage'], 'json_tradeoffer': json_tradeoffer,
                'captcha': '', 'trade_offer_create_params': dumps(trade_offer_create_params)}

        return self.session.post(create_offer_link, data=data, headers=headers)

    def confirm_all_trade_offers(self):
        for i in range(3):
            try:
                message(self.account_name, 'y', 'Confirming..')
                self.confirmation_executor.allow_only_trade_offers()
                return
            except:
                printy(f'[r]{format_exc()}')
                sleep(60)

    def create_offers(self, offers):
        counter = 0
        for offer in offers:
            counter += 1
            try:
                response = self.create_single_offer(offer)
            except:
                message(self.login, 'r', 'Steam is not responding..')
                continue

            # If session expired
            if not response.json():
                if not self.is_session_alive():
                    message(self.login, 'r', 'Seems like session is expired, need relogin..')
                    self.login_to_account()
                    return
                continue

            # If session is ok, and trade offer need confirmation
            if response.status_code == 200:
                trade_id = response.json()['tradeofferid']
                self.sent_offers_messages.append(offer['tradeoffermessage'])
                Thread(target=register_trade, args=(self.tm_api, trade_id, self.login)).start()
                Thread(target=self.cancel_trade_offer, args=(trade_id,)).start()
                message(self.login, 'y>', f'Offer #{counter}/{len(offers)} creating..')
                sleep(1)
                continue

            # If error in sending offer
            else:
                message(self.login, 'r', f'Error sending offer {response.text}')
        self.confirm_all_trade_offers()

    def login_to_account(self):
        global stop_flag

        message(self.account_name, 'y>', 'Logining to account..')
        try:
            self.session = LoginExecutor(self.login, self.password, self.shared_secret).run()

        except:
            telegram_notify(f'Unexpected error in login to {self.account_name}')
            message(self.account_name, 'r', 'Unexpected error in login')
            sleep(60)
            return False

        else:
            message(self.account_name, 'n', 'Success login')
            telegram_notify(f'Success login to {self.account_name}')
            self.cookies = dict_from_cookiejar(self.session.cookies)
            self.confirmation_executor = ConfirmationExecutor(self.identity_secret, self.steam_id, self.session)
            return True

    def cancel_trade_offer(self, trade_id):
        sleep(600)
        url = 'https://steamcommunity.com/tradeoffer/' + trade_id + '/cancel'
        try:
            self.session.post(url, data={'sessionid': self.cookies['sessionid']}, timeout=60)
            message(self.login, 'n', f'Canceled offer #{trade_id}')
        except:
            message(self.login, 'r', 'Trade offer cancellation error')
            return self.cancel_trade_offer(trade_id)


printy('[m]Created by@ [w]vk.com/YunosRage\n')
with open('Accounts & Settings.json') as file:
    settings = load(file)
    proxy = settings['proxy']
    if proxy:
        environ['https_proxy'] = proxy
        message('', 'y', f'Working with {proxy} proxy\n')

try:
    TmFighter()
except:
    print(format_exc())
input('Press enter to Exit')
