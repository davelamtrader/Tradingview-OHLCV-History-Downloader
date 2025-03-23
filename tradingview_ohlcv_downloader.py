import requests
import csv
import json
import time
from datetime import date, datetime, timedelta
import pandas as pd
import os
import random
from tvDatafeed import TvDatafeed, Interval
import multiprocessing


def get_crypto_top_24h_gainers(min_cap, min_chg_pct, scheduled_time):
    url = 'https://scanner.tradingview.com/crypto/scan'
    form = {"filter":[{"left":"market_cap_calc","operation":"egreater","right":min_cap},{"left":"change","operation":"greater","right":min_chg_pct}],
            "options":{"lang":"en"},"markets":["crypto"],"symbols":{"query":{"types":[]},"tickers":[]},
            "columns":["base_currency_logoid","currency_logoid","name","Recommend.MA","close","SMA20","BB.upper","BB.lower","change|60","change","change|240","change|1W","change|1M","VWMA","24h_vol_change|5","description","type","subtype","update_mode","exchange","pricescale","minmov","fractional","minmove2","Rec.VWMA"],
            "sort":{"sortBy":"change","sortOrder":"desc"},"price_conversion":{"to_symbol":False},"range":[0,1000]}
    headers = {
        #'Cookies': '_sp_ses.cf1a=*; device_t=dE9WUTow.h0NMV2mlguKF2bvY-SVxkiVa5SJ3vZYhdD5J6CBsj8Y; sessionid=nzfp4lbphx4bleovlqlg3cssqxlc7sv3; sessionid_sign=v1:5QANGG5krbtDis2SxPSDWh81RIp/57dHjywwy1oeN0w=; tv_ecuid=3c9492ac-a984-4842-b7ea-3093efae596c; _sp_id.cf1a=.1689768028.1.1691893661.1689768028.578022c0-c3f1-42cf-b588-fbaf2d6b7539',
        'Referer': 'https://www.tradingview.com/',
        'Sec-Fetch-Mode': 'cors'
    }
    response = requests.post(url, json=form, headers=headers)
    data = response.json() if response.status_code == 200 else None
    log_dt = (scheduled_time + timedelta(hours=15)).strftime('%Y%m%d-%H%M')

    subfolder = 'Tradingview/screener result'
    if not os.path.exists(subfolder):
        os.makedirs(subfolder)
    filepath = os.path.join(subfolder, f'crypto_top24h_gainers_mktcap-{min_cap}_change-{min_chg_pct}%_{log_dt}.json')
    with open(filepath, 'w') as json_file:
        json.dump(data, json_file)

    table_head = form['columns'] #.insert(0, 'tradingview_name')
    table_head.insert(0, 'tradingview_name')
    print(table_head)
    table_values_list = []
    data_dict = {}
    for item, i in zip(data['data'], range(1, len(data['data']) + 1)):
        tv_name = item['s']
        d = item['d']
        d.insert(0, tv_name)
        table_values_list.append(d)
        single_dict = dict(zip(table_head, d))
        data_dict[i] = single_dict

    print(data_dict)
    df = pd.DataFrame().from_dict(data_dict, orient='index')
    print(df)
    csv_path = os.path.join(subfolder, f'crypto_top24h_gainers_mktcap-{min_cap}_change-{min_chg_pct}%_{log_dt}.csv')
    df.to_csv(csv_path, index=False)

    return data, df


