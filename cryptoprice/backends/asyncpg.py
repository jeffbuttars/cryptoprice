import os
import subprocess
import typing
from aiocontext import async_contextmanager as contextmanager
import asyncpg
from asyncpg import Connection
from apistar import Command, Component, Settings
import logging

logger = logging.getLogger(__name__)


class AsyncPgBackend(object):
    """AsyncPg Backend"""
    CLI_CONFIG_MAP = {
        'HOST': '--host',
        'PORT': '--port',
        'USER': '--username',
        'NAME': '--dbname',
        'DATABASE': '--dbname',
    }

    def __init__(self, settings: Settings) -> None:
        #  self._conn = await asyncpg.connect()
        self._config = settings.get('DATABASE')
        self._url = self._config.get('URL')
        self._pool = None

    async def pool(self):
        if self._pool:
            return self._pool

        if self._url:
            logger.debug("Creating Postgresql connection from URL")
            self._pool = await asyncpg.create_pool(self._url)
        else:
            logger.debug("Creating Postgresql connection from credentials")
            kwargs = {}
            if 'DATBASE' not in self._config:
                kwargs['database'] = self._config.pop('NAME', '')

            for k in ('HOST', 'DATABASE', 'USER', 'PORT', 'PASSWORD', 'TIMEOUT', 'SSL'):
                if k in self._config:
                    kwargs[k.lower()] = self._config[k]

            self._pool = await asyncpg.create_pool(**kwargs)

        return self._pool

    async def conn(self):
        pool = await self.pool()
        return await pool.acquire()

    @property
    def url(self):
        return self._url

    @property
    def config(self):
        return self._config.copy()


@contextmanager
async def get_conn(backend: AsyncPgBackend) -> typing.Generator[Connection, None, None]:
    """
    Get a database connection in a context that will release itself when the context is left.
    """
    pool = await backend.pool()
    conn = await pool.acquire()

    try:
        yield conn
    except Exception:
        raise
    finally:
        pool.release(conn)


def pg_cli(backend: AsyncPgBackend):
    """
    Run the Postgresql shell with this projects DB settings
    """
    psql = ['psql']
    env = os.environ.copy()

    if backend.url:
        # Prefer the url
        psql.append(backend.url)
    else:
        # Build a command line from the config.
        # Put the password in the environment with PGPASS
        config = backend.config
        env['DBPASSWORD'] = config.get('PASSWORD', '')

        keys = set(config.keys()) & set(backend.CLI_CONFIG_MAP.keys())
        for k in keys:
            psql.append(backend.CLI_CONFIG_MAP[k])
            psql.append(config[k])

    subprocess.call(psql, env=env)


components = [
    Component(AsyncPgBackend, init=AsyncPgBackend),
    Component(Connection, init=get_conn, preload=False),
]


commands = [
    Command('dbshell', pg_cli),
]
