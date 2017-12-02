#!/usr/bin/env python
# encoding: utf-8

#  from pprint import pformat
import datetime
import logging
import json


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

    @property
    def slack_str(self):
        return (
            f'*{self.symbol}* \t*${self.usd}* :dollar:\n'
            f'\t1h: {self.one_hour}%,\t24h: {self.one_day}%,\t7d: {self.one_week}%'
        )

    def __str__(self):
        od = self.one_day
        od = f'{od}' if od < 0 else f' {od}'
        return f'{self.symbol}\t${self.usd}  {od}  ${self.market_cap}'

    def __repr__(self):
        return f'<BlockChain {self.symbol} : ${self.usd}>'


class CryptoWorld(object):
    REDIS_KEY_GLOBAL = 'coin_global'
    REDIS_KEY_TICKER = 'coin_ticker'

    def __init__(self, redis_db, client, data_expire=600):
        logger.debug("CryptoWorld __init__ redis: %s, client: %s", redis_db, client)
        self._redis_db = redis_db
        self._client = client
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

    async def _get_cached(self, key, url, params={}):
        logger.debug("_get_cached %s, %s, %s", key, url, params)
        data = await self._redis_db.exec('get', key)

        if data:
            logger.debug("_get_cached HIT")
            return json.loads(data)

        logger.debug("_get_cached MISS")
        resp = await self._client.get(url, params=params)

        if resp.status != 200:
            resp.raise_for_status()

        data = await resp.text()

        await self._redis_db.exec('setex', key, self._data_expire, data)

        logger.debug("_get_cached UPDATED")
        data = json.loads(data)

        from pprint import pformat
        logger.debug("_get_cached NEW DATA\n%s : %s", key, pformat(data))

        return data

    async def update_global(self):
        # Get the global market data
        logger.debug("Fetching global info...")

        g_data = await self._get_cached(self.REDIS_KEY_GLOBAL, GLOBAL_URL)
        self._global = g_data

        return self

    async def update_ticker(self):
        # Get all price data for all currencies
        logger.debug("Fetching ticker info...")

        t_data = await self._get_cached(
            self.REDIS_KEY_TICKER, f'{TICKER_URL}', params={'limit': 0})

        for bcd in t_data:
            bc = Blockchain(bcd)
            self._by_id[bcd['id']] = bc
            self._by_symbol[bcd['symbol'].lower()] = bc

        return self

    async def ticker_get(self, bc_id):
        if not bc_id:
            raise ValueError('Invalid block chain id argument')

        await self.update_ticker()
        return self._by_id.get(bc_id.lower())

    async def update(self):
        logger.debug("CryptoWorld update...")
        await self.update_global()
        await self.update_ticker()

    async def fuzzy_match(self, tokens):
        logger.debug("fuzzy_match %s", tokens)
        await self.update()

        symbols = set(tokens) & set(self._by_symbol.keys())
        ids = (set(tokens) & set(self._by_id.keys())) - symbols
        logger.debug("fuzzy_matched symbols/ids %s %s", symbols, ids)

        res = []
        if symbols:
            for s in symbols:
                res.append(self._by_symbol[s])

        if ids:
            for id in ids:
                res.append(self._by_id[id])

        logger.debug("fuzzy_matched %s", res)
        return res

    def __str__(self):
        return (
            f'Total Market Cap\t{self.total_cap}\n'
            f'Total 24 Hour Volume\t{self.total_daily_volume}\n'
            f'Active Currencies\t{self.active_currencies}\n'
            f'Active Markets\t\t{self.active_markets}\n'
        ) + '\n'.join(f'{bc}' for bc in self._by_id.values())