def get_symbols_list_by_country(country):
    link = f'https://symbol-search.tradingview.com/symbol_search/v3/?text=&hl=1&country={country}&lang=en&search_type=stocks&domain=production'
    response = requests.get(link)
    count = response.json()['symbols_remaining'] + 50 if 'symbols_remaining' in list(response.json().keys()) else None
    if count is None:
        get_symbols_list_by_country(country)

    if count >= 1:
        starts = [i for i in range(1, count, 50)]
        print(starts)
        ends = [i for i in range(50, count + 1, 50)]
        print(ends)
        symbols_data = []
        for start, end in zip(starts, ends):
            url = f'https://symbol-search.tradingview.com/symbol_search/v3/?text=&hl=1&country={country}&lang=en&search_type=stocks&start={start}&end={end}&domain=production'
            print(url)
            response = requests.get(url)
            raw_data = response.json() if response.status_code == 200 else None
            data = raw_data['symbols'] if type(raw_data) == dict and 'symbols' in list(raw_data.keys()) else raw_data
            if response.status_code == 200:
                symbols_data.extend(data)
                print(data)
            elif response.status_code == 400:
                print(response.text)
                break
            time.sleep(0.2)

        sub = 'symbols'
        os.makedirs(sub, exist_ok=True)
        filepath = os.path.join(sub, f'{country}_stock_symbols.json')
        with open(filepath, 'w') as json_file:
            json.dump(symbols_data, json_file)
        print(f'Stock symbols data from {country} successfully saved!')

        return symbols_data


def get_all_futures_symbols():
    link = 'https://symbol-search.tradingview.com/symbol_search/v3/?text=&hl=1&exchange=&lang=en&search_type=futures&domain=production'
    response = requests.get(link)
    count = response.json()['symbols_remaining'] + 50 if 'symbols_remaining' in list(response.json().keys()) else None
    if count is None:
        get_all_futures_symbols()

    if count >= 1:
        starts = [i for i in range(1, count, 50)]
        print(starts)
        ends = [i for i in range(50, count + 1, 50)]
        print(ends)
        symbols_data = []
        for start, end in zip(starts, ends):
            url = f'https://symbol-search.tradingview.com/symbol_search/v3/?text=&hl=1&exchange=&lang=en&search_type=futures&start={start}&end={end}&domain=production'
            print(url)
            response = requests.get(url)
            raw_data = response.json() if response.status_code == 200 else None
            data = raw_data['symbols'] if type(raw_data) == dict and 'symbols' in list(raw_data.keys()) else raw_data
            if response.status_code == 200:
                symbols_data.extend(data)
                print(data)
            else:
                print(response.text)
            time.sleep(0.2)

        sub = 'symbols'
        os.makedirs(sub, exist_ok=True)
        filepath = os.path.join(sub, f'all_futures_symbols.json')
        with open(filepath, 'w') as json_file:
            json.dump(symbols_data, json_file)
        print(f'All futures symbols data successfully saved!')

        return symbols_data


def get_all_indices_symbols():
    link = 'https://symbol-search.tradingview.com/symbol_search/v3/?text=&hl=1&exchange=&lang=en&search_type=index&domain=production'
    response = requests.get(link)
    count = response.json()['symbols_remaining'] + 50 if 'symbols_remaining' in list(response.json().keys()) else None
    if count is None:
        get_all_indices_symbols()

    if count >= 1:
        starts = [i for i in range(1, count, 50)]
        print(starts)
        ends = [i for i in range(50, count + 1, 50)]
        print(ends)
        symbols_data = []
        for start, end in zip(starts, ends):
            url = f'https://symbol-search.tradingview.com/symbol_search/v3/?text=&hl=1&exchange=&lang=en&search_type=index&start={start}&end={end}&domain=production'
            print(url)
            response = requests.get(url)
            raw_data = response.json() if response.status_code == 200 else None
            data = raw_data['symbols'] if type(raw_data) == dict and 'symbols' in list(raw_data.keys()) else raw_data
            if response.status_code == 200:
                symbols_data.extend(data)
                print(data)
            else:
                print(response.text)
            time.sleep(0.2)

        sub = 'symbols'
        os.makedirs(sub, exist_ok=True)
        filepath = os.path.join(sub, f'all_indices_symbols.json')
        with open(filepath, 'w') as json_file:
            json.dump(symbols_data, json_file)
        print(f'All indices symbols data successfully saved!')

        return symbols_data


