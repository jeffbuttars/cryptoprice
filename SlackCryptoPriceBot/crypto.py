#!/usr/bin/env python
# encoding: utf-8

import os
import datetime
import requests
import logging
import json
import redis


logger = logging.getLogger(__name__)
BASE_URL = 'https://api.coinmarketcap.com/v1/'
GLOBAL_URL = f'{BASE_URL}global/'
TICKER_URL = f'{BASE_URL}ticker/'


class Blockchain(object):
    """Info instance for a particular blockchain from coinmarketcap
    ex: {
        "id": "bitcoin",
        "name": "Bitcoin",
        "symbol": "BTC",
        "rank": "1",
        "price_usd": "573.137",
        "price_btc": "1.0",
        "24h_volume_usd": "72855700.0",
        "market_cap_usd": "9080883500.0",
        "available_supply": "15844176.0",
        "total_supply": "15844176.0",
        "percent_change_1h": "0.04",
        "percent_change_24h": "-0.3",
        "percent_change_7d": "-0.57",
        "last_updated": "1472762067"
    },
    """
    def __init__(self, data={}):
        self._ts = datetime.datetime.utcnow()
        self._data = data

    def __getitem__(self, key):
        return self._data.get(key)

    def __getattr__(self, key):
        return self._data.get(key)

    @property
    def market_cap(self):
        return float(self._data.get('market_cap_usd') or 0)

    @property
    def last_updated(self):
        return datetime.utcfromtimestamp(int(self._data.get('last_updated', 0)))

    @property
    def usd(self):
        return '%2.2f' % float(self._data.get('price_usd', 0))

    @property
    def symbol(self):
        return self._data.get('symbol', '').upper()

    @property
    def id(self):
        return self._data.get('id', '').lower()

    @property
    def one_hour(self):
        return float(self._data.get('percent_change_1h') or 0)

    @property
    def one_day(self):
        return float(self._data.get('percent_change_24h') or 0)

    @property
    def one_week(self):
        return float(self._data.get('percent_change_7d') or 0)

    def __str__(self):
        od = self.one_day
        od = f'{od}' if od < 0 else f' {od}'
        return f'{self.symbol}\t${self.usd}  {od}  ${self.market_cap}'


class CryptoWorld(object):
    REDIS_KEY_GLOBAL = 'coin_global'
    REDIS_KEY_TICKER = 'coin_ticker'

    def __init__(self, redis_db, data_expire=600):
        self._redis_db = redis_db
        self._data_expire = data_expire
        self._global = {}
        self._by_symbol = {}
        self._by_id = {}

    @property
    def total_cap(self):
        return int(self._global.get('total_market_cap_usd', 0))

    @property
    def total_daily_volume(self):
        return int(self._global.get('total_24h_volume_usd', 0))

    @property
    def active_currencies(self):
        return int(self._global.get('active_currencies', 0))

    @property
    def active_assets(self):
        return int(self._global.get('active_assets', 0))

    @property
    def active_markets(self):
        return int(self._global.get('active_markets', 0))

    @property
    def last_updated(self):
        return datetime.utcfromtimestamp(int(self._global.get('last_updated', 0)))

    def _get_cached(self, key, url, params={}):
        logger.debug("_get_cached %s, %s, %s", key, url, params)
        data = self._redis_db.get(key)

        if data:
            logger.debug("_get_cached HIT")
            return json.loads(data)

        logger.debug("_get_cached MISS")
        resp = requests.get(url, params=params)

        if resp.status_code != requests.codes.ok:
            resp.raise_for_status()

        self._redis_db.setex(key, resp.content, self._data_expire)
        logger.debug("_get_cached UPDATED")

        return resp.json()

    def update_global(self):
        # Get the global market data
        logger.info("Fetching global info...")

        g_data = self._get_cached(self.REDIS_KEY_GLOBAL, GLOBAL_URL)

        self._global = g_data
        logger.info("Fetched global info %s", self._global)

        return self

    def update_ticker(self):
        # Get all price data for all currencies
        logger.info("Fetching ticker info...")

        t_data = self._get_cached(self.REDIS_KEY_TICKER, f'{TICKER_URL}', params={'limit': 0})

        for bcd in t_data:
            print('BCD:', bcd)
            bc = Blockchain(bcd)
            self._by_id[bcd['id']] = bc
            self._by_symbol[bcd['symbol']] = bc

        return self

    def ticker_get(self, bc_id):
        if not bc_id:
            raise ValueError('Invalid block chain id argument')

        self.update_ticker()
        return self._by_id.get(bc_id)

    def update(self):
        self.update_global()
        self.update_ticker()

    def __str__(self):
        #  logger.info("STR: %s", self._by_id.values())
        return (
            f'Total Market Cap\t{self.total_cap}\n'
            f'Total 24 Hour Volume\t{self.total_daily_volume}\n'
            f'Active Currencies\t{self.active_currencies}\n'
            f'Active Markets\t\t{self.active_markets}\n'
        ) + '\n'.join(f'{bc}' for bc in self._by_id.values())


def main():
    # Set up the logger
    logger = logging.getLogger(__name__)
    # Use a console handler, set it to debug by default
    logger_ch = logging.StreamHandler()
    logger.setLevel(logging.DEBUG)
    log_formatter = logging.Formatter(('%(levelname)s: %(asctime)s %(processName)s:%(process)d'
                                       ' %(filename)s:%(lineno)s %(module)s::%(funcName)s()'
                                       ' -- %(message)s'))
    logger_ch.setFormatter(log_formatter)
    logger.addHandler(logger_ch)

    redis_db = redis.Redis.from_url(os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/0'))

    cw = CryptoWorld(redis_db)
    cw.update()
    print(f'CryptoWorld:\n{cw}')


if __name__ == '__main__':
    main()
