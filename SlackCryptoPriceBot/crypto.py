#!/usr/bin/env python
# encoding: utf-8

import datetime
import requests
import logging


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
        return float(self._data.get('percent_change_1h'))

    @property
    def one_day(self):
        return float(self._data.get('percent_change_24h'))

    @property
    def one_week(self):
        return float(self._data.get('percent_change_7d'))

    def __str__(self):
        return f'{self.symbol} ${self.usd}'


class CryptoWorld(object):
    def __init__(self):
        self._global = {}
        self._by_symbol = {}
        self._by_id = {}
        self._last_global_update = None
        self._last_ticker_update = None

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

    def update_global(self):
        # Get the global market data
        # XXX(need to check age of cached object and return cache or refresh if needed.)
        logger.info("Fetching global info...")
        resp = requests.get(GLOBAL_URL)
        logger.info("Fetched global info %s", resp)

        if resp.status_code != requests.codes.ok:
            resp.raise_for_status()

        self._global = resp.json()
        self._last_global_update = datetime.datetime.utcnow()

        return self

    def update_ticker(self):
        # Get all price data for all currencies
        # XXX(need to check age of cached objects and return cache or refresh if needed.)
        logger.info("Fetching ticker info...")
        resp = requests.get(f'{TICKER_URL}limit=0')
        logger.info("Fetched ticker info %s", resp)

        if resp.status_code != requests.codes.ok:
            resp.raise_for_status()

        for bcd in resp.json():
            bc = Blockchain()
            self._by_id[bcd['id']] = bc.id
            self._by_symbol[bcd['symbol']] = bc.symbol

        self._last_ticker_update = datetime.datetime.utcnow()

        return

    def ticker_get(self, bc_id):
        if not bc_id:
            raise ValueError('Invalid block chain id argument')

        # Return from cache
        # XXX(need to check age of cached object and refresh if needed.)
        return self._by_id.get(bc_id)

        resp = requests.get(f'{TICKER_URL}{bc_id}/')

        if resp.status_code != requests.codes.ok:
            resp.raise_for_status()

        return Blockchain(resp.json())

    def update(self):
        self.update_global()
        self.update_ticker()

    def __str__(self):
        return '\n'.join(f'{bc}' for bc in self._by_id.values())


def main():
    cw = CryptoWorld()
    cw.update()
    print(f'CryptoWorld:\n{cw}')


if __name__ == '__main__':
    main()