def get_all_bond_symbols():
    link = 'https://symbol-search.tradingview.com/symbol_search/v3/?text=&hl=1&exchange=&lang=en&search_type=bond&domain=production'
    response = requests.get(link)
    count = response.json()['symbols_remaining'] + 50 if 'symbols_remaining' in list(response.json().keys()) else None
    if count is None:
        get_all_bond_symbols()

    if count >= 1:
        starts = [i for i in range(1, count, 50)]
        print(starts)
        ends = [i for i in range(50, count + 1, 50)]
        print(ends)
        symbols_data = []
        for start, end in zip(starts, ends):
            url = f'https://symbol-search.tradingview.com/symbol_search/v3/?text=&hl=1&exchange=&lang=en&search_type=bond&start={start}&end={end}&domain=production'
            print(url)
            response = requests.get(url)
            raw_data = response.json() if response.status_code == 200 else None
            data = raw_data['symbols'] if type(raw_data) == dict and 'symbols' in list(raw_data.keys()) else raw_data
            if response.status_code == 200:
                symbols_data.extend(data)
                print(data)
            else:
                print(response.text)
            time.sleep(0.2)

        sub = 'symbols'
        os.makedirs(sub, exist_ok=True)
        filepath = os.path.join(sub, f'all_bond_symbols.json')
        with open(filepath, 'w') as json_file:
            json.dump(symbols_data, json_file)
        print(f'All bond symbols data successfully saved!')

        return symbols_data


def get_all_funds_symbols():
    link = 'https://symbol-search.tradingview.com/symbol_search/v3/?text=&hl=1&exchange=&lang=en&search_type=funds&domain=production'
    response = requests.get(link)
    count = response.json()['symbols_remaining'] + 50 if 'symbols_remaining' in list(response.json().keys()) else None
    if count is None:
        get_all_funds_symbols()

    if count >= 1:
        starts = [i for i in range(1, count, 50)]
        print(starts)
        ends = [i for i in range(50, count + 1, 50)]
        print(ends)
        symbols_data = []
        for start, end in zip(starts, ends):
            url = f'https://symbol-search.tradingview.com/symbol_search/v3/?text=&hl=1&exchange=&lang=en&search_type=funds&start={start}&end={end}&domain=production'
            print(url)
            response = requests.get(url)
            raw_data = response.json() if response.status_code == 200 else None
            data = raw_data['symbols'] if type(raw_data) == dict and 'symbols' in list(raw_data.keys()) else raw_data
            if response.status_code == 200:
                symbols_data.extend(data)
                print(data)
            else:
                print(response.text)
            time.sleep(0.2)

        sub = 'symbols'
        os.makedirs(sub, exist_ok=True)
        filepath = os.path.join(sub, f'all_funds_symbols.json')
        with open(filepath, 'w') as json_file:
            json.dump(symbols_data, json_file)
        print(f'All funds symbols data successfully saved!')

        return symbols_data


def get_all_crypto_symbols():
    link = 'https://symbol-search.tradingview.com/symbol_search/v3/?text=&hl=1&exchange=&lang=en&search_type=crypto&domain=production'
    response = requests.get(link)
    count = response.json()['symbols_remaining'] + 50 if 'symbols_remaining' in list(response.json().keys()) else None
    if count is None:
        get_all_crypto_symbols()

    if count >= 1:
        starts = [i for i in range(1, count, 50)]
        print(starts)
        ends = [i for i in range(50, count + 1, 50)]
        print(ends)
        symbols_data = []
        for start, end in zip(starts, ends):
            url = f'https://symbol-search.tradingview.com/symbol_search/v3/?text=&hl=1&exchange=&lang=en&search_type=crypto&start={start}&end={end}&domain=production'
            print(url)
            response = requests.get(url)
            raw_data = response.json() if response.status_code == 200 else None
            data = raw_data['symbols'] if type(raw_data) == dict and 'symbols' in list(raw_data.keys()) else raw_data
            if response.status_code == 200:
                symbols_data.extend(data)
                print(data)
            else:
                print(response.text)
            time.sleep(0.2)

        sub = 'symbols'
        os.makedirs(sub, exist_ok=True)
        filepath = os.path.join(sub, f'all_crypto_symbols.json')
        with open(filepath, 'w') as json_file:
            json.dump(symbols_data, json_file)
        print(f'All crypto symbols data successfully saved!')

        return symbols_data


