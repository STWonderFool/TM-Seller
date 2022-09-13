from datetime import datetime
from json import dumps
from json import load, dump
from os import environ
from re import findall
from statistics import median
from string import capwords
from struct import unpack
from threading import Thread
from time import sleep, time
from traceback import format_exc

from bs4 import BeautifulSoup
from notifiers import get_notifier
from printy import printy
from requests import get, Session
from requests.utils import dict_from_cookiejar
from steampy.confirmation import ConfirmationExecutor
from steampy.exceptions import CaptchaRequired, InvalidCredentials
from steampy.login import LoginExecutor

stop_flag = False


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


def ping_pong(account_name, tm_api):
    global stop_flag
    update_inventory(tm_api)

    url = 'https://market.csgo.com/api/v2/ping?key=' + tm_api
    while True:
        if stop_flag:
            message(account_name, 'y', 'Exit from ping-pong')
            return

        while True:
            try:
                response = get(url, timeout=60).json()
            except:
                continue
            if response['success']:
                message(account_name, 'w', f'Ping pong - {response}')
                break
            message(account_name, 'r', f'Ping pong - {response}')
        sleep(80)


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
        response = get(url + item_name).text
        item_id = findall(r'Market_LoadOrderSpread\(\s(\d+)', response)[0]
    except:
        message(account_name, 'r', 'Error getting item ID :(')
        return None
    message(account_name, 'n', 'Got new item ID ^ ^')
    return item_id


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
        try:
            response = get(url)
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

        self.session = Session()
        while True:
            if self.login_to_account():
                self.steam_api = self.get_my_steam_api()
                break

        self.sent_offers_messages = []

        self.run()

    def run(self):
        global stop_flag

        try:
            Thread(target=self.cancel_all_offers_older_10_min).start()
            Thread(target=ping_pong, args=(self.account_name, self.tm_api)).start()
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
                    try:
                        self.create_offers(offers)
                    except:
                        message(self.account_name, 'r', 'Some error in creating offers')

                    message(self.account_name, 'y>', 'Sent all offers!')
                    sleep(30)
            except:
                telegram_notify(f'Critical error in Sender module {self.account_name}')
                print(format_exc())

    def is_session_alive(self):
        main_page_response = self.session.get('https://steamcommunity.com/')
        try:
            response = self.login.lower() in main_page_response.text.lower()
        except:
            return False
        return response

    def get_my_steam_api(self):
        global stop_flag

        url = 'https://steamcommunity.com/dev/apikey'
        try:
            response = self.session.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            steam_api = soup.find('div', id='bodyContents_ex').p.text.split()[1]
            return steam_api
        except:
            message(self.account_name, 'r', f'Error getting your steam api')
            stop_flag = True

    def cancel_all_offers_older_10_min(self):
        global stop_flag

        while True:
            if stop_flag:
                return
            sleep(90)
            url = f'http://api.steampowered.com/IEconService/GetTradeOffers/v1/?key={self.steam_api}&get_sent_offers=1&active_only=1'

            try:
                trade_offers = get(url).json()['response']['trade_offers_sent']
                for i in trade_offers:
                    if time() - i['time_created'] > 600:
                        try:
                            self.cancel_trade_offer(i['tradeofferid'])
                        except:
                            message(self.account_name, 'r', 'Trade offer cancellation error')
            except:
                pass

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

    def confirm_trade_offer(self, trade_id):
        for i in range(3):
            try:
                self.confirmation_executor.send_trade_allow_request(trade_id)
            except:
                sleep(60)

    def create_offers(self, offers):
        counter = 0
        for offer in offers:
            counter += 1
            try:
                response = self.create_single_offer(offer)
            except:
                message(self.account_name, 'r', 'Steam is not responding..')
                continue

            # If session expired
            if not response.json():
                if not self.is_session_alive():
                    message(self.account_name, 'r', 'Seems like session is expired, need relogin..')
                    self.login_to_account()
                    return
                continue

            # If session is ok, and trade offer need confirmation
            if response.status_code == 200:
                trade_id = response.json()['tradeofferid']
                Thread(target=self.confirm_trade_offer, args=(trade_id,)).start()
                message(self.account_name, 'y>', f'Offer #{counter}/{len(offers)} creating..')
                self.sent_offers_messages.append(offer['tradeoffermessage'])
                continue

            # If error in sending offer
            else:
                message(self.account_name, 'r', f'Error sending offer {response.text}')

    def login_to_account(self):
        global stop_flag

        message(self.account_name, 'y>', 'Logining to account..')
        try:
            LoginExecutor(self.login, self.password, self.shared_secret, self.session).login()

        except InvalidCredentials:
            telegram_notify(f'Incorrect login/password in {self.account_name} or steam lags')
            message(self.account_name, 'r', 'Incorrect login/password or steam lags, sleeping for next 60 seconds..')
            sleep(60)
            return False

        except CaptchaRequired:
            telegram_notify(f'Captcha required on {self.account_name}')
            message(self.account_name, 'r', 'Captcha required, sleeping for next 60 seconds..')
            sleep(60)
            return False

        except:
            telegram_notify(f'Unexpected error in login to {self.account_name}')
            message(self.account_name, 'r', 'Unexpected error in login')
            sleep(30)
            return False

        else:
            message(self.account_name, 'n', 'Success login')
            telegram_notify(f'Success login to {self.account_name}')
            self.cookies = dict_from_cookiejar(self.session.cookies)
            self.confirmation_executor = ConfirmationExecutor(self.identity_secret, self.steam_id, self.session)
            return True

    def cancel_trade_offer(self, trade_id):
        url = 'https://steamcommunity.com/tradeoffer/' + trade_id + '/cancel'
        return self.session.post(url, data={'sessionid': self.cookies['sessionid']})


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