def get_all_forex_symbols():
    link = 'https://symbol-search.tradingview.com/symbol_search/v3/?text=&hl=1&exchange=&lang=en&search_type=forex&domain=production'
    response = requests.get(link)
    count = response.json()['symbols_remaining'] + 50 if 'symbols_remaining' in list(response.json().keys()) else None
    if count is None:
        get_all_forex_symbols()

    if count >= 1:
        starts = [i for i in range(1, count, 50)]
        print(starts)
        ends = [i for i in range(50, count + 1, 50)]
        print(ends)
        symbols_data = []
        for start, end in zip(starts, ends):
            url = f'https://symbol-search.tradingview.com/symbol_search/v3/?text=&hl=1&exchange=&lang=en&search_type=forex&start={start}&end={end}&domain=production'
            print(url)
            response = requests.get(url)
            raw_data = response.json() if response.status_code == 200 else None
            data = raw_data['symbols'] if type(raw_data) == dict and 'symbols' in list(raw_data.keys()) else raw_data
            if response.status_code == 200:
                symbols_data.extend(data)
                print(data)
            else:
                print(response.text)
            time.sleep(0.2)

        sub = 'symbols'
        os.makedirs(sub, exist_ok=True)
        filepath = os.path.join(sub, f'all_forex_symbols.json')
        with open(filepath, 'w') as json_file:
            json.dump(symbols_data, json_file)
        print(f'All forex symbols data successfully saved!')

        return symbols_data


def get_all_economic_indicators():
    link = 'https://symbol-search.tradingview.com/symbol_search/v3/?text=&hl=1&exchange=&lang=en&search_type=economic&domain=production&sort_by_country=US'
    response = requests.get(link)
    count = response.json()['symbols_remaining'] + 50 if 'symbols_remaining' in list(response.json().keys()) else None
    if count is None:
        get_all_economic_indicators()

    if count >= 1:
        starts = [i for i in range(1, count, 50)]
        print(starts)
        ends = [i for i in range(50, count + 1, 50)]
        print(ends)
        symbols_data = []
        for start, end in zip(starts, ends):
            url = f'https://symbol-search.tradingview.com/symbol_search/v3/?text=&hl=1&exchange=&lang=en&search_type=economic&start={start}&end={end}&domain=production'
            print(url)
            response = requests.get(url)
            raw_data = response.json() if response.status_code == 200 else None
            data = raw_data['symbols'] if type(raw_data) == dict and 'symbols' in list(raw_data.keys()) else raw_data
            if response.status_code == 200:
                symbols_data.extend(data)
                print(data)
            else:
                print(response.text)
            time.sleep(0.2)

        sub = 'symbols'
        os.makedirs(sub, exist_ok=True)
        filepath = os.path.join(sub, f'all_economic_indicators.json')
        with open(filepath, 'w') as json_file:
            json.dump(symbols_data, json_file)
        print(f'All economic indicators data successfully saved!')

        return symbols_data



def download_candles_data_job(tv, symbol, exchange, interval_dict, interval, bars_count, path):
    try:
        df = tv.get_hist(symbol=symbol, exchange=exchange, interval=interval_dict[interval], n_bars=bars_count)
        filepath = os.path.join(path, f'{exchange}-{symbol}_{interval}.csv')
        df.to_csv(filepath, index=True)
        result_text = f'Successfully fetched {interval} candles data of {symbol} from {exchange}!'
        time.sleep(0.2)
    except:
        if '_DL' in exchange:
            result_text = f'Failed in fetching {interval} candles data of {symbol} from {exchange}! Job aborted!'
        else:
            result_text = f'Failed in fetching {interval} candles data of {symbol} from {exchange}! Now adding suffix _DL and try again'
            exchange = exchange + '_DL'
            download_candles_data_job(tv, symbol, exchange, interval_dict, interval, bars_count, path)

    return result_text


def load_stock_symbols_from_file(filepath):
    with open(filepath, 'r') as file:
        data = json.load(file)
    symbols = [[item['symbol'], item['exchange'] if 'EURONEXT' not in item['exchange'] else 'EURONEXT', item['currency_code']] for item in data if item['type'] == 'stock']
    ss = list(set([item[0] for item in symbols]))
    return symbols


def get_candles_data_of_all_stocks(username, password, auth_path, interval, bars_count, core_num, selected_countries=[]):
    sub1 = 'symbols'
    raw_files = os.listdir(sub1)
    # filenames = [f for f in raw_files if 'all_' not in f]
    filenames = [f for f in raw_files if f[:2] in selected_countries] if selected_countries != [] else [f for f in raw_files]
    interval_dict = {
        '1m': Interval.in_1_minute,
        '3m': Interval.in_3_minute,
        '5m': Interval.in_5_minute,
        '15m': Interval.in_15_minute,
        '30m': Interval.in_30_minute,
        '45m': Interval.in_45_minute,
        '1h': Interval.in_1_hour,
        '2h': Interval.in_2_hour,
        '3h': Interval.in_3_hour,
        '4h': Interval.in_4_hour,
        '1D': Interval.in_daily,
        'W': Interval.in_weekly,
        'M': Interval.in_monthly
    }
    tv = TvDatafeed(username, password, auth_path)

    def callback(result):
        print(result)

    for name in filenames:
        ps = f'{name[:2]}/{interval}'
        country_path = os.path.join('data/stocks', ps)
        os.makedirs(country_path, exist_ok=True)

        filepath = os.path.join(sub1, name)
        symbols = load_stock_symbols_from_file(filepath)
        # for item in symbols:
        #     item[1] = item[1] + '_DLY'

        print(f'There are {len(symbols)} stocks in total for country {name}.')
        symbols = [s for s in symbols if s[0] not in [f[:-7] for f in os.listdir(country_path)]]

        pool = multiprocessing.Pool(processes=core_num)
        jobs = []

        for symbol, exchange, currency in symbols:
            job = pool.apply_async(download_candles_data_job, args=(tv, symbol, exchange, interval_dict, interval, bars_count, country_path), callback=callback)
            jobs.append(job)

        for job in jobs:
            job.get()



def get_list_of_futures_exchanges():
    read_path = 'symbols/all_futures_symbols.json'
    with open(read_path, 'r') as file:
        data = json.load(file)
    exchanges = sorted(list(set([item['exchange'] for item in data if 'exchange' in list(item.keys())])))
    filepath = 'exchanges_list.csv'
    with open(filepath, 'w', newline='') as file:
        for e in exchanges:
            file.write(e + '\n')
        file.close()

    print(exchanges)
    return exchanges


def get_all_futures_prefix(read_path='symbols/all_futures_symbols.json'):
    with open(read_path, 'r') as file:
        data = json.load(file)
    contracts = [[item['symbol'], item['exchange'], item['contracts']] for item in data if
                 'contracts' in list(item.keys())]
    prefixes = []

    for s, e, sl in contracts:
        for item in sl:
            if 'prefix' in list(item.keys()):
                c = item['symbol']
                p = item['prefix']
                symbol = [c, p]
                prefixes.append(symbol)

    filepath = 'futures_prefix.csv'
    with open(filepath, 'w', newline='') as file:
        for c, p in prefixes:
            file.write(c + ',' + p + '\n')
        file.close()

    return prefixes


def load_futures_symbols_from_file(filepath, selected_exchange=''):
    with open(filepath, 'r') as file:
        data = json.load(file)
    if selected_exchange == '':
        contracts = [[item['symbol'], item['exchange'], item['contracts']] for item in data if
                     'contracts' in list(item.keys())]
        no_contracts = [[item['symbol'], item['exchange']] for item in data if 'contracts' not in list(item.keys())]
        no_countries = [[item['symbol'], item['exchange']] for item in data if 'country' not in list(item.keys())]
    else:
        contracts = [[item['symbol'], item['exchange'], item['contracts']] for item in data if
                     'contracts' in list(item.keys()) and item['exchange'] == selected_exchange]
        no_contracts = [[item['symbol'], item['exchange']] for item in data if
                        'contracts' not in list(item.keys()) and item['exchange'] == selected_exchange]
        no_countries = [[item['symbol'], item['exchange']] for item in data if
                        'country' not in list(item.keys()) and item['exchange'] == selected_exchange]

    symbols = []
    for s, e, sl in contracts:
        for item in sl:
            # c = item['prefix'] + '_' + item['symbol'] if 'prefix' in list(item.keys()) else item['symbol']
            c = item['symbol']
            e = item['prefix'] + '_DL' if 'prefix' in list(item.keys()) else e
            symbol = [c, e]
            symbols.append(symbol)

    symbols.extend(no_contracts)
    symbols.extend(no_countries)
    exchange_tag = selected_exchange if selected_exchange != '' else 'all-exchanges'
    print(f'There are {len(symbols)} symbols from {exchange_tag} in total.')

    write_path = f'symbols/{exchange_tag}_symbols.csv'
    with open(write_path, 'w', newline='') as file:
        for c, e in symbols:
            file.write(c + ',' + e + '\n')
        file.close()

    return symbols


def get_candles_data_of_all_futures(username, password, auth_path, interval, bars_count, core_num, selected_exchanges=[]):
    sub = 'symbols'
    filepath = 'symbols/all_futures_symbols.json'

    interval_dict = {
        '1m': Interval.in_1_minute,
        '3m': Interval.in_3_minute,
        '5m': Interval.in_5_minute,
        '15m': Interval.in_15_minute,
        '30m': Interval.in_30_minute,
        '45m': Interval.in_45_minute,
        '1h': Interval.in_1_hour,
        '2h': Interval.in_2_hour,
        '3h': Interval.in_3_hour,
        '4h': Interval.in_4_hour,
        '1D': Interval.in_daily,
        'W': Interval.in_weekly,
        'M': Interval.in_monthly
    }
    tv = TvDatafeed(username, password, auth_path)

    def callback(result):
        print(result)

    data = load_futures_symbols_from_file(filepath)
    all_exchanges = sorted(list(set([s[1] for s in data])))
    exchanges = selected_exchanges if selected_exchanges != [] else all_exchanges

    for e in exchanges:
        exchange_path = os.path.join('data', e)
        os.makedirs(exchange_path, exist_ok=True)
        tf_path = os.path.join(exchange_path, interval)
        os.makedirs(tf_path, exist_ok=True)

        files = os.listdir(tf_path)
        # existing_data = [f[len(e)+1:-(5+len(interval))] for f in files]
        symbols = [s for s in data if (s[1] == e or s[1].startswith(e)) and not any(
            f.__contains__(s[0]) for f in files)]  # s[0] not in existing_data

        pool = multiprocessing.Pool(processes=core_num)
        jobs = []

        for symbol, exchange in symbols:
            job = pool.apply_async(download_candles_data_job,args=(tv, symbol, exchange, interval_dict, interval, bars_count, tf_path),callback=callback)
            jobs.append(job)

        for job in jobs:
            job.get()



def get_candles_data_of_all_indices(username, password, auth_path, interval, bars_count, core_num, selected_exchanges=[]):
    sub = 'symbols'
    filepath = 'symbols/all_indices_symbols.json'

    interval_dict = {
        '1m': Interval.in_1_minute,
        '3m': Interval.in_3_minute,
        '5m': Interval.in_5_minute,
        '15m': Interval.in_15_minute,
        '30m': Interval.in_30_minute,
        '45m': Interval.in_45_minute,
        '1h': Interval.in_1_hour,
        '2h': Interval.in_2_hour,
        '3h': Interval.in_3_hour,
        '4h': Interval.in_4_hour,
        '1D': Interval.in_daily,
        'W': Interval.in_weekly,
        'M': Interval.in_monthly
    }
    tv = TvDatafeed(username, password, auth_path)

    def callback(result):
        print(result)

    with open(filepath, 'r') as file:
        raw_data = json.load(file)
    data = [[item['symbol'], item['exchange'] if 'EURONEXT' not in item['exchange'] else 'EURONEXT'] for item in raw_data if item['type'] == 'index']
    ss = list(set([item[0] for item in data]))

    all_exchanges = sorted(list(set([s[1] for s in data])))
    exchanges = selected_exchanges if selected_exchanges != [] else all_exchanges
    print(exchanges)

    pool = multiprocessing.Pool(processes=core_num)
    jobs = []

    for e in exchanges[::]:
        exchange_path = os.path.join('data/indices', e)
        os.makedirs(exchange_path, exist_ok=True)
        tf_path = os.path.join(exchange_path, interval)
        os.makedirs(tf_path, exist_ok=True)

        files = os.listdir(tf_path)
        symbols = [s for s in data if (s[1] == e or s[1].startswith(e)) and not any(f.__contains__(s[0]) for f in files)]
        print(symbols)

        for symbol, exchange in symbols:
            job = pool.apply_async(download_candles_data_job, args=(tv, symbol, exchange, interval_dict, interval, bars_count, tf_path), callback=callback)
            jobs.append(job)

    for job in jobs:
        job.get()




if __name__ == '__main__':

    # def get_gainers_auto_run():
    #     min_cap = 100000
    #     min_chg_pct = 10
    #     today = datetime.today().strftime('%Y%m%d')
    #
    #     start_time = datetime.now().replace(hour=3, minute=15, second=0, microsecond=0)
    #     days_to_run = 365
    #     interval = 60
    #     end_time = start_time + timedelta(days=days_to_run)
    #
    #     scheduled_time = start_time
    #     while scheduled_time <= end_time:
    #         time.sleep(0.01)
    #         if datetime.now() >= scheduled_time:
    #             get_crypto_top_24h_gainers(min_cap, min_chg_pct, scheduled_time)
    #             scheduled_time += timedelta(minutes=interval)

    country_list = ['US', 'HK', 'JP', 'KR', 'GB', 'CN']   # Define your own list of countries here
    for country in country_list:
        country_symbols = get_symbols_list_by_country(country)

    futures = get_all_futures_symbols()
    indices = get_all_indices_symbols()
    bonds = get_all_bond_symbols()
    funds = get_all_funds_symbols()
    cryptos = get_all_crypto_symbols()
    forex = get_all_forex_symbols()
    economic = get_all_economic_indicators()

    username = 'XXX@gmail.com'
    password = 'PASSWORD'
    auth_path = r'C:\Users\user\Documents\#Coding\Tradingview\tokendata.txt'  # Place your token data to a directory and specify the path here

    countries = ['HK', 'US', 'JP'] # Define your own list of countries here
    get_candles_data_of_all_stocks(username, password, auth_path, '1D', 20000, 4, selected_countries=countries)

    selected_exchanges = get_list_of_futures_exchanges()
    get_candles_data_of_all_futures(username, password, auth_path, '1h', 20000, 2, selected_exchanges=['HKEX'])

    get_candles_data_of_all_indices(username, password, auth_path, '1D', 20000, 4)



